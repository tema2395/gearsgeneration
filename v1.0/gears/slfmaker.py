# gears/slfmaker.py

from math import sin, cos, pi, sqrt, atan


def normalize(x, y):
    """Нормализация вектора."""
    if (x == 0.0 and y == 0.0):
        return (0.0, 0.0)
    length = sqrt(x * x + y * y)
    return (x / length, y / length)


def to_cartesian(r, theta):
    """Преобразование полярных координат в декартовы."""
    return (r * cos(theta), r * sin(theta))


def involute(a, t):
    """Вычисляет точку инволюты окружности радиуса a при параметре t."""
    return [a * (sin(t) - t * cos(t)), a * (cos(t) + t * sin(t)) - a]


class SLFMaker:
    def __init__(self, teeth_count, ts=5, depth=0.1, tolerance=0.001, is_circular=False):
        """Базовый класс для создания шестерён."""
        self.depth = depth
        self.teeth_loc = []
        self.teeth_count = teeth_count
        self.is_circular = is_circular
        self.tooth_slices = ts
        self.tolerance = tolerance
        self.cpitch = self.perimeter() / teeth_count  # Циркулярный шаг
        print("Est. circular pitch:", self.cpitch, "Est. perimeter:", self.perimeter())

    def perimeter(self):
        """Вычисляет периметр шестерни."""
        if self.is_circular:
            return 2 * pi * self.oradius
        else:
            # Для овальной шестерни используем приближение Рамануджана
            a = self.a
            b = self.b
            h = ((a - b) / (a + b)) ** 2
            return pi * (a + b) * (1 + (3 * h) / (10 + sqrt(4 - 3 * h)))

    def outerradius(self, theta):
        """Возвращает внешний радиус для заданного угла theta."""
        if self.is_circular:
            return self.oradius
        else:
            return self.p / (1.0 - self.e * cos(self.nodes * theta))

    def innerradius(self, theta):
        """Возвращает внутренний радиус для заданного угла theta."""
        return self.iradius

    def dx(self, t):
        """Первая производная по t для x координаты."""
        if self.is_circular:
            return -self.oradius * sin(t)
        else:
            return (-self.e * self.nodes * self.p * cos(t) * sin(self.nodes * t)) / (1.0 - self.e * cos(self.nodes * t))**2 - \
                   (self.p * sin(t)) / (1.0 - self.e * cos(self.nodes * t))

    def dy(self, t):
        """Первая производная по t для y координаты."""
        if self.is_circular:
            return self.oradius * cos(t)
        else:
            return self.p * cos(t) / (1.0 - self.e * cos(self.nodes * t)) - \
                   (self.e * self.nodes * self.p * sin(t) * sin(self.nodes * t)) / (1.0 - self.e * cos(self.nodes * t))**2

    def dx2(self, t):
        """Вторая производная по t для x координаты."""
        if self.is_circular:
            return -self.oradius * cos(t)
        else:
            return (2.0 * self.e**2 * self.nodes**2 * self.p * cos(t) * sin(self.nodes * t)**2) / \
                   (1.0 - self.e * cos(self.nodes * t))**3 + \
                   (2.0 * self.e * self.nodes * self.p * sin(t) * sin(self.nodes * t)) / \
                   (1.0 - self.e * cos(self.nodes * t))**2 - \
                   (self.p * cos(t)) / (1.0 - self.e * cos(self.nodes * t)) - \
                   (self.e * self.nodes**2 * self.p * cos(t) * cos(self.nodes * t)) / \
                   (1.0 - self.e * cos(self.nodes * t))**2

    def dy2(self, t):
        """Вторая производная по t для y координаты."""
        if self.is_circular:
            return -self.oradius * sin(t)
        else:
            return (2.0 * self.e**2 * self.nodes**2 * self.p * sin(t) * sin(self.nodes * t)**2) / \
                   (1.0 - self.e * cos(self.nodes * t))**3 - \
                   (2.0 * self.e * self.nodes * self.p * cos(t) * sin(self.nodes * t)) / \
                   (1.0 - self.e * cos(self.nodes * t))**2 - \
                   (self.p * sin(t)) / (1.0 - self.e * cos(self.nodes * t)) - \
                   (self.e * self.nodes**2 * self.p * sin(t) * cos(self.nodes * t)) / \
                   (1.0 - self.e * cos(self.nodes * t))**2

    def radius_of_curvature(self, t):
        """Вычисляет радиус кривизны в точке t."""
        dx = self.dx(t)
        dy = self.dy(t)
        dx2 = self.dx2(t)
        dy2 = self.dy2(t)
        denominator = (dx * dy2 - dx2 * dy)
        if denominator == 0:
            return float('inf')  # Избежание деления на ноль
        return ((dx * dx + dy * dy) ** 1.5) / denominator

    def calc_points(self):
        """Вычисление точек для шестерни."""
        refinement = 1
        max_refinement = 100 
        if self.is_circular:
            halfteeth_count = self.teeth_count
        else:
            halfteeth_count = self.teeth_count * 2
        halfpitch = self.cpitch / 2.0

        while refinement <= max_refinement:
            module = halfpitch * 2.0 / pi
            self.dedendumd = module * 1.25
            self.adendumd = module

            ccd = 0.0
            theta = 0.0
            ro = self.outerradius(theta) - self.dedendumd
            lx = ro * cos(theta)
            ly = ro * sin(theta)
            actual_teeth = 1

            while theta < 2.0 * pi:
                theta += self.tolerance
                ro = self.outerradius(theta) - self.dedendumd
                x = ro * cos(theta)
                y = ro * sin(theta)
                ccd += sqrt((x - lx) ** 2 + (y - ly) ** 2)
                if (ccd >= halfpitch and actual_teeth < halfteeth_count):
                    actual_teeth += 1
                    ccd = 0.0
                lx = x
                ly = y

            print(f"Refinement {refinement}, Half-teeth = {actual_teeth}, Extra = {ccd}, C pitch = {halfpitch * 2.0}")
            if halfteeth_count == actual_teeth and abs(ccd - halfpitch) < self.tolerance * 5:
                break

            refinement += 1
            halfpitch = (halfpitch * actual_teeth + ccd) / (halfteeth_count + 1)

        if refinement > max_refinement:
            raise RuntimeError("Достигнуто максимальное количество уточнений при расчёте периметра.")

        self.cpitch = halfpitch * 2.0
        print("New circular pitch =", self.cpitch)
        print("New perimeter =", self.cpitch * self.teeth_count)

        module = self.cpitch / pi
        self.dedendumd = module * 1.25
        self.adendumd = module
        print("Dedendum distance =", self.dedendumd)
        print("Adendum distance =", self.adendumd)
        print("Tooth height =", self.dedendumd + self.adendumd)

        # Окончательное вычисление точек
        ccd = 0.0
        theta = 0.0
        ro = self.outerradius(theta) - self.dedendumd
        lx = ro * cos(theta)
        ly = ro * sin(theta)
        rc = self.radius_of_curvature(theta)

        self.teeth_loc = [{'x': lx, 'y': ly, 'r': ro, 't': 0.0, 'rc': rc}]
        self.gap_loc = []
        gap_flag = True
        actual_teeth = 1

        print("Computing points for final refinement")

        while actual_teeth < halfteeth_count and theta < 10 * pi: 
            theta += self.tolerance
            ro = self.outerradius(theta) - self.dedendumd
            x = ro * cos(theta)
            y = ro * sin(theta)
            ccd = sqrt((x - lx) ** 2 + (y - ly) ** 2)
            if (ccd >= halfpitch):
                rc = self.radius_of_curvature(theta)
                if gap_flag:
                    self.gap_loc.append({'x': x, 'y': y, 'r': ro, 't': theta, 'rc': rc})
                else:
                    self.teeth_loc.append({'x': x, 'y': y, 'r': ro, 't': theta, 'rc': rc})
                gap_flag = not gap_flag
                lx = x
                ly = y
                actual_teeth += 1

        if actual_teeth < halfteeth_count:
            raise RuntimeError("Не удалось завершить расчёт точек шестерни. Попробуйте изменить параметры.")

    def get_lines(self):
        """Возвращает список линий для рисования."""
        lines = []
        # Объединяем зубья и промежутки
        all_teeth = self.teeth_loc + self.gap_loc
        # Сортируем по углу
        all_teeth_sorted = sorted(all_teeth, key=lambda d: d['t'])
        points = [(tooth['x'], tooth['y']) for tooth in all_teeth_sorted]
        for i in range(len(points)):
            j = (i + 1) % len(points)
            lines.append((points[i], points[j]))
        return lines
