import math

def involute(base_radius, t):
    """
    Вычисляет точку инволюты.
    """
    x = base_radius * (math.cos(t) + t * math.sin(t))
    y = base_radius * (math.sin(t) - t * math.cos(t))
    return x, y

class Gear:
    def __init__(self, teeth, module, pressure_angle=20, clearance=0.25):
        """
        Инициализация параметров шестерни.
        """
        self.teeth = teeth
        self.module = module
        self.pressure_angle = pressure_angle
        self.clearance = clearance

        self.pitch_diameter = module * teeth
        self.pitch_radius = self.pitch_diameter / 2
        self.base_diameter = self.pitch_diameter * math.cos(math.radians(pressure_angle))
        self.base_radius = self.base_diameter / 2
        self.addendum = module
        self.dedendum = module * (1 + clearance)
        self.outer_radius = self.pitch_radius + self.addendum
        self.root_radius = self.pitch_radius - self.dedendum

        self.num_involute_points = 20

    def generate_tooth_profile(self):
        """
        Генерация профиля зуба.
        """
        t_max = math.sqrt((self.outer_radius / self.base_radius)**2 - 1)
        t_values = [t_max * i / (self.num_involute_points - 1) for i in range(self.num_involute_points)]
        involute_points = [involute(self.base_radius, t) for t in t_values]

        # Зеркальный профиль
        involute_mirror = [(-x, y) for (x, y) in involute_points]

        # Верхняя дуга зуба (соединение на аддентумном круге)
        arc_points = [(self.outer_radius * math.cos(a), self.outer_radius * math.sin(a))
                      for a in self.linspace(math.atan2(involute_points[-1][1], involute_points[-1][0]),
                                             -math.atan2(involute_points[-1][1], -involute_points[-1][0]),
                                             10)]

        # Замкнутый профиль зуба
        tooth_profile = involute_points + arc_points + involute_mirror[::-1]
        return tooth_profile

    def linspace(self, start, stop, num):
        """
        Генерирует равномерно распределенные точки между start и stop.
        """
        step = (stop - start) / (num - 1)
        return [start + i * step for i in range(num)]

    def rotate_point(self, point, angle):
        """
        Поворот точки на заданный угол.
        """
        x, y = point
        x_rot = x * math.cos(angle) - y * math.sin(angle)
        y_rot = x * math.sin(angle) + y * math.cos(angle)
        return x_rot, y_rot

    def generate_gear_geometry(self, offset=(0, 0)):
        """
        Генерация полной геометрии шестерни.
        :param offset: Смещение шестерни (x, y)
        :return: Список линий, определяющих шестерню
        """
        tooth_profile = self.generate_tooth_profile()
        angle_per_tooth = 2 * math.pi / self.teeth

        gear_lines = []
        ox, oy = offset  # Извлекаем смещение

        for i in range(self.teeth):
            angle = i * angle_per_tooth
            rotated_profile = [self.rotate_point(pt, angle) for pt in tooth_profile]
            # Применяем смещение
            rotated_profile = [(x + ox, y + oy) for x, y in rotated_profile]
            for j in range(len(rotated_profile) - 1):
                gear_lines.append((rotated_profile[j], rotated_profile[j + 1]))
            gear_lines.append((rotated_profile[-1], rotated_profile[0]))

        return gear_lines
