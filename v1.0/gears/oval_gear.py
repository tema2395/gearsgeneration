# gears/oval_gear.py

from gears.slfmaker import SLFMaker
from math import sqrt, cos


class OvalGear(SLFMaker):
    def __init__(self, teeth, ts, a, e, nodes, iradius, depth, tolerance):
        """Класс для создания овальной шестерни."""
        self.a = a
        self.e = e
        self.nodes = nodes
        self.c = e * a
        self.is_circular = (e == 0)
        assert 0.0 <= self.e <= 1.0, "Эксцентриситет должен быть в диапазоне [0, 1]"
        self.p = a * (1.0 - self.e * self.e)
        self.b = sqrt(a * a - self.c * self.c) if e != 0 else a
        self.iradius = iradius
        if self.is_circular:
            self.oradius = a  # Определяем внешний радиус для круглой шестерни
        print("Elliptical Gear" if not self.is_circular else "Circular Gear")
        print("a =", self.a, "c =", self.c, "e =", self.e)
        print("teeth =", teeth, "thickness =", depth, "inner radius =", iradius)
        super().__init__(teeth_count=teeth, ts=ts, depth=depth, tolerance=tolerance, is_circular=self.is_circular)

    def outerradius(self, theta):
        """Возвращает внешний радиус для заданного угла theta."""
        if self.is_circular:
            return self.oradius
        return self.p / (1.0 - self.e * cos(self.nodes * theta))
