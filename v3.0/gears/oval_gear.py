from .base_gear import BaseGear, to_cartesian
import math

class OvalGear(BaseGear):
    """
    Класс для овальной или эллиптической шестерни.
    В случае e=0 (эксцентриситет=0), эллипс становится окружностью.
    """
    def __init__(self, teeth, ts=10, a=1.0, e=0.3, nodes=1, iradius=0.5, depth=0.2, tolerance=0.001):
        """
        Инициализация овальной шестерни.
        :param teeth: Количество зубьев
        :param ts: Количество сегментов на зуб
        :param a: большая полуось эллипса
        :param e: эксцентриситет (0 ≤ e < 1)
        :param nodes: количество узлов (частота изменения эллипса)
        :param iradius: внутренний радиус
        :param depth: глубина зуба
        :param tolerance: допуск точности вычислений
        """
        super().__init__(teeth_count=teeth, ts=ts, depth=depth, tolerance=tolerance, is_circular=(e==0))
        self.a = a
        self.e = e
        self.nodes = nodes
        self.c = e*a             
        self.p = a*(1.0 - e*e)    # параметр, связанный с эллипсом
        if e == 0:
            self.b = a
        else:
            self.b = math.sqrt(a*a - self.c*self.c)  # малая полуось
        self.iradius = iradius

    def perimeter(self):
        """Приближенный периметр эллипса (формула Рамануджана)."""
        a = self.a
        b = self.b
        h = ((a - b)/(a + b))**2
        return math.pi * (a + b) * (1.0 + (3.0*h)/(10.0+math.sqrt(4.0 - 3.0*h)))

    def outerradius(self, theta):
        """
        Возвращает радиус внешнего контура в зависимости от угла theta.
        Используем формулу полярной координаты для эллипса с фокусом в начале.
        """
        if self.is_circular:
            return self.a  # круг
        return self.p / (1.0 - self.e*math.cos(self.nodes*theta))

    def innerradius(self, theta):
        """Внутренний радиус."""
        return self.iradius

    def dx(self, t):
        """Первая производная x(t) по t для эллиптического профиля."""
        if self.is_circular:
            return -self.a * math.sin(t)
        return (-self.e*self.nodes*self.p*math.cos(t)*math.sin(self.nodes*t)) / (1.0 - self.e*math.cos(self.nodes*t))**2 - \
               (self.p*math.sin(t))/(1.0 - self.e*math.cos(self.nodes*t))

    def dy(self, t):
        """Первая производная y(t) по t для эллиптического профиля."""
        if self.is_circular:
            return self.a * math.cos(t)
        return self.p*math.cos(t)/(1.0 - self.e*math.cos(self.nodes*t)) - \
               (self.e*self.nodes*self.p*math.sin(t)*math.sin(self.nodes*t)) / (1.0 - self.e*math.cos(self.nodes*t))**2

    def dx2(self, t):
        """Вторая производная x(t) по t.
        Уравнения получены аналитически или путём дифференцирования."""
        if self.is_circular:
            return -self.a * math.cos(t)
        return (2.0*self.e*self.e*self.nodes*self.nodes*self.p*math.cos(t)*math.sin(self.nodes*t)**2)/ \
               (1.0 - self.e*math.cos(self.nodes*t))**3 + \
               (2.0*self.e*self.nodes*self.p*math.sin(t)*math.sin(self.nodes*t))/ \
               (1.0 - self.e*math.cos(self.nodes*t))**2 - \
               (self.p*math.cos(t))/(1.0 - self.e*math.cos(self.nodes*t)) - \
               (self.e*self.nodes*self.nodes*self.p*math.cos(t)*math.cos(self.nodes*t))/ \
               (1.0 - self.e*math.cos(self.nodes*t))**2

    def dy2(self, t):
        """Вторая производная y(t) по t."""
        if self.is_circular:
            return -self.a * math.sin(t)
        return (2.0*self.e*self.e*self.nodes*self.nodes*self.p*math.sin(t)*math.sin(self.nodes*t)**2)/ \
               (1.0 - self.e*math.cos(self.nodes*t))**3 - \
               (2.0*self.e*self.nodes*self.p*math.cos(t)*math.sin(self.nodes*t))/ \
               (1.0 - self.e*math.cos(self.nodes*t))**2 - \
               (self.p*math.sin(t))/(1.0 - self.e*math.cos(self.nodes*t)) - \
               (self.e*self.nodes*self.nodes*self.p*math.sin(t)*math.cos(self.nodes*t))/ \
               (1.0 - self.e*math.cos(self.nodes*t))**2
