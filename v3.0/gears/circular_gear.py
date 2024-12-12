from .base_gear import BaseGear, to_cartesian, normalize, involute
import math

class CircularGear(BaseGear):
    """Класс для круглой шестерни, наследующийся от BaseGear."""
    def __init__(self, teeth, ts=10, oradius=1.0, iradius=0.125, depth=0.2, tolerance=0.001):
        """
        Инициализация круглой шестерни.
        :param teeth: количество зубьев
        :param ts: количество сегментов на зуб
        :param oradius: внешний радиус
        :param iradius: внутренний радиус
        :param depth: глубина зуба
        :param tolerance: допуск точности
        """
        super().__init__(teeth_count=teeth, ts=ts, depth=depth, tolerance=tolerance, is_circular=True)
        self.oradius = oradius
        self.iradius = iradius

    def perimeter(self):
        """Периметр окружности равен 2*pi*R."""
        return 2 * math.pi * self.oradius

    def outerradius(self, theta):
        """Для круга радиус постоянен и равен oradius."""
        return self.oradius

    def innerradius(self, theta):
        """Внутренний радиус."""
        return self.iradius

    def dx(self, t):
        """x'(t) для параметризации окружности: -R*sin(t)."""
        return -self.oradius * math.sin(t)

    def dy(self, t):
        """y'(t) для параметризации окружности: R*cos(t)."""
        return self.oradius * math.cos(t)

    def dx2(self, t):
        """Вторая производная x(t): -R*cos(t)."""
        return -self.oradius * math.cos(t)

    def dy2(self, t):
        """Вторая производная y(t): -R*sin(t)."""
        return -self.oradius * math.sin(t)
