# Генерирует стандартное круглое зубчатое колесо.

from slfmaker import SLFMaker
from math import sin, cos, pi, sqrt

class circle(SLFMaker):
    def __init__(self, teeth, ts, oradius, iradius, depth, tolerance):
        self.centerOffset = 0
        self.iradius = iradius  # внутренний радиус, для отверстия
        self.oradius = oradius  # внешний радиус
        print("Circle")
        print("radius =", oradius)
        print("teeth =", teeth, "thickness =", depth, "inner radius =", iradius)

        # Инициализация базового класса SLFMaker с флагом is_circular=True
        super().__init__(teethCount=teeth, ts=ts, depth=depth, tolerance=tolerance, is_circular=True)

    def outerradius(self, theta):
        """Возвращает внешний радиус для заданного угла theta."""
        return self.oradius

    def innerradius(self, theta):
        """Возвращает внутренний радиус для заданного угла theta."""
        return self.iradius

    def dx(self, t):
        """Первая производная по t для x координаты."""
        return -self.oradius * sin(t)

    def dy(self, t):
        """Первая производная по t для y координаты."""
        return self.oradius * cos(t)

    def dx2(self, t):
        """Вторая производная по t для x координаты."""
        return -self.oradius * cos(t)

    def dy2(self, t):
        """Вторая производная по t для y координаты."""
        return -self.oradius * sin(t)

    def perimeter(self):
        """Вычисляет периметр круга."""
        return 2 * pi * self.oradius

    def width(self):
        """Возвращает ширину зубчатого колеса."""
        return self.outerradius(0) * 2

    def get_lines(self):
        """Возвращает список линий для отображения в Tkinter."""
        lines = []
        points = [(tooth['x'], tooth['y']) for tooth in self.teethLoc]
        for i in range(len(points)):
            j = (i + 1) % len(points)
            lines.append((points[i], points[j]))
        return lines

if __name__ == "__main__":
    # Создание экземпляра класса circle с заданными параметрами
    e = circle(teeth=20, ts=10, oradius=1.0, iradius=0.125, depth=0.2, tolerance=0.001)
    
    # Запись геометрии в DXF файл
    e.write('cgear7.dxf')
