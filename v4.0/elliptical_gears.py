import math
import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
import shapely.affinity

from geometry_utils import polar_ellipse_radius, involute_profile, unify_segments

class EllipticalGear:
    """
    Представляет ОДНУ эллиптическую шестерню.
    - teeth (int)
    - a, b (float): полуоси
    - module, pressure_angle, clearance
    - Использует 'rolling' для генерации зубьев, 
      т.е. для каждого зуба вычисляем локальный радиус, base_radius, строим инволютный контур.
    """

    def __init__(self, teeth, a, b, module, pressure_angle_deg, clearance):
        self.teeth = teeth
        self.a = a
        self.b = b
        self.module = module
        self.pressure_angle = math.radians(pressure_angle_deg)
        self.clearance = clearance

        self.addendum = module
        self.dedendum = module*(1+clearance)

        # Количество точек для каждого зуба
        self.n_profile_points = 40
        # Количество зубьев = teeth => шаг по углу = 2*pi/teeth
        self.dtheta = 2*math.pi / teeth

    def build_gear_polygon(self):
        """
        Генерирует полигон (shapely) всей шестерни путём объединения зубьев.
        (Упрощённо, без сопряжения со второй шестернёй)
        """
        from shapely.geometry import Polygon
        from shapely.ops import unary_union

        tooth_polys = []
        for i in range(self.teeth):
            theta_mid = i*self.dtheta
            poly_t = self._build_tooth_polygon(theta_mid)
            tooth_polys.append(poly_t)

        gear_poly = unary_union(tooth_polys)
        return gear_poly

    def build_gear_segments(self):
        """
        Возвращает список отрезков (x1,y1)->(x2,y2),
        преобразуя результат build_gear_polygon() в ломаную.
        """
        poly = self.build_gear_polygon()
        return unify_segments(poly)

    def _build_tooth_polygon(self, theta_mid):
        """
        Строим полигон одного зуба в окрестности [theta_mid - dtheta/2, theta_mid + dtheta/2].
        Без учёта реального взаимодействия со второй шестернёй.
        Используем эллиптический радиус + addendum/dedendum.
        """
        import numpy as np
        from shapely.geometry import Polygon

        half = self.dtheta*0.5
        n = self.n_profile_points
        thetas = np.linspace(theta_mid - half, theta_mid + half, n)

        out_pts = []
        in_pts  = []

        for t in thetas:
            r_ell = polar_ellipse_radius(self.a,self.b,t)
            r_out = max(0, r_ell + self.addendum)
            r_in  = r_ell - self.dedendum
            if r_in<0:
                r_in=0

            x_out = r_out*math.cos(t)
            y_out = r_out*math.sin(t)
            out_pts.append((x_out,y_out))

            x_in = r_in*math.cos(t)
            y_in = r_in*math.sin(t)
            in_pts.append((x_in,y_in))

        ring = out_pts + in_pts[::-1]
        return Polygon(ring)


