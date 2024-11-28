# slfmaker.py

"""Этот модуль содержит базовые классы и
вспомогательные функции для генерации геометрии шестерён. 
Основной класс SLFMaker отвечает за вычисление точек шестерни и экспорт их в файл."""

from math import sin, cos, pi, sqrt, atan

def involute(a, t):
    """Вычисляет точку инволюты окружности радиуса a при параметре t. Инволюта - вид зубчатого зацепления"""
    return [a * (sin(t) - t * cos(t)), a * (cos(t) + t * sin(t)) - a]

def minIndex(l):
    m = l[0]
    mi = 0
    for n in range(1, len(l)):
        if l[n] < m:
            m = l[n]
            mi = n
    return mi

def findClosest(l, v):
    """Поиск ближайшего значения в списке."""
    d = [abs(x[0] - v) for x in l]
    return l[minIndex(d)][1]

def findClosestDown(l, v):
    """Поиск ближайшего значения в списке, где x[0] <= v."""
    filtered = [x for x in l if v - x[0] >= 0.0]
    if not filtered:
        raise ValueError("No elements in list l satisfy v - x[0] >= 0.0")
    best = filtered[0]
    bestIndex = 0
    for x in range(len(l)):
        i = v - l[x][0]
        if (i >= 0.0 and i <= best[0]):
            bestIndex = x
            best = i
    return l[bestIndex][1]

def normalize(x, y):
    """Нормализация вектора."""
    if (x == 0.0 and y == 0.0):
        return (0.0, 0.0)
    return (x / sqrt(x * x + y * y), y / sqrt(x * x + y * y))

def toCartesian(r, t):
    """Преобразование полярных координат в декартовы."""
    return (r * cos(t), r * sin(t))

