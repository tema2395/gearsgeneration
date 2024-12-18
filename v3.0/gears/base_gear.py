import math

def involute(a, t):
    return [a * (math.sin(t) - t * math.cos(t)), a * (math.cos(t) + t * math.sin(t)) - a]

def normalize(x, y):
    l = math.sqrt(x*x + y*y)
    if l == 0:
        return 0.0, 0.0
    return x/l, y/l

def to_cartesian(r, theta):
    return (r * math.cos(theta), r * math.sin(theta))

def findClosest(l, v):
    d = [abs(x[0] - v) for x in l]
    m = min(d)
    return l[d.index(m)][1]

def findClosestDown(l, v):
    filtered = [x for x in l if v - x[0] >= 0.0]
    if not filtered:
        # Если нет подходящих значений, вернем ближайшее меньшее или равное
        # Но в оригинале был raise ValueError. Сохраним логику:
        raise ValueError("No elements in list satisfy v - x[0] >= 0.0")
    d = [v - x[0] for x in filtered]
    m = min(d)
    return filtered[d.index(m)][1]


class BaseGear:
    def __init__(self, teeth_count, ts=10, depth=0.2, tolerance=0.001, is_circular=False):
        self.teeth_count = teeth_count
        self.tooth_slices = ts
        self.depth = depth
        self.tolerance = tolerance
        self.is_circular = is_circular
        self.teethLoc = []

    def perimeter(self):
        raise NotImplementedError

    def outerradius(self, theta):
        raise NotImplementedError

    def innerradius(self, theta):
        raise NotImplementedError

    def dx(self, t):
        raise NotImplementedError

    def dy(self, t):
        raise NotImplementedError

    def dx2(self, t):
        raise NotImplementedError

    def dy2(self, t):
        raise NotImplementedError

    def radius_of_curvature(self, t):
        dx = self.dx(t)
        dy = self.dy(t)
        dx2 = self.dx2(t)
        dy2 = self.dy2(t)
        denom = (dx * dy2 - dx2 * dy)
        if denom == 0:
            return float('inf')
        return ((dx*dx + dy*dy)**1.5)/abs(denom)

    def calc_points(self):
        # Должен быть переопределен в потомках, где вычисляется геометрия.
        pass

    def get_lines(self):
        points = self.teethLoc
        lines = []
        for i in range(len(points)):
            j = (i+1)%len(points)
            lines.append(((points[i]['x'], points[i]['y']),
                          (points[j]['x'], points[j]['y'])))
        return lines
