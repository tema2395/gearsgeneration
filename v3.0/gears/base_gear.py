import math

def normalize(x, y):
    """Нормализует вектор (x, y), возвращая единичный вектор в том же направлении.
    Если вектор нулевой, возвращается (0.0, 0.0)."""
    if (x == 0.0 and y == 0.0):
        return (0.0, 0.0)
    length = math.sqrt(x * x + y * y)
    return (x / length, y / length)

def to_cartesian(r, theta):
    """Преобразует полярные координаты (r, theta) в декартовы (x, y)."""
    return (r * math.cos(theta), r * math.sin(theta))

def involute(a, t):
    """Вычисляет точку инволюты круга радиуса a для параметра t.
    Инволюта - кривая, возникающая при раскатывании прямой по окружности."""
    return [a * (math.sin(t) - t * math.cos(t)), a * (math.cos(t) + t * math.sin(t)) - a]

class BaseGear:
    """Базовый класс для всех типов шестерён.
    Предоставляет общий интерфейс и некоторые базовые вычисления."""
    def __init__(self, teeth_count, ts=10, depth=0.2, tolerance=0.001, is_circular=False):
        """
        Инициализация базовой шестерни.
        :param teeth_count: Количество зубьев
        :param ts: Количество сегментов на зуб (для детализации)
        :param depth: Глубина зуба
        :param tolerance: Допуск точности вычислений
        :param is_circular: Является ли шестерня круговой
        """
        self.teeth_count = teeth_count
        self.tooth_slices = ts
        self.depth = depth
        self.tolerance = tolerance
        self.is_circular = is_circular
        self.teeth_loc = []  # Список точек положения зубьев
        self.gap_loc = []    # Список точек положения впадин (можно расширить)

    def perimeter(self):
        """Должен вернуть периметр наружного контура шестерни (длина окружности и т.п.)."""
        raise NotImplementedError

    def outerradius(self, theta):
        """Возвращает радиус внешнего контура шестерни при угле theta."""
        raise NotImplementedError

    def innerradius(self, theta):
        """Возвращает внутренний радиус шестерни при угле theta."""
        raise NotImplementedError

    def dx(self, t):
        """Первая производная x(t) по параметру t.
        Нужна для вычисления кривизны и других характеристик."""
        raise NotImplementedError

    def dy(self, t):
        """Первая производная y(t) по параметру t."""
        raise NotImplementedError

    def dx2(self, t):
        """Вторая производная x(t)."""
        raise NotImplementedError

    def dy2(self, t):
        """Вторая производная y(t)."""
        raise NotImplementedError

    def radius_of_curvature(self, t):
        """
        Вычисляет радиус кривизны контура в точке, определённой параметром t.
        Формула: R = ((x'^2 + y'^2)^(3/2)) / |x'y'' - y'x''|
        """
        dx = self.dx(t)
        dy = self.dy(t)
        dx2 = self.dx2(t)
        dy2 = self.dy2(t)
        denominator = (dx * dy2 - dx2 * dy)
        if denominator == 0:
            return float('inf')
        return ((dx * dx + dy * dy) ** 1.5) / denominator

    def calc_points(self):
        """
        Вычисляет точки внешнего контура шестерни.
        В данной упрощённой версии просто берём точки по углам и радиусам.
        """
        total_perim = self.perimeter()
        self.cpitch = total_perim / self.teeth_count

        dtheta = 2.0 * math.pi / self.teeth_count
        for i in range(self.teeth_count):
            theta = i * dtheta
            r = self.outerradius(theta) - (self.depth / 2.0)
            x, y = to_cartesian(r, theta)
            # Сохраняем точку, а также радиус кривизны в этой точке
            self.teeth_loc.append({'x': x, 'y': y, 'r': r, 't': theta, 'rc': self.radius_of_curvature(theta)})

    def get_points(self):
        """Возвращает список координат (x, y) точек контура.
        Если точки ещё не были вычислены, вызывает calc_points()."""
        if not self.teeth_loc:
            self.calc_points()
        return [(p['x'], p['y']) for p in self.teeth_loc]

    def get_lines(self):
        """Возвращает список отрезков (пар точек), определяющих контур шестерни."""
        points = self.get_points()
        lines = []
        for i in range(len(points)):
            j = (i + 1) % len(points)
            lines.append((points[i], points[j]))
        return lines