class SLFMaker:
    def __init__(self, teethCount, ts=5, depth=0.1, tolerance=0.001, is_circular=False):
        """Базовый класс для создания шестерён. Определяет методы для вычисления периметра, ширины, радиуса кривизны и точек шестерни."""
        self.depth = depth
        self.teethLoc = []
        self.teethCount = teethCount
        self.is_circular = is_circular
        self.cpitch = self.perimeter() / teethCount  # Циркулярный шаг
        self.toothSlices = ts
        print("est. circular pitch:", self.cpitch, "est. perimeter: ", self.perimeter())

        self.tolerance = tolerance

    def write(self, filename):
        """Запись данных зубчатого колеса в файл."""
        if not self.teethLoc:
            self.calcPoints()
        with open(filename, 'w') as f:
            self.preamble(f)
            self.amble(f)
            self.postamble(f)

    def amble(self, f):
        """Создание геометрии зубчатого колеса в файле."""
        import string

        n = 0
        inc = 0.01

        print("teeth completed: ", end=' ')

        teeth_ends = []
        inner_pts = []
        # Проход по каждому зубу
        for d in self.teethLoc:
            rc = abs(d['rc'])
            inverseInvoluteTableY = []
            inverseInvoluteTableX = []
            t = 0.0
            while t < pi / 2.0:
                i = involute(rc, t)
                inverseInvoluteTableX.append((i[0], t))
                inverseInvoluteTableY.append((i[1], t))
                t += inc

            # Параметр t на окружности деления
            td = findClosest(inverseInvoluteTableY, self.dedendumd)

            # Параметр t на вершине зуба
            tt = findClosest(inverseInvoluteTableY, self.dedendumd + self.adendumd)

            # Обрезка сторон инволюты для устранения наложений

            # Новые координаты
            r = d['r']
            x = r * cos(d['t'])
            y = r * sin(d['t'])

            dx = self.dx(d['t'])
            dy = self.dy(d['t'])

            dx2 = self.dx2(d['t'])
            dy2 = self.dy2(d['t'])

            dx, dy = normalize(dx, dy)

            # Ширина зуба = циркулярный шаг / 2 - люфт
            toothWidth = self.cpitch / 2.0
            offset = (toothWidth / 2.0) + involute(rc, td)[0]

            # Убедиться, что инволюта не пересекает симметричного партнера
            tx = findClosestDown(inverseInvoluteTableX, offset)

            if (tt > tx):
                print("clipping tooth " + repr(n) + ": " + repr(tt) + " " + repr(tx))
                tt = tx

            if (dy < 0):
                rot = 3.0 * pi / 2.0 + atan(dx / dy)
            else:
                rot = pi / 2.0 + atan(dx / dy)

            t = 0.0
            m = 0

            pts = []
            while m < self.toothSlices:
                ix, iy = involute(rc, t)
                px = -offset + ix
                py = iy

                npx = px * cos(rot) + py * sin(rot)
                npy = px * -sin(rot) + py * cos(rot)

                arr = [(x + npx, y + npy,)]

                # Правая сторона
                px = offset - ix  # отражение
                py = iy

                npx = px * cos(rot) + py * sin(rot)
                npy = px * -sin(rot) + py * cos(rot)

                arr.append((x + npx, y + npy,))
                pts.append(arr)

                t += tt / (self.toothSlices - 1.0)
                m += 1

            # Рисование линий зуба
            for i in range(0, len(pts)):
                # Линия левой стороны
                f.write("  0\nLINE\n")
                f.write("  8\n %s \n" % ('gear'))  # Имя слоя
                if(i == 0):
                    f.write(" 10\n%f\n" % pts[i][0][0])
                    f.write(" 20\n%f\n" % pts[i][0][1])
                else:
                    f.write(" 10\n%f\n" % pts[i-1][0][0])
                    f.write(" 20\n%f\n" % pts[i-1][0][1])
                f.write(" 11\n%f\n" % pts[i][0][0])
                f.write(" 21\n%f\n" % pts[i][0][1])

                # Линия правой стороны
                f.write("  0\nLINE\n")
                f.write("  8\n %s \n" % ('gear'))
                if(i == 0):
                    f.write(" 10\n%f\n" % pts[i][1][0])
                    f.write(" 20\n%f\n" % pts[i][1][1])
                else:
                    f.write(" 10\n%f\n" % pts[i-1][1][0])
                    f.write(" 20\n%f\n" % pts[i-1][1][1])
                f.write(" 11\n%f\n" % pts[i][1][0])
                f.write(" 21\n%f\n" % pts[i][1][1])

            # Сохранение начальных точек для соединения зубов
            teeth_ends.append((pts[0][0][0], pts[0][0][1], pts[0][1][0], pts[0][1][1],))

            # Соединение последних точек зуба
            f.write("  0\nLINE\n")
            f.write("  8\n %s \n" % ('gear'))
            f.write(" 10\n%f\n" % pts[-1][0][0])
            f.write(" 20\n%f\n" % pts[-1][0][1])
            f.write(" 11\n%f\n" % pts[-1][1][0])
            f.write(" 21\n%f\n" % pts[-1][1][1])

            # Внутренние точки для внутреннего отверстия
            ri = self.innerradius(d['t'])
            xi, yi = toCartesian(ri, d['t'])

            inner_pts.append((xi, yi,))

            print(n, end=' ')
            n += 1

        # Соединение внутреннего радиуса
        for i in range(0, len(inner_pts)):
            f.write("  0\nLINE\n")
            f.write("  8\n %s \n" % ('gear'))  # Имя слоя
            if(i == 0):
                f.write(" 10\n%f\n" % inner_pts[-1][0])
                f.write(" 20\n%f\n" % inner_pts[-1][1])
            else:
                f.write(" 10\n%f\n" % inner_pts[i-1][0])
                f.write(" 20\n%f\n" % inner_pts[i-1][1])
            f.write(" 11\n%f\n" % inner_pts[i][0])
            f.write(" 21\n%f\n" % inner_pts[i][1])

        # Соединение концов зубов
        for i in range(0, len(teeth_ends)):
            f.write("  0\nLINE\n")
            f.write("  8\n %s \n" % ('gear'))  # Имя слоя
            if(i == 0):
                f.write(" 10\n%f\n" % teeth_ends[-1][0])
                f.write(" 20\n%f\n" % teeth_ends[-1][1])
            else:
                f.write(" 10\n%f\n" % teeth_ends[i-1][0])
                f.write(" 20\n%f\n" % teeth_ends[i-1][1])
            f.write(" 11\n%f\n" % teeth_ends[i][2])
            f.write(" 21\n%f\n" % teeth_ends[i][3])

    def preamble(self, f):
        """Запись заголовка DXF файла."""
        f.write("  999\nDXF created from gearsgen.py phill baker\n")
        f.write("  0\nSECTION\n")
        f.write("  2\nENTITIES\n")

    def postamble(self, f):
        """Запись окончания DXF файла."""
        f.write("  0\nENDSEC\n")
        f.write("  0\nEOF\n")

    def radiusOfCurvature(self, t):
        """Вычисление радиуса кривизны в точке t."""
        dx = self.dx(t)
        dy = self.dy(t)
        dx2 = self.dx2(t)
        dy2 = self.dy2(t)

        return ((dx * dx + dy * dy) ** 1.5) / (dx * dy2 - dx2 * dy)

    def calcPoints(self):
        """Вычисление точек для зубчатого колеса."""
        refinement = 1
        if self.is_circular:
            halfteethCount = self.teethCount
        else:
            halfteethCount = self.teethCount * 2
        halfpitch = self.cpitch / 2.0

        while True:
            module = halfpitch * 2.0 / pi

            self.dedendumd = module * 1.25
            self.adendumd = module

            ccd = 0.0

            theta = 0.0
            ro = self.outerradius(0) - self.dedendumd

            fx = lx = ro * cos(0)
            fy = ly = ro * sin(0)

            actualTeeth = 1

            while theta < 2.0 * pi:
                theta += self.tolerance
                ro = self.outerradius(theta) - self.dedendumd
                x = ro * cos(theta)
                y = ro * sin(theta)
                # Добавление расстояния от последней точки
                ccd += sqrt((x - lx) ** 2 + (y - ly) ** 2)
                if (ccd >= halfpitch and actualTeeth < halfteethCount):
                    # Добавление новой точки
                    actualTeeth += 1
                    ccd = 0.0

                lx = x
                ly = y

            print(f"refinement {refinement}, half-teeth = {actualTeeth}, extra = {ccd}, c pitch = {halfpitch * 2.0}")
            if halfteethCount == actualTeeth and abs(ccd - halfpitch) < self.tolerance * 5:
                break

            refinement += 1
            halfpitch = (halfpitch * actualTeeth + ccd) / (halfteethCount + 1)

        self.cpitch = halfpitch * 2.0

        print("new circular pitch =", self.cpitch)
        print("new perimeter =", self.cpitch * self.teethCount)

        module = self.cpitch / pi

        self.dedendumd = module * 1.25
        self.adendumd = module

        print("dedendum distance =", self.dedendumd)
        print("adendum distance =", self.adendumd)
        print("tooth height =", self.dedendumd + self.adendumd)

        # Вычисление окончательных точек и сохранение данных
        ccd = 0.0
        theta = 0.0
        ro = self.outerradius(theta) - self.dedendumd

        lx = ro * cos(theta)
        ly = ro * sin(theta)

        rc = self.radiusOfCurvature(theta)

        self.teethLoc = [{'x': lx, 'y': ly, 'r': ro, 't': 0.0, 'rc': rc}]
        self.gapLoc = []
        gapFlag = True

        print("computing points for final refinement")

        actualTeeth = 1

        while actualTeeth < halfteethCount:
            theta += self.tolerance
            ro = self.outerradius(theta) - self.dedendumd
            x = ro * cos(theta)
            y = ro * sin(theta)
            # Добавление расстояния от последней точки
            ccd = sqrt((x - lx) ** 2 + (y - ly) ** 2)
            if (ccd >= halfpitch):
                # Добавление новой точки
                rc = self.radiusOfCurvature(theta)
                if gapFlag:
                    self.gapLoc.append({'x': x, 'y': y, 'r': ro, 't': theta, 'rc': rc})
                else:
                    self.teethLoc.append({'x': x, 'y': y, 'r': ro, 't': theta, 'rc': rc})

                gapFlag = not gapFlag
                lx = x
                ly = y
                actualTeeth += 1
