import math

def involute_point(base_radius, t):
    """Вычисляет координаты точки на инволюте окружности радиуса base_radius по параметру t."""
    x = base_radius * (math.cos(t) + t * math.sin(t))
    y = base_radius * (math.sin(t) - t * math.cos(t))
    return x, y

class Gear:
    def __init__(self, teeth, module, pressure_angle=20, clearance=0.25):
        """
        Инициализация круговой (обычной) шестерни.
        """
        self.teeth = teeth
        self.module = module
        self.pressure_angle = pressure_angle
        self.clearance = clearance

        # Расчёты
        self.pitch_diameter = module * teeth
        self.pitch_radius   = self.pitch_diameter / 2
        self.base_diameter  = self.pitch_diameter * math.cos(math.radians(pressure_angle))
        self.base_radius    = self.base_diameter / 2
        self.addendum       = module
        self.dedendum       = module * (1 + clearance)
        self.outer_radius   = self.pitch_radius + self.addendum
        self.root_radius    = self.pitch_radius - self.dedendum

        self.num_involute_points = 30

    def linspace(self, start, stop, num):
        if num <= 1:
            return [start]
        step = (stop - start) / (num - 1)
        return [start + i * step for i in range(num)]

    def rotate_point(self, point, angle):
        x, y = point
        ca = math.cos(angle)
        sa = math.sin(angle)
        return (x*ca - y*sa, x*sa + y*ca)

    def generate_tooth_profile(self):
        """
        Генерация одного зуба — замкнутый контур из:
         1) Дуги корня (если нужно)
         2) Инволюты (от max(root_radius, base_radius) до outer_radius)
         3) Дуги верха (outer_radius)
         4) Зеркальной инволюты
        """
        start_radius = max(self.root_radius, self.base_radius)
        if start_radius < 0:
            start_radius = 0

        def param_from_r(r):
            if r < self.base_radius:
                return 0
            return math.sqrt((r / self.base_radius)**2 - 1)

        t_start = param_from_r(start_radius)
        t_end   = param_from_r(self.outer_radius)

        t_values = self.linspace(t_start, t_end, self.num_involute_points)
        involute_curve = [involute_point(self.base_radius, t) for t in t_values]
        involute_mirror = [(-x, y) for x, y in involute_curve[::-1]]

        def angle_of_point(p):
            return math.atan2(p[1], p[0])

        angle1 = angle_of_point(involute_curve[-1])
        angle2 = angle_of_point(involute_mirror[0])
        if angle2 < angle1:
            angle2 += 2*math.pi

        arc_top = []
        arc_div = 10
        for a in self.linspace(angle1, angle2, arc_div):
            x = self.outer_radius * math.cos(a)
            y = self.outer_radius * math.sin(a)
            arc_top.append((x, y))

        # Дуга корня (если root_radius > 0 && root_radius >= base_radius, и т.д.)
        root_arc = []
        # Упрощённо
        if self.root_radius > 0 and self.root_radius >= self.base_radius:
            left_pt = involute_mirror[-1]
            right_pt = involute_curve[0]
            la = angle_of_point(left_pt)
            ra = angle_of_point(right_pt)
            if ra < la:
                ra += 2*math.pi
            arc_div2 = 10
            for a in self.linspace(la, ra, arc_div2):
                x = self.root_radius * math.cos(a)
                y = self.root_radius * math.sin(a)
                root_arc.append((x,y))

        # Формируем итоговый список
        profile = []
        profile += root_arc
        profile += involute_curve
        profile += arc_top
        profile += involute_mirror

        return profile

    def generate_gear_geometry(self, offset=(0,0)):
        tooth_profile = self.generate_tooth_profile()
        angle_per_tooth = 2*math.pi / self.teeth

        lines = []
        ox, oy = offset

        for i in range(self.teeth):
            angle = i*angle_per_tooth
            rot = [self.rotate_point(pt, angle) for pt in tooth_profile]
            shift = [(x+ox, y+oy) for (x,y) in rot]
            # В отрезки
            for j in range(len(shift)-1):
                lines.append((shift[j], shift[j+1]))
            lines.append((shift[-1], shift[0]))
        return lines
