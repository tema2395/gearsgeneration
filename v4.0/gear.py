import math

def involute_point(base_radius, t):
    """Вычисляет координаты точки на инволюте окружности радиуса base_radius по параметру t."""
    x = base_radius * (math.cos(t) + t * math.sin(t))
    y = base_radius * (math.sin(t) - t * math.cos(t))
    return x, y

class Gear:
    def __init__(self, teeth, module, pressure_angle=20, clearance=0.25):
        """
        Инициализация параметров шестерни.
        
        :param teeth: Число зубьев
        :param module: Модуль
        :param pressure_angle: Угол давления в градусах
        :param clearance: Дополнительный зазор (коэффициент)
        """
        self.teeth = teeth
        self.module = module
        self.pressure_angle = pressure_angle
        self.clearance = clearance

        # Основные расчёты
        self.pitch_diameter = module * teeth                 # Делительный диаметр
        self.pitch_radius   = self.pitch_diameter / 2        # Делительный радиус
        self.base_diameter  = self.pitch_diameter * math.cos(math.radians(pressure_angle))
        self.base_radius    = self.base_diameter / 2         # Базовый радиус (для инволюты)
        self.addendum       = module                         # Высота головки зуба
        self.dedendum       = module * (1 + clearance)       # Высота ножки зуба (c зазором)
        self.outer_radius   = self.pitch_radius + self.addendum  # Наружный радиус (ad + pitch)
        self.root_radius    = self.pitch_radius - self.dedendum   # Радиус впадины (pitch - dedendum)

        # Количество точек для аппроксимации инволюты
        self.num_involute_points = 30

    def linspace(self, start, stop, num):
        """Генерирует равномерно распределённые точки от start до stop включительно."""
        if num <= 1:
            return [start]
        step = (stop - start) / (num - 1)
        return [start + i * step for i in range(num)]

    def rotate_point(self, point, angle):
        """
        Поворот точки (x, y) на угол angle (в радианах) вокруг (0, 0).
        Возвращает (x_rot, y_rot).
        """
        x, y = point
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return x * cos_a - y * sin_a, x * sin_a + y * cos_a

    def generate_tooth_profile(self):
        """
        Генерация контура одного зуба (замкнутый профиль).
        
        1) Дуга по окружности корня (root arc), если нужно
        2) Инволюта (от корневого или базового радиуса – что больше – до наружного радиуса)
        3) Дуга по окружности вершины (addendum arc) у наружного радиуса
        4) Зеркальная инволюта и снова дуга корня (закрываем контур)
        
        Возвращает список (x, y) точек в порядке обхода.
        """

        # Определяем радиус, с которого начинается инволюта
        # Начинаем не с самого корневого, если он меньше базового,
        # а с max(root_radius, base_radius). Если root_radius < base_radius,
        # часть зуба «ниже» базового радиуса обычно скругляется.
        start_radius = max(self.root_radius, self.base_radius)
        if start_radius < 0:
            # Если по расчетам получился отрицательный root_radius,
            # нужно обработать этот случай. Упростим: поставим в 0.
            start_radius = 0

        # Параметр инволюты t: R = base_radius * sqrt(1 + t^2)
        # => t = sqrt((R/base_radius)^2 - 1)
        def param_from_radius(r):
            if r < self.base_radius:
                return 0
            return math.sqrt((r / self.base_radius) ** 2 - 1)

        t_start = param_from_radius(start_radius)
        t_end   = param_from_radius(self.outer_radius)

        # Инволюта от start_radius до outer_radius
        t_values = self.linspace(t_start, t_end, self.num_involute_points)
        involute_curve = [involute_point(self.base_radius, t) for t in t_values]

        # Зеркальная ветвь инволюты: отражение по оси X
        # Порядок разворачиваем, чтобы шло от наружного радиуса к корню
        involute_mirror = [(-x, y) for (x, y) in involute_curve[::-1]]

        # Дуга вершины зуба (addendum arc) по окружности outer_radius
        # от угла, соответствующего последней точке involute_curve,
        # до угла, соответствующего первой точке involute_mirror.
        def angle_of_point(p):
            return math.atan2(p[1], p[0])

        angle1 = angle_of_point(involute_curve[-1])
        angle2 = angle_of_point(involute_mirror[0])
        if angle2 < angle1:
            angle2 += 2 * math.pi

        addendum_arc_points = []
        arc_addendum_div = 10  # количество шагов на дуге вершины
        for a in self.linspace(angle1, angle2, arc_addendum_div):
            x = self.outer_radius * math.cos(a)
            y = self.outer_radius * math.sin(a)
            addendum_arc_points.append((x, y))

        # Дуга корня (root arc): если root_radius > 0,
        # то рисуем дугу от зеркальной инволюты до обычной (по нижнему радиусу).
        # Теоретически, если root_radius < base_radius, то уже была "отрезанная" инволюта.
        # Но для простоты сделаем дугу по окружности root_radius.
        root_arc_points = []
        if self.root_radius > 0 and self.root_radius < start_radius:
            # Случай, когда root_radius < base_radius, 
            # часто делают скругление у корня по технологическим соображениям,
            # но у нас упрощённая схема. Можно пропустить.
            pass
        else:
            # Точки, где инволюта начинается: involute_curve[0] (справа) и involute_mirror[-1] (слева).
            # Углы для корневой дуги.
            left_pt  = involute_mirror[-1]  # Последняя точка зеркальной инволюты
            right_pt = involute_curve[0]    # Первая точка прямой инволюты
            left_ang  = angle_of_point(left_pt)
            right_ang = angle_of_point(right_pt)

            # Чтобы идти по окружности "снизу" слева-направо, если нужно, увеличим right_ang на 2π.
            if right_ang < left_ang:
                right_ang += 2 * math.pi

            arc_root_div = 10
            for a in self.linspace(left_ang, right_ang, arc_root_div):
                x = self.root_radius * math.cos(a)
                y = self.root_radius * math.sin(a)
                root_arc_points.append((x, y))

        # Сборка замкнутого контура зуба:
        # root_arc_points -> involute_curve -> addendum_arc -> involute_mirror -> (обратно к root_arc_points[0])
        tooth_profile = []
        tooth_profile += root_arc_points
        tooth_profile += involute_curve
        tooth_profile += addendum_arc_points
        tooth_profile += involute_mirror
        # На этом профиль «схлопывается» (последняя точка к первой), когда будем строить линии.

        return tooth_profile

    def generate_gear_geometry(self, offset=(0, 0)):
        """
        Генерация массива отрезков, описывающих всю шестерню, 
        путём копирования зуба self.teeth раз и поворота каждого зуба.
        
        :param offset: смещение (ox, oy) для центра шестерни
        :return: список линий, где каждая линия = ((x1, y1), (x2, y2))
        """
        tooth_profile = self.generate_tooth_profile()
        angle_per_tooth = 2.0 * math.pi / self.teeth

        gear_lines = []
        ox, oy = offset

        for i in range(self.teeth):
            angle = i * angle_per_tooth
            # Повернём каждый зуб и затем сместим
            rotated_profile = [self.rotate_point(pt, angle) for pt in tooth_profile]
            shifted_profile = [(x + ox, y + oy) for (x, y) in rotated_profile]

            # Превращаем набор точек в набор отрезков
            for j in range(len(shifted_profile) - 1):
                gear_lines.append((shifted_profile[j], shifted_profile[j + 1]))
            # Замыкаем последний отрезок (между последней и первой точками)
            gear_lines.append((shifted_profile[-1], shifted_profile[0]))

        return gear_lines