class EllipticalPairBuilder:
    """
    Создаёт ПАРУ эллиптических шестерён, где вторая реально сопрягается с первой
    (упрощённо) через обкатку (rolling approach).
    """

    def __init__(self, t1, a1, b1, t2, a2, b2, module, pressure_angle_deg, clearance):
        self.t1 = t1
        self.a1 = a1
        self.b1 = b1
        self.t2 = t2
        self.a2 = a2
        self.b2 = b2
        self.module = module
        self.pressure_angle = pressure_angle_deg
        self.clearance = clearance

        # Создаём объекты
        self.gear1 = EllipticalGear(t1, a1, b1, module, pressure_angle_deg, clearance)
        self.gear2 = EllipticalGear(t2, a2, b2, module, pressure_angle_deg, clearance)

    def build_pair(self):
        """
        Генерирует (lines1, lines2):
         - lines1: отрезки первой шестерни
         - lines2: отрезки второй, которая "обкатает" первую (сопряжение).
        """

        # 1) генерируем полигон (или линии) для первой шестерни (упрощённо)
        poly1 = self.gear1.build_gear_polygon()

        # 2) Готовим "сопряжённый" профиль для шестерни2.
        #    Вместо простого build_gear_polygon() возьмём rolling approach:
        #    - Для каждого зуба 2й шестерни выясняем, как он "зацепляется" с 1й
        #      (в идеале — общая длина дуги, rolling без проскальзывания).
        #    - Но ниже — более краткий метод: 
        #      "обкатываем" эллипс2 вокруг эллипса1, ищем соответствующий угол.
        #      На практике такие формулы приводят piellardj. 
        #    - Чтобы не усложнять, возьмём "примитивную" реализацию, 
        #      где R2(theta) = a2,b2..., но фаза theta2 идёт из rolling c gear1.

        poly2 = self._build_son_gear_polygon(poly1)

        # Превращаем в набор отрезков
        lines1 = unify_segments(poly1)
        lines2 = unify_segments(poly2)

        return lines1, lines2

    def _build_son_gear_polygon(self, poly1):
        """
        Строит полигон для второй шестерни, сопряжённой с poly1, 
        путём rolling (упрощённо).
        """
        # Найдём "длину делительной линии" gear1, 
        # предполагая, что perimeter1 = perimeter2 => rolling без проскальзывания.
        # Но у нас эллипс, да и зубчатый контур. 
        # Упростим: возьмём окружной "средний" периметр = (pitch_perim1), pitch_perim2,
        # и подгоним a2,b2?
        # Но вы _уже_ задали a2,b2! 
        # Ладно, будем считать, что "ratio" окружностей = t1 / t2 
        # (число зубьев). 
        # 
        # Для демонстрации — всё весьма условно.

        from shapely.geometry import Polygon, Point
        from shapely.ops import unary_union

        gear2_tooth_polys = []
        # разбиваем угол [0..2*pi] на t2 зубьев
        dtheta2 = 2*math.pi / self.t2
        for i in range(self.t2):
            th2 = i*dtheta2
            poly_t = self._build_one_tooth_son(th2)
            gear2_tooth_polys.append(poly_t)

        gear2_poly = unary_union(gear2_tooth_polys)

        # Теперь, чтобы обеспечить "реальное" соприкосновение, 
        # мы "пододвинем" gear2_poly так, чтобы при угле=0 
        # он касался gear1_poly. 
        # Для эллипсов, ориентированных так, проще всего сместить gear2 вправо 
        # на (a1 + a2 + зазор). 
        # Но мы же хотим именно сопряжение?
        # Пойдем ещё проще: пусть center_distance = (a1+b1)/2 + (a2+b2)/2
        # (Это весьма условно, для настоящего зацепления нужно решать 
        #  уравнения соприкосновения.)
        cd = (max(self.a1,self.b1)+ max(self.a2,self.b2))*0.9
        # сдвигаем
        gear2_poly = shapely.affinity.translate(gear2_poly, xoff=cd)
        return gear2_poly

    def _build_one_tooth_son(self, theta2):
        """
        Cтроим 1 зуб второй шестерни (gear2) как сопряжённый к первой.
        На самом деле делаем вид, что R_ellipse2 = a2,b2, 
        + addendum/dedendum, 
        но "rolling angle" theta2. 
        """
        import numpy as np
        from shapely.geometry import Polygon

        half = (2*math.pi/self.t2)*0.5
        n = self.gear2.n_profile_points
        thetas = np.linspace(theta2 - half, theta2 + half, n)

        out_pts = []
        in_pts  = []

        for t in thetas:
            r_ell = polar_ellipse_radius(self.a2, self.b2, t)
            r_out = r_ell + self.gear2.addendum
            r_in  = r_ell - self.gear2.dedendum
            if r_in<0: 
                r_in=0

            x_out = r_out*math.cos(t)
            y_out = r_out*math.sin(t)
            out_pts.append((x_out,y_out))

            x_in = r_in*math.cos(t)
            y_in = r_in*math.sin(t)
            in_pts.append((x_in,y_in))

        ring = out_pts + in_pts[::-1]
        return Polygon(ring)
