import math

def involute_point(base_radius, t):
    """Та же функция, что и в gear.py."""
    x = base_radius * (math.cos(t) + t * math.sin(t))
    y = base_radius * (math.sin(t) - t * math.cos(t))
    return x, y

class EllipticalGear:
    def __init__(self, teeth, module, pressure_angle=20, clearance=0.25,
                 a=40.0, b=25.0):
        """
        Примитивная реализация "эллиптической" шестерни.
        a,b - полуоси эллипса.
        """
        self.teeth = teeth
        self.module = module
        self.pressure_angle = math.radians(pressure_angle)
        self.clearance = clearance
        self.a = a
        self.b = b

        # Шаг по окружности (по аналогии с кругом) ~ module
        # Условно делаем "период" = 2*pi и делим на teeth. 
        # Но на самом деле шаг вдоль эллипса можем считать равным 2*pi/teeth.
        self.dtheta = 2*math.pi / teeth

        # Для "масштаба" возьмём некий эквивалентный "средний радиус" ~ (a+b)/2
        # и вычислим addendum, dedendum
        self.pitch_mean = (a + b)/2.0
        self.addendum = self.module
        self.dedendum = self.module * (1 + self.clearance)

        # Зададим количество точек для инволюты
        self.num_points_involute = 20
        
        # Для удобства вычислим "максимальный радиус" эллипса.
        # Наиболее длинный радиус эллипса = a, если a>b, (на оси X)
        # но вообще "дальний" радиус бывает под углом, точнее это max R(\theta).
        # Проще найти максимум по многим \theta.
        steps = 360
        rr = []
        for i in range(steps):
            th = 2*math.pi*i/steps
            rr.append(self._pitch_radius(th) + self.addendum)
        self.max_radius = max(rr)

    def _pitch_radius(self, theta):
        """
        Локальный делительный радиус эллипса в направлении угла theta.
        
        Формула: R = a*b / sqrt( (b cos theta)^2 + (a sin theta)^2 )
        """
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        denom = math.sqrt((self.b*cos_t)**2 + (self.a*sin_t)**2)
        return (self.a*self.b)/denom if denom!=0 else 0

    def _base_radius(self, theta):
        """
        Локальный базовый радиус = pitch_radius * cos(pressure_angle)
        Упрощенно.
        """
        return self._pitch_radius(theta) * math.cos(self.pressure_angle)

    def _root_radius(self, theta):
        """
        Локальный корневой радиус = pitch_radius - dedendum
        """
        return self._pitch_radius(theta) - self.dedendum

    def _outer_radius(self, theta):
        """
        Локальный внешний радиус = pitch_radius + addendum
        """
        return self._pitch_radius(theta) + self.addendum

    def _tooth_profile_at_theta(self, theta0):
        """
        Строит "кусочек" зуба, расположенного возле угла theta0.
        - Берём некий малый угол Delta = dtheta/2 (половина шага),
          чтобы зуб был "по центру" в theta0.
        - Считаем, что tooth-profile идёт от (theta0 - Delta) до (theta0 + Delta).
        - Для упрощения берём средний base_radius = _base_radius(theta0).
          Т.е. все точки инволюты считаем из одной "базы" — грубое упрощение!
        """
        # полушаг
        half_step = self.dtheta / 2.0

        # усреднённые радиусы
        base_r  = self._base_radius(theta0)
        root_r  = self._root_radius(theta0)
        outer_r = self._outer_radius(theta0)

        if root_r < 0:
            root_r = 0

        # Как и в gear.py, определяем инволюту:
        # start = max(root_r, base_r)
        start_r = max(root_r, base_r)
        def param_from_r(r):
            if r < base_r:
                return 0
            return math.sqrt((r/base_r)**2 - 1)
        t_start = param_from_r(start_r)
        t_end   = param_from_r(outer_r)

        # Соберём точки инволюты (не в глобальных координатах, а в локальной системе)
        # Считаем, что ось X - радиальная, Y - "вверх".
        # После этого повернём этот контур на theta0.
        invol = []
        t_count = self.num_points_involute
        for t in range(t_count):
            tv = t_start + (t_end - t_start)*t/(t_count-1 if t_count>1 else 1)
            x = base_r*(math.cos(tv) + tv*math.sin(tv))
            y = base_r*(math.sin(tv) - tv*math.cos(tv))
            invol.append((x,y))
        # Зеркальная ветвь:
        invol_mirr = [(-x,y) for x,y in invol[::-1]]

        # Дуга наружная (окружность radius=outer_r)
        # Углы концов дуги:
        def ang_of(p):
            return math.atan2(p[1], p[0])
        a1 = ang_of(invol[-1])
        a2 = ang_of(invol_mirr[0])
        if a2 < a1:
            a2 += 2*math.pi
        arc_top = []
        div_top = 8
        for i in range(div_top):
            a = a1 + (a2 - a1)*i/(div_top-1 if div_top>1 else 1)
            arc_top.append((outer_r*math.cos(a), outer_r*math.sin(a)))

        # Дуга корня, если root_r >= base_r (условно)
        root_arc = []
        if root_r >= base_r:
            left_pt = invol_mirr[-1]
            right_pt= invol[0]
            la = ang_of(left_pt)
            ra = ang_of(right_pt)
            if ra < la:
                ra += 2*math.pi
            div_root = 8
            for i in range(div_root):
                a = la + (ra - la)*i/(div_root-1 if div_root>1 else 1)
                rx = root_r*math.cos(a)
                ry = root_r*math.sin(a)
                root_arc.append((rx,ry))

        # Собираем контур
        contour = []
        contour += root_arc
        contour += invol
        contour += arc_top
        contour += invol_mirr

        # Теперь надо этот контур "раскрыть" вдоль реального направления.
        # Т.е. мы поворачиваем каждую точку на угол theta0 вокруг (0,0),
        # НО кроме поворота, у нас эллипс: фактическая "радиальная" линия
        # на угле (theta0 + локальный_угол) - в общем, это уже упрощение.
        # Мы сделаем так: у нас tooth "сидит" в интервале theta0 ± half_step.
        # Для каждой точки (x,y) в локальной системе повёрнутой на "u",
        # мы повернём их глобально на theta0. Упрощённо.
        # => Можно просто rotate_point(..., theta0).
        
        # Но чтобы хоть чуть-чуть учесть эллипс, 
        # можно сперва повернуть (x,y) на +someAngle, зависящий от (theta0 ± small),
        # но это усложнит код. Оставим примитив — всё зубья "радиально" стоят.
        
        # Повернём контур целиком на theta0:
        def rotate(pt, ang):
            xx, yy = pt
            ca = math.cos(ang)
            sa = math.sin(ang)
            return (xx*ca - yy*sa, xx*sa + yy*ca)
        
        global_contour = [rotate(p, theta0) for p in contour]
        return global_contour

    def generate_gear_geometry(self, offset=(0,0)):
        """
        Собираем все зубья: всего teeth штук, равномерно распределённые по 0..2*pi.
        Но так как шестерня некруглая, каждый зуб мы строим как _tooth_profile_at_theta(i*dtheta).
        """
        lines = []
        ox, oy = offset

        for i in range(self.teeth):
            theta0 = i*self.dtheta
            profile = self._tooth_profile_at_theta(theta0)
            # Превратим набор точек в набор отрезков
            # и сместим на (ox, oy)
            shifted = [(p[0]+ox, p[1]+oy) for p in profile]
            for j in range(len(shifted)-1):
                lines.append((shifted[j], shifted[j+1]))
            lines.append((shifted[-1], shifted[0]))

        return lines
