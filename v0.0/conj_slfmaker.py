"""Этот модуль содержит класс ConjugateSLFMaker, 
который отвечает за генерацию пары сопряжённых шестерён.
Такие шестерни взаимодействуют друг с другом с определёнными параметрами."""

from math import sin, cos, pi, sqrt, atan, acos
from slfmaker import SLFMaker, involute, normalize, findClosest, findClosestDown, toCartesian 

class ConjugateSLFMaker(SLFMaker):
    """Расширяет функциональность SLFMaker для создания сопряжённых шестерён."""

    def __init__(self, teethCount, ts=5, period=2, holedistance=1.0, depth=0.1, tolerance=0.001):
        """
        Инициализирует экземпляр класса ConjugateSLFMaker.

        :param teethCount: Количество зубьев на шестерне.
        :param ts: Количество делений зуба.
        :param period: Период сопряжения.
        :param holedistance: Расстояние между отверстиями.
        :param depth: Глубина зуба.
        :param tolerance: Допуск для вычислений.
        """
        # Вызов конструктора базового класса SLFMaker без tolerance
        super().__init__(teethCount=teethCount, ts=ts, period=period, holedistance=holedistance, depth=depth)
        
        # Инициализация дополнительных атрибутов
        self.tolerance = tolerance
        self.teethLoc = []
        self.gapLoc = []
        self.periodfactor = period
        self.conjugateTeethLoc = []
        self.toothSlices = ts
        self.secondOffset = 1.0

        print("est. circular pitch:", self.cpitch, "est. perimeter: ", self.perimeter())

    def write(self, filename):
        """
        Записывает данные шестерни в файл.

        :param filename: Имя файла для записи.
        """
        if not self.teethLoc:
            self.calcPoints()
        if not self.conjugateTeethLoc:
            self.calcConjugatePoints()
        with open(filename, 'w') as f:
            self.preamble(f)
            self.amble(f)
            self.postamble(f)

    def amble(self, f):
        """
        Создаёт чертеж шестерён и записывает его в файл.

        :param f: Файл для записи.
        """
        # self.teethLoc и self.conjugateTeethLoc содержат координаты зубьев
        self.doShape(f, self.teethLoc, "a", "sBlu")
        self.doShape(f, self.conjugateTeethLoc, "b", "sRed")

    def doShape(self, f, teethLoc, gearLetter, color):
        """
        Рисует форму шестерни.

        :param f: Файл для записи.
        :param teethLoc: Локальные координаты зубьев.
        :param gearLetter: Буква для обозначения шестерни.
        :param color: Цвет шестерни.
        """
        import string

        inc = 0.01
        teethCount = len(teethLoc)

        print("teeth completed: ", end=' ')

        n = 0
        teeth_ends = []
        inner_pts = []
        for d in teethLoc:
            rc = abs(d['rc'])
            inverseInvoluteTableY = []
            inverseInvoluteTableX = []
            t = 0.0
            while t < pi / 2.0:
                i = involute(rc, t)
                inverseInvoluteTableX.append((i[0], t))
                inverseInvoluteTableY.append((i[1], t))
                t += inc

            # t параметр на пике окружности
            td = findClosest(inverseInvoluteTableY, self.dedendumd)

            # t параметр на вершине зуба
            tt = findClosest(inverseInvoluteTableY, self.dedendumd + self.adendumd)

            # Новый радиус и соответствующие x и y
            r = d['r']
            x = r * cos(d['t'])
            y = r * sin(d['t'])

            dx = d['dx']
            dy = d['dy']

            dx, dy = normalize(dx, dy)

            # Ширина зуба = половина круговой высоты - люфт
            # Смещение = половина ширины зуба + x(td)
            toothWidth = self.cpitch / 2.0
            offset = (toothWidth / 2.0) + involute(rc, td)[0]

            # Убедиться, что инволюта не пересечёт симметричного партнёра
            tx = findClosestDown(inverseInvoluteTableX, offset)

            if tt > tx:
                tt = tx

            if dy < 0:
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
                px = offset - ix  # зеркальное отображение левой стороны
                py = iy

                npx = px * cos(rot) + py * sin(rot)
                npy = px * -sin(rot) + py * cos(rot)
                arr.append((x + npx, y + npy,))

                pts.append(arr)

                t += tt / (self.toothSlices - 1.0)
                m += 1

            for i in range(len(pts)):
                # Рисуем линию для левой стороны зуба
                f.write("  0\nLINE\n")
                f.write("  8\n %s \n" % ('gear'))  # Имя слоя
                if i == 0:
                    # Для первой линии не имеет смысла соединять с предыдущей
                    f.write(" 10\n%f\n" % pts[i][0][0])
                    f.write(" 20\n%f\n" % pts[i][0][1])
                else:
                    f.write(" 10\n%f\n" % pts[i - 1][0][0])
                    f.write(" 20\n%f\n" % pts[i - 1][0][1])
                f.write(" 11\n%f\n" % pts[i][0][0])
                f.write(" 21\n%f\n" % pts[i][0][1])

                # Рисуем линию для правой стороны зуба
                f.write("  0\nLINE\n")
                f.write("  8\n %s \n" % ('gear'))
                if i == 0:
                    f.write(" 10\n%f\n" % pts[i][1][0])
                    f.write(" 20\n%f\n" % pts[i][1][1])
                else:
                    f.write(" 10\n%f\n" % pts[i - 1][1][0])
                    f.write(" 20\n%f\n" % pts[i - 1][1][1])
                f.write(" 11\n%f\n" % pts[i][1][0])
                f.write(" 21\n%f\n" % pts[i][1][1])

            # Сохраняем первые две точки для соединения зубьев
            teeth_ends.append((pts[0][0][0], pts[0][0][1], pts[0][1][0], pts[0][1][1],))

            # Соединяем последние две точки вершины зуба
            f.write("  0\nLINE\n")
            f.write("  8\n %s \n" % ('gear'))
            f.write(" 10\n%f\n" % pts[-1][0][0])
            f.write(" 20\n%f\n" % pts[-1][0][1])
            f.write(" 11\n%f\n" % pts[-1][1][0])
            f.write(" 21\n%f\n" % pts[-1][1][1])

            # Внутренняя точка на внутреннем валу
            ri = self.innerradius(d['t'])
            xi, yi = toCartesian(ri, d['t'])

            inner_pts.append((xi, yi,))

            print(n, end=' ')

            n += 1

        # Соединяем внутренний радиус
        for i in range(len(inner_pts)):
            f.write("  0\nLINE\n")
            f.write("  8\n %s \n" % ('gear'))  # Имя слоя
            if i == 0:
                f.write(" 10\n%f\n" % inner_pts[-1][0])
                f.write(" 20\n%f\n" % inner_pts[-1][1])
            else:
                f.write(" 10\n%f\n" % inner_pts[i - 1][0])
                f.write(" 20\n%f\n" % inner_pts[i - 1][1])
            f.write(" 11\n%f\n" % inner_pts[i][0])
            f.write(" 21\n%f\n" % inner_pts[i][1])

        # Соединяем зубья
        for i in range(len(teeth_ends)):
            f.write("  0\nLINE\n")
            f.write("  8\n %s \n" % ('gear'))  # Имя слоя
            if i == 0:
                f.write(" 10\n%f\n" % teeth_ends[-1][0])
                f.write(" 20\n%f\n" % teeth_ends[-1][1])
            else:
                f.write(" 10\n%f\n" % teeth_ends[i - 1][0])
                f.write(" 20\n%f\n" % teeth_ends[i - 1][1])
            f.write(" 11\n%f\n" % teeth_ends[i][2])
            f.write(" 21\n%f\n" % teeth_ends[i][3])

    def preamble(self, f):
        """
        Записывает преамбулу в файл DXF.

        :param f: Файл для записи.
        """
        f.write("  999\nDXF создан с помощью gearsgen.py phill baker\n")
        f.write("  0\nSECTION\n")
        f.write("  2\nENTITIES\n")

    def postamble(self, f):
        """
        Записывает постамбулу в файл DXF.

        :param f: Файл для записи.
        """
        f.write("  0\nENDSEC\n")
        f.write("  0\nEOF\n")

    def radiusOfCurvature(self, t):
        """
        Вычисляет радиус кривизны в точке t.

        :param t: Угол в радианах.
        :return: Радиус кривизны.
        """
        dx = self.dx(t)
        dy = self.dy(t)
        dx2 = self.dx2(t)
        dy2 = self.dy2(t)

        return ((dx * dx + dy * dy) ** 1.5) / (dx * dy2 - dx2 * dy)

    def calcPoints(self):
        """
        Вычисляет точки для зубьев шестерни с учётом заданной точности.
        """
        refinement = 1
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
                # Добавляем расстояние от последней точки
                ccd += sqrt((x - lx) ** 2 + (y - ly) ** 2)
                if (ccd >= halfpitch and actualTeeth < halfteethCount):
                    # Добавляем новый набор точек
                    actualTeeth += 1
                    ccd = 0.0

                lx = x
                ly = y

            print("refinement", refinement, ",", "half-teeth =", actualTeeth, "extra = ", ccd, "c pitch = ", halfpitch * 2.0)
            # Проверяем, достигли ли нужного количества зубьев с допустимым отклонением
            if halfteethCount == actualTeeth and (abs(ccd - halfpitch) < self.tolerance * 5):
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

        # Вычисляем финальную доработку и сохраняем данные
        ccd = 0.0
        theta = 0.0
        ro = self.outerradius(theta) - self.dedendumd

        lx = ro * cos(theta)
        ly = ro * sin(theta)

        rc = self.radiusOfCurvature(theta)

        self.teethLoc = [{
            'x': lx, 'y': ly, 'r': ro, 't': 0.0, 
            'rc': rc, 
            'dx': self.dx(0.0), 'dy': self.dy(0.0), 
            'dx2': self.dx2(0.0), 'dy2': self.dy2(0.0)
        }]
        self.gapLoc = []
        gapFlag = 1

        print("вычисление точек для финальной доработки")

        actualTeeth = 1

        while actualTeeth < halfteethCount:
            theta += self.tolerance
            ro = self.outerradius(theta) - self.dedendumd
            x = ro * cos(theta)
            y = ro * sin(theta)
            # Добавляем расстояние от последней точки
            ccd = sqrt((x - lx) ** 2 + (y - ly) ** 2)
            if (ccd >= halfpitch):
                # Добавляем новый набор точек
                rc = self.radiusOfCurvature(theta)
                if gapFlag:
                    self.gapLoc.append({
                        'x': x, 'y': y, 'r': ro, 't': theta, 
                        'rc': rc, 
                        'dx': self.dx(theta), 'dy': self.dy(theta), 
                        'dx2': self.dx2(theta), 'dy2': self.dy2(theta)
                    })
                else:
                    self.teethLoc.append({
                        'x': x, 'y': y, 'r': ro, 't': theta, 
                        'rc': rc, 
                        'dx': self.dx(theta), 'dy': self.dy(theta), 
                        'dx2': self.dx2(theta), 'dy2': self.dy2(theta)
                    })

                gapFlag = not gapFlag
                lx = x
                ly = y
                actualTeeth += 1

    def calcConjugatePoints(self):
        """
        Вычисляет сопряжённые точки шестерён.
        """
        self.secondOffset = 1.2 * self.holedistance / 2.0

        print("вычисление сопряжённых точек")

        while True:
            p = self.gapLoc[0]

            r = self.holedistance - (p['r'] + 2.0 * self.dedendumd)
            t = pi - p['t']
            x, y = toCartesian(r, t)

            dx = -sin(t)
            dy = cos(t)

            self.conjugateTeethLoc = [{
                'x': x,
                'y': y,
                'r': r,
                't': t,
                'rc': p['rc'],
                'dx': dx,
                'dy': dy,
                'dx2': p['dx2'],
                'dy2': p['dy2']
            }]

            n = 1
            while n < len(self.gapLoc) * self.periodfactor + 1:
                p = self.gapLoc[n % self.teethCount]

                rp1 = self.holedistance - (p['r'] + 2.0 * self.dedendumd)
                rp2 = self.conjugateTeethLoc[n - 1]['r']

                r1 = self.gapLoc[n % self.teethCount]['r']
                r2 = self.gapLoc[(n - 1) % self.teethCount]['r']

                dt = self.gapLoc[n % self.teethCount]['t'] - self.gapLoc[(n - 1) % self.teethCount]['t']

                # Вычисление разности углов для сопряжения
                numerator = (r1 ** 2.0 + r2 ** 2.0 - 2.0 * r1 * r2 * cos(dt) - rp1 ** 2.0 - rp2 ** 2.0)
                denominator = (-2.0 * rp1 * rp2)
                # Проверка, чтобы аргумент acos был в пределах [-1, 1]
                if denominator == 0:
                    raise ValueError("Деление на ноль при вычислении acos")
                arg = numerator / denominator
                # Ограничение значения аргумента acos
                arg = max(min(arg, 1.0), -1.0)
                dtp = acos(arg)
                t = self.conjugateTeethLoc[n - 1]['t'] + dtp
                if t < 0:
                    t += 2.0 * pi
                if t > 2.0 * pi:
                    t -= 2.0 * pi

                x = cos(t) * rp1
                y = sin(t) * rp1

                dx = -sin(t)
                dy = cos(t)

                self.conjugateTeethLoc.append({
                    'x': x,
                    'y': y,
                    'r': rp1,
                    't': t,
                    'rc': p['rc'],
                    'dx': dx,
                    'dy': dy,
                    'dx2': p['dx2'],
                    'dy2': p['dy2']
                })
                n += 1

            if n < self.teethCount * self.periodfactor + 1:
                self.holedistance += self.tolerance
            elif n > self.teethCount * self.periodfactor + 1:
                self.holedistance -= self.tolerance
            else:  # должно быть равно
                gap = sqrt(
                    (self.conjugateTeethLoc[-1]['x'] - self.conjugateTeethLoc[0]['x']) ** 2 +
                    (self.conjugateTeethLoc[-1]['y'] - self.conjugateTeethLoc[0]['y']) ** 2
                )
                if gap >= self.tolerance * 10:
                    if t >= 2.0 * pi:
                        self.holedistance += self.tolerance
                    else:
                        self.holedistance -= self.tolerance
                else:
                    self.conjugateTeethLoc = self.conjugateTeethLoc[:-1]
                    break

        print("используется расстояние между отверстиями:", repr(self.holedistance))
        for n in range(len(self.conjugateTeethLoc)):
            before = n - 1
            after = n + 1

            if before < 0:
                before += len(self.conjugateTeethLoc)
            if after >= len(self.conjugateTeethLoc):
                after -= len(self.conjugateTeethLoc)
            dt = self.conjugateTeethLoc[after]['t'] - self.conjugateTeethLoc[before]['t']
            if dt < 0:
                dt += 2.0 * pi

            dx = self.conjugateTeethLoc[after]['x'] - self.conjugateTeethLoc[before]['x']
            dy = self.conjugateTeethLoc[after]['y'] - self.conjugateTeethLoc[before]['y']

            self.conjugateTeethLoc[n]['dx'] = dx
            self.conjugateTeethLoc[n]['dy'] = dy

    @staticmethod
    def teethCmp(x, y):
        """
        Сравнивает два зубца по углу t.

        :param x: Первый зубец.
        :param y: Второй зубец.
        :return: -1, 0 или 1 в зависимости от сравнения.
        """
        if x['t'] == y['t']:
            return 0
        elif x['t'] < y['t']:
            return -1
        else:
            return 1

