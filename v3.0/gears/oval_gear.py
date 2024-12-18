from .base_gear import BaseGear, to_cartesian, involute, normalize, findClosest, findClosestDown
import math

class OvalGear(BaseGear):
    """
    Овальная шестерня с инволютными зубьями, интегрированная из логики v0.0.
    Реально будет строить зубья, а не просто контур.
    """

    def __init__(self, teeth, ts=10, a=1.0, e=0.15, nodes=2, iradius=0.0625, depth=0.25, tolerance=0.001):
        super().__init__(teeth_count=teeth, ts=ts, depth=depth, tolerance=tolerance, is_circular=(e==0))
        self.a = a
        self.e = e
        self.nodes = nodes
        self.iradius = iradius

        self.c = e * a
        assert 0.0 <= self.e <= 1.0
        self.p = a * (1.0 - self.e*self.e)
        self.b = math.sqrt(a*a - self.c*self.c) if e != 0 else a

        # Параметры будут подсчитаны в calc_points()
        self.teethLoc = []
        self.gapLoc = []

        self.involuteLines = []  # Здесь будем хранить все линии зубьев

    def perimeter(self):
        h = ((self.a - self.b)/(self.a+self.b))**2.0
        return math.pi * (self.a+self.b) * (1.0+(3.0*h)/(10.0+math.sqrt(4.0-3.0*h)))

    def outerradius(self,theta):
        return self.p / (1.0 - self.e * math.cos(self.nodes * theta))

    def innerradius(self, theta):
        return self.iradius

    def dx(self, t):
        return (-self.e*self.nodes*self.p*math.cos(t)*math.sin(self.nodes*t)) / (1.0 - self.e*math.cos(self.nodes*t))**2 - \
               (self.p*math.sin(t)) / (1.0 - self.e*math.cos(self.nodes*t))

    def dy(self, t):
        return self.p*math.cos(t)/(1.0 - self.e*math.cos(self.nodes*t)) - \
               (self.e*self.nodes*self.p*math.sin(t)*math.sin(self.nodes*t)) / (1.0 - self.e*math.cos(self.nodes*t))**2

    def dx2(self, t):
        return (2.0*self.e*self.e*self.nodes*self.nodes*self.p*math.cos(t)*math.sin(self.nodes*t)**2) / \
               (1.0 - self.e*math.cos(self.nodes*t))**3 + \
               (2.0*self.e*self.nodes*self.p*math.sin(t)*math.sin(self.nodes*t)) / \
               (1.0 - self.e*math.cos(self.nodes*t))**2 - \
               (self.p*math.cos(t)) / (1.0 - self.e*math.cos(self.nodes*t)) - \
               (self.e*self.nodes*self.nodes*self.p*math.cos(t)*math.cos(self.nodes*t)) / \
               (1.0 - self.e*math.cos(self.nodes*t))**2

    def dy2(self, t):
        return (2.0*self.e*self.e*self.nodes*self.nodes*self.p*math.sin(t)*math.sin(self.nodes*t)**2) / \
               (1.0 - self.e*math.cos(self.nodes*t))**3 - \
               (2.0*self.e*self.nodes*self.p*math.cos(t)*math.sin(self.nodes*t)) / \
               (1.0 - self.e*math.cos(self.nodes*t))**2 - \
               (self.p*math.sin(t)) / (1.0 - self.e*math.cos(self.nodes*t)) - \
               (self.e*self.nodes*self.nodes*self.p*math.sin(t)*math.cos(self.nodes*t)) / \
               (1.0 - self.e*math.cos(self.nodes*t))**2

    def calc_points(self):
        # Логика аналогична SLFMaker из v0.0: найти шаг зуба (cpitch), dedendumd, adendumd и пр.
        total_perim = self.perimeter()
        self.cpitch = total_perim / self.teeth_count
        halfteethCount = self.teeth_count * 2
        halfpitch = self.cpitch / 2.0
        refinement = 1

        while True:
            module = halfpitch * 2.0 / math.pi
            self.dedendumd = module * 1.25
            self.adendumd = module

            ccd = 0.0
            theta = 0.0
            ro = self.outerradius(0) - self.dedendumd
            lx = ro * math.cos(theta)
            ly = ro * math.sin(theta)

            actualTeeth = 1

            while theta < 2.0 * math.pi:
                theta += self.tolerance
                ro = self.outerradius(theta) - self.dedendumd
                x = ro * math.cos(theta)
                y = ro * math.sin(theta)
                ccd += math.sqrt((x - lx)**2 + (y - ly)**2)
                if ccd >= halfpitch and actualTeeth < halfteethCount:
                    actualTeeth += 1
                    ccd = 0.0
                lx = x
                ly = y

            if halfteethCount == actualTeeth and abs(ccd - halfpitch) < self.tolerance * 5:
                break
            refinement += 1
            halfpitch = (halfpitch * actualTeeth + ccd) / (halfteethCount + 1)

        self.cpitch = halfpitch * 2.0
        module = self.cpitch / math.pi
        self.dedendumd = module * 1.25
        self.adendumd = module

        # Финальный проход
        ccd = 0.0
        theta = 0.0
        ro = self.outerradius(theta) - self.dedendumd
        lx = ro * math.cos(theta)
        ly = ro * math.sin(theta)
        rc = self.radius_of_curvature(theta)

        self.teethLoc = [{'x': lx, 'y': ly, 'r': ro, 't': 0.0, 'rc': rc,
                          'dx': self.dx(0.0), 'dy': self.dy(0.0), 'dx2': self.dx2(0.0), 'dy2': self.dy2(0.0)}]
        self.gapLoc = []
        gapFlag = True
        actualTeeth = 1

        while actualTeeth < halfteethCount:
            theta += self.tolerance
            ro = self.outerradius(theta) - self.dedendumd
            x = ro * math.cos(theta)
            y = ro * math.sin(theta)
            dist = math.sqrt((x - lx)**2 + (y - ly)**2)
            if dist >= halfpitch:
                rc = self.radius_of_curvature(theta)
                dat = {'x': x, 'y': y, 'r': ro, 't': theta, 'rc': rc,
                       'dx': self.dx(theta), 'dy': self.dy(theta),
                       'dx2': self.dx2(theta), 'dy2': self.dy2(theta)}
                if gapFlag:
                    self.gapLoc.append(dat)
                else:
                    self.teethLoc.append(dat)
                gapFlag = not gapFlag
                lx = x
                ly = y
                actualTeeth += 1

        # Теперь у нас есть points для зубьев. Но нужны инволютные линии зуба.
        # Мы повторим логику построения зубьев, как в v0.0/slfmaker.py -> amble()/doShape()
        # Для каждого зуба используем инволюту и строим линии.

        self.build_teeth_geometry()

    def build_teeth_geometry(self):
        # Логика из v0.0: каждый зуб формируется из пары точек в teethLoc (для вершин зубьев)
        # и из инволют, рассчитываемых по радиусу кривизны.
        # В v0.0 для каждого зуба брались точки из self.teethLoc и gapLoc, считался offset, td, tt и т.д.

        # Здесь мы упрощённо повторим `doShape` из v0.0. Допустим, каждый "зуб" - это участок между двумя точками teethLoc.
        # В v0.0 между точками teethLoc делали инволютные боковые стороны.
        # Рассчёт очень сложный, скопируем основные шаги.

        inc = 0.01
        # teethLoc - точки вершин зубьев
        # Рассчитаем зуб по каждой точке teethLoc (каждая точка - вершина зуба)
        # В v0.0 зуб формировался между точками teethLoc и gapLoc чередуясь.
        # У нас teethLoc и gapLoc чередуются. teethLoc - вершины, gapLoc - впадины.
        # Попарно возьмём одну точку из teethLoc и одну из gapLoc для формирования зуба.

        # Нам нужна чёткая логика: 
        # Кол-во зубьев = self.teeth_count
        # У нас есть массивы teethLoc и gapLoc по числу зубьев, каждый задаёт точку на окружности.
        # Зуб будет между точкой teethLoc[i] и gapLoc[i] или наоборот.

        # Предположим, teethLoc - вершины зубьев, gapLoc - впадины между зубьями.
        # Значит, один зуб - это между teethLoc[i] и gapLoc[i], формируя левую и правую сторону зуба с помощью инволюты.

        for i in range(self.teeth_count):
            # Найдём соответствующую пару точек: вершина зуба - teethLoc[i], впадина - gapLoc[i].
            pt_tooth = self.teethLoc[i]
            pt_gap = self.gapLoc[i]

            # Центр и направление
            # В v0.0 рассчитывали offset, td, tt через инволютивные таблицы
            # Для упрощения возьмём код из v0.0/slfmaker.py doShape фрагментарно.

            rc = abs(pt_tooth['rc'])
            inverseInvoluteTableY = []
            inverseInvoluteTableX = []
            t = 0.0
            while t < math.pi/2.0:
                iv = involute(rc, t)
                inverseInvoluteTableX.append((iv[0], t))
                inverseInvoluteTableY.append((iv[1], t))
                t += inc

            # Находим td и tt (параметры инволюты для dedendum и addendum)
            td = findClosest(inverseInvoluteTableY, self.dedendumd)
            tt = findClosest(inverseInvoluteTableY, self.dedendumd + self.adendumd)

            # Координаты точки зуба
            x = pt_tooth['x']
            y = pt_tooth['y']
            dx = pt_tooth['dx']
            dy = pt_tooth['dy']
            dx, dy = normalize(dx, dy)

            toothWidth = self.cpitch / 2.0
            offset = (toothWidth / 2.0) + involute(rc, td)[0]

            tx = findClosestDown(inverseInvoluteTableX, offset)
            if tt > tx:
                tt = tx

            # Определим поворот для зуба
            # В v0.0 было:
            if dy < 0:
                rot = 3.0*math.pi/2.0 + math.atan(dx/dy)
            else:
                rot = math.pi/2.0 + math.atan(dx/dy)

            # Строим линии зуба с ts сегментами
            pts = []
            segments = self.tooth_slices
            t_step = tt/(segments-1)

            t_val = 0.0
            for m in range(segments):
                ix, iy = involute(rc, t_val)
                px = -offset + ix
                py = iy
                # Левая сторона зуба
                npx = px*math.cos(rot) + py*math.sin(rot)
                npy = px*(-math.sin(rot)) + py*math.cos(rot)
                left_point = (x+npx, y+npy)

                # Правая сторона зуба (симметрия)
                px = offset - ix
                py = iy
                npx = px*math.cos(rot) + py*math.sin(rot)
                npy = px*(-math.sin(rot)) + py*math.cos(rot)
                right_point = (x+npx, y+npy)

                # Сохраним линии по сторонам зуба:
                if m>0:
                    # Левые стороны
                    self.involuteLines.append((prev_left, left_point))
                    # Правые стороны
                    self.involuteLines.append((prev_right, right_point))

                prev_left = left_point
                prev_right = right_point
                t_val += t_step

            # Соединяем вершину зуба (последние точки слева и справа)
            self.involuteLines.append((prev_left, prev_right))

            # Добавим линию внутреннего радиуса
            ri = self.innerradius(pt_tooth['t'])
            xi, yi = to_cartesian(ri, pt_tooth['t'])
            # Можно соединить внутренние точки зубьев по окружности.

        # Таким образом у нас в self.involuteLines все линии зубьев.
        # Это сильно упрощённый вариант. Для полного совпадения с v0.0 придётся тщательно перенести всю логику.

    def get_lines(self):
        # Возвращаем сгенерированные линии зубьев
        return self.involuteLines