class ConjugateSLFMakerSphereTeeth(ConjugateSLFMaker):
    """
    Класс для создания шестерён с шариковыми зубьями.
    Наследуется от ConjugateSLFMaker.
    """
    def __init__(self, teethCount, depth=0.1, tolerance=0.001):
        """
        Инициализирует экземпляр класса ConjugateSLFMakerSphereTeeth.

        :param teethCount: Количество зубьев на шестерне.
        :param depth: Глубина зуба.
        :param tolerance: Допуск для вычислений.
        """
        # Вызов конструктора родительского класса с ts=0 и period=1 (или другими подходящими значениями)
        super().__init__(teethCount=teethCount, ts=0, period=1, holedistance=1.0, depth=depth, tolerance=tolerance)

    def doShape(self, f, points, gearLetter, color):
        """
        Переопределяет метод doShape для создания шариковых зубьев.

        :param f: Файл для записи.
        :param points: Локальные координаты точек.
        :param gearLetter: Буква для обозначения шестерни.
        :param color: Цвет шестерни.
        """
        import string
        n = 0
        # Реализуйте метод согласно вашим требованиям
        pass

if __name__ == "__main__":
    # Пример создания и использования класса ConjugateSLFMaker
    teeth_count = 20  # Укажите необходимое количество зубьев
    maker = ConjugateSLFMaker(teethCount=teeth_count)
    maker.calcPoints()
    maker.calcConjugatePoints()
    maker.write("output.dxf")
    print("### ConjugateSLFMake self-test завершен")
