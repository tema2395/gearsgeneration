import math
from math import sin, cos, pi, sqrt, atan

############################
# Код из v0.0/slfmaker.py
############################

def involute(a, t):
    return [a * (sin(t) - t * cos(t)), a * (cos(t) + t * sin(t)) - a]

def normalize(x, y):
    if (x == 0.0 and y == 0.0):
        return (0.0, 0.0)
    l = sqrt(x*x + y*y)
    return (x/l, y/l)

def toCartesian(r, t):
    return (r*cos(t), r*sin(t))

def minIndex(l):
    m = l[0]
    mi = 0
    for n in range(1, len(l)):
        if l[n] < m:
            m = l[n]
            mi = n
    return mi

def findClosest(l, v):
    d = [abs(x[0] - v) for x in l]
    return l[minIndex(d)][1]

def findClosestDown(l, v):
    filtered = [x for x in l if v - x[0]>=0.0]
    if not filtered:
        raise ValueError("No elements in list satisfy v - x[0]>=0.0")
    best = filtered[0]
    bestVal = v - best[0]
    for cand in filtered:
        val = v - cand[0]
        if (val>=0 and val<=bestVal):
            best = cand
            bestVal = val
    return best[1]

############################
# Код из v0.0/conj_slfmaker.py
############################

class ConjugateSLFMaker:
    def __init__(self, teethCount, ts=5, period=2, holedistance=1.0, depth=0.1, tolerance=0.001):
        self.teethCount = teethCount
        self.toothSlices = ts
        self.period = period
        self.holedistance = holedistance
        self.depth = depth
        self.tolerance = tolerance
        self.teethLoc = []
        self.gapLoc = []
        self.conjugateTeethLoc = []
        self.generated_lines = []

    def dx(self, t):
        raise NotImplementedError
    def dy(self, t):
        raise NotImplementedError
    def dx2(self, t):
        raise NotImplementedError
    def dy2(self, t):
        raise NotImplementedError
    def outerradius(self, theta):
        raise NotImplementedError
    def innerradius(self, theta):
        raise NotImplementedError
    def perimeter(self):
        raise NotImplementedError
    def radiusOfCurvature(self, t):
        dx = self.dx(t)
        dy = self.dy(t)
        dx2 = self.dx2(t)
        dy2 = self.dy2(t)
        denom = (dx*dy2 - dx2*dy)
        if denom == 0:
            return float('inf')
        return ((dx*dx+dy*dy)**1.5)/abs(denom)

    def calcPoints(self):
        pass

    def calcConjugatePoints(self):
        pass

    def preamble(self, f):
        f.write("  999\nDXF created from gearsgen.py phill baker\n")
        f.write("  0\nSECTION\n")
        f.write("  2\nENTITIES\n")

    def postamble(self, f):
        f.write("  0\nENDSEC\n")
        f.write("  0\nEOF\n")

    def write(self, filename):
        if not self.teethLoc:
            self.calcPoints()
        if not self.conjugateTeethLoc:
            self.calcConjugatePoints()
        with open(filename, 'w') as f:
            self.preamble(f)
            self.amble(f)
            self.postamble(f)

    def amble(self, f):
        self.doShape(f, self.teethLoc, "a", "sBlu")
        self.doShape(f, self.conjugateTeethLoc, "b", "sRed")

    def doShape(self, f, teethLoc, gearLetter, color):
        inc = 0.01
        teethCount = len(teethLoc)
        n=0
        teeth_ends = []
        inner_pts = []
        points_for_line = lambda p: (p[0], p[1])

        for d in teethLoc:
            rc = abs(d['rc'])
            inverseInvoluteTableY = []
            inverseInvoluteTableX = []
            t = 0.0
            while t < pi/2.0:
                i = involute(rc, t)
                inverseInvoluteTableX.append((i[0], t))
                inverseInvoluteTableY.append((i[1], t))
                t += inc

            td = findClosest(inverseInvoluteTableY, self.dedendumd)
            tt = findClosest(inverseInvoluteTableY, self.dedendumd + self.adendumd)

            r = d['r']
            x = r*cos(d['t'])
            y = r*sin(d['t'])

            dx = d['dx']
            dy = d['dy']
            dx, dy = normalize(dx, dy)

            toothWidth = self.cpitch / 2.0
            offset = (toothWidth / 2.0) + involute(rc, td)[0]
            tx = findClosestDown(inverseInvoluteTableX, offset)
            if tt > tx:
                tt = tx

            if dy < 0:
                rot = 3.0*pi/2.0 + atan(dx/dy)
            else:
                rot = pi/2.0 + atan(dx/dy)

            tval = 0.0
            m=0
            pts=[]
            while m < self.toothSlices:
                ix, iy = involute(rc, tval)
                px = -offset + ix
                py = iy
                npx = px*cos(rot) + py*sin(rot)
                npy = px*(-sin(rot)) + py*cos(rot)
                arr = [(x+npx, y+npy,)]

                px = offset - ix
                py = iy
                npx = px*cos(rot) + py*sin(rot)
                npy = px*(-sin(rot)) + py*cos(rot)
                arr.append((x+npx,y+npy,))
                pts.append(arr)

                tval += tt/(self.toothSlices-1.0)
                m+=1

            for i in range(len(pts)):
                f.write("  0\nLINE\n")
                f.write("  8\n gear\n")
                if i==0:
                    f.write(" 10\n%f\n" % pts[i][0][0])
                    f.write(" 20\n%f\n" % pts[i][0][1])
                else:
                    f.write(" 10\n%f\n" % pts[i-1][0][0])
                    f.write(" 20\n%f\n" % pts[i-1][0][1])
                f.write(" 11\n%f\n" % pts[i][0][0])
                f.write(" 21\n%f\n" % pts[i][0][1])
                if i==0:
                    start_left = (pts[i][0][0], pts[i][0][1])
                    end_left = (pts[i][0][0], pts[i][0][1])
                else:
                    start_left = (pts[i-1][0][0], pts[i-1][0][1])
                    end_left = (pts[i][0][0], pts[i][0][1])
                self.generated_lines.append((start_left, end_left))

                f.write("  0\nLINE\n")
                f.write("  8\n gear\n")
                if i==0:
                    f.write(" 10\n%f\n" % pts[i][1][0])
                    f.write(" 20\n%f\n" % pts[i][1][1])
                else:
                    f.write(" 10\n%f\n" % pts[i-1][1][0])
                    f.write(" 20\n%f\n" % pts[i-1][1][1])
                f.write(" 11\n%f\n" % pts[i][1][0])
                f.write(" 21\n%f\n" % pts[i][1][1])
                if i==0:
                    start_right = (pts[i][1][0], pts[i][1][1])
                    end_right = (pts[i][1][0], pts[i][1][1])
                else:
                    start_right = (pts[i-1][1][0], pts[i-1][1][1])
                    end_right = (pts[i][1][0], pts[i][1][1])
                self.generated_lines.append((start_right, end_right))

            f.write("  0\nLINE\n")
            f.write("  8\n gear\n")
            f.write(" 10\n%f\n" % pts[-1][0][0])
            f.write(" 20\n%f\n" % pts[-1][0][1])
            f.write(" 11\n%f\n" % pts[-1][1][0])
            f.write(" 21\n%f\n" % pts[-1][1][1])
            self.generated_lines.append(((pts[-1][0][0], pts[-1][0][1]),(pts[-1][1][0], pts[-1][1][1])))

            ri = self.innerradius(d['t'])
            xi, yi = toCartesian(ri, d['t'])
            inner_pts.append((xi, yi,))

            teeth_ends.append((pts[0][0][0], pts[0][0][1], pts[0][1][0], pts[0][1][1],))
            n+=1

        for i in range(len(inner_pts)):
            f.write("  0\nLINE\n")
            f.write("  8\n gear\n")
            if i==0:
                f.write(" 10\n%f\n" % inner_pts[-1][0])
                f.write(" 20\n%f\n" % inner_pts[-1][1])
            else:
                f.write(" 10\n%f\n" % inner_pts[i-1][0])
                f.write(" 20\n%f\n" % inner_pts[i-1][1])
            f.write(" 11\n%f\n" % inner_pts[i][0])
            f.write(" 21\n%f\n" % inner_pts[i][1])
            if i==0:
                start_inner = (inner_pts[-1][0], inner_pts[-1][1])
                end_inner = (inner_pts[i][0], inner_pts[i][1])
            else:
                start_inner = (inner_pts[i-1][0], inner_pts[i-1][1])
                end_inner = (inner_pts[i][0], inner_pts[i][1])
            self.generated_lines.append((start_inner, end_inner))

        for i in range(len(teeth_ends)):
            f.write("  0\nLINE\n")
            f.write("  8\n gear\n")
            if i==0:
                f.write(" 10\n%f\n" % teeth_ends[-1][0])
                f.write(" 20\n%f\n" % teeth_ends[-1][1])
            else:
                f.write(" 10\n%f\n" % teeth_ends[i-1][0])
                f.write(" 20\n%f\n" % teeth_ends[i-1][1])
            f.write(" 11\n%f\n" % teeth_ends[i][2])
            f.write(" 21\n%f\n" % teeth_ends[i][3])
            if i==0:
                start_ends = (teeth_ends[-1][0], teeth_ends[-1][1])
                end_ends = (teeth_ends[i][2], teeth_ends[i][3])
            else:
                start_ends = (teeth_ends[i-1][0], teeth_ends[i-1][1])
                end_ends = (teeth_ends[i][2], teeth_ends[i][3])
            self.generated_lines.append((start_ends, end_ends))

############################
# Код из v0.0/conj_oval_gear.py
############################

class oval(ConjugateSLFMaker):
    def __init__(self, teeth, ts, a, e, nodes, period, holedistance, iradius, depth, tolerance):
        self.a = a;
        self.nodes = nodes
        self.e = e
        self.c = e*a
        self.p = a*(1.0 - self.e*self.e)
        self.b = math.sqrt(a*a - self.c*self.c)
        self.iradius = iradius
        print("Oval Gear Pair")
        print("a =", self.a, "c =", self.c, "e =", self.e)
        print("teeth =", teeth, "thickness =", depth, "inner radius =", iradius)
        super().__init__(teethCount=teeth, ts=ts, period=period, holedistance=holedistance, depth=depth, tolerance=tolerance)

    def width(self):
        return 2.0*(self.a+self.adendumd+self.dedendumd)

    def outerradius(self,theta):
        return self.p / (1.0 - self.e * cos(self.nodes*theta))

    def innerradius(self, theta):
        return self.iradius

    def dx(self, t):
        return (-self.e*self.nodes*self.p*cos(t)*sin(self.nodes*t)) / (1.0 - self.e*cos(self.nodes*t))**2 - (self.p*sin(t))/(1.0 - self.e*cos(self.nodes*t))

    def dy(self, t):
        return self.p*cos(t)/(1.0 - self.e*cos(self.nodes*t)) - (self.e*self.nodes*self.p*sin(t)*sin(self.nodes*t)) / (1.0 - self.e*cos(self.nodes*t))**2

    def dx2(self, t):
        return (2.0*self.e*self.e*self.nodes*self.nodes*self.p*cos(t)*sin(self.nodes*t)**2)/(1.0 - self.e*cos(self.nodes*t))**3 + \
               (2.0*self.e*self.nodes*self.p*sin(t)*sin(self.nodes*t)) / (1.0 - self.e*cos(self.nodes*t))**2 - \
               (self.p*cos(t))/(1.0 - self.e*cos(self.nodes*t)) - \
               (self.e*self.nodes*self.nodes*self.p*cos(t)*cos(self.nodes*t)) / (1.0 - self.e*cos(self.nodes*t))**2

    def dy2(self, t):
        return (2.0*self.e*self.e*self.nodes*self.nodes*self.p*sin(t)*sin(self.nodes*t)**2)/(1.0 - self.e*cos(self.nodes*t))**3 - \
               (2.0*self.e*self.nodes*self.p*cos(t)*sin(self.nodes*t)) / (1.0 - self.e*cos(self.nodes*t))**2 - \
               (self.p*sin(t))/(1.0 - self.e*cos(self.nodes*t)) - \
               (self.e*self.nodes*self.nodes*self.p*sin(t)*cos(self.nodes*t)) / (1.0 - self.e*cos(self.nodes*t))**2

    def perimeter(self):
        h = ((self.a-self.b)/(self.a+self.b))**2.0
        return pi * (self.a+self.b) * (1.0+(3.0 * h)/(10.0+sqrt(4.0-3.0*h)))

    def calcPoints(self):
        refinement = 1
        halfteethCount = self.teethCount * 2
        halfpitch = self.perimeter() / self.teethCount / 2.0

        while True:
            module = halfpitch * 2.0 / pi
            self.dedendumd = module * 1.25
            self.adendumd = module

            ccd = 0.0
            theta = 0.0
            ro = self.outerradius(theta) - self.dedendumd
            lx = ro*cos(0)
            ly = ro*sin(0)
            actualTeeth = 1

            while theta < 2.0 * pi:
                theta += self.tolerance
                ro = self.outerradius(theta) - self.dedendumd
                x = ro*cos(theta)
                y = ro*sin(theta)
                ccd += sqrt((x - lx)**2+(y - ly)**2)
                if (ccd >= halfpitch and actualTeeth < halfteethCount):
                    actualTeeth += 1
                    ccd = 0.0
                lx = x
                ly = y

            if halfteethCount == actualTeeth and abs(ccd - halfpitch)< self.tolerance * 5:
                break
            refinement += 1
            halfpitch = (halfpitch * actualTeeth + ccd)/(halfteethCount + 1)

        self.cpitch = halfpitch * 2.0
        module = self.cpitch / pi
        self.dedendumd = module * 1.25
        self.adendumd = module

        ccd = 0.0
        theta = 0.0
        ro = self.outerradius(theta) - self.dedendumd
        lx = ro*cos(theta)
        ly = ro*sin(theta)
        rc = self.radiusOfCurvature(theta)

        self.teethLoc = [{'x': lx,'y': ly,'r': ro,'t':0.0,'rc':rc,'dx':self.dx(0.0),'dy':self.dy(0.0),'dx2':self.dx2(0.0),'dy2':self.dy2(0.0)}]
        self.gapLoc = []
        gapFlag = True
        actualTeeth = 1

        while actualTeeth < halfteethCount:
            theta += self.tolerance
            ro = self.outerradius(theta) - self.dedendumd
            x = ro*cos(theta)
            y = ro*sin(theta)
            ccd = sqrt((x - lx)**2+(y - ly)**2)
            if (ccd >= halfpitch):
                rc = self.radiusOfCurvature(theta)
                dat = {'x': x,'y': y,'r': ro,'t':theta,'rc':rc,'dx':self.dx(theta),'dy':self.dy(theta),'dx2':self.dx2(theta),'dy2':self.dy2(theta)}
                if gapFlag:
                    self.gapLoc.append(dat)
                else:
                    self.teethLoc.append(dat)
                gapFlag = not gapFlag
                lx = x
                ly = y
                actualTeeth += 1

    def calcConjugatePoints(self):
        self.secondOffset = 1.2*self.holedistance/2.0

        while True:
            p = self.gapLoc[0]
            r = self.holedistance - (p['r'] + 2.0*self.dedendumd)
            t = pi - p['t']
            x,y = toCartesian(r,t)
            dx = -sin(t)
            dy = cos(t)
            self.conjugateTeethLoc = [{
                'x': x, 'y': y, 'r': r, 't': t,'rc': p['rc'],'dx': dx,'dy': dy,'dx2': p['dx2'],'dy2': p['dy2']
            }]

            n=1
            while n < len(self.gapLoc)*self.period + 1:
                p = self.gapLoc[n%self.teethCount]
                rp1 = self.holedistance - (p['r']+2.0*self.dedendumd)
                rp2 = self.conjugateTeethLoc[n-1]['r']

                r1 = self.gapLoc[n%self.teethCount]['r']
                r2 = self.gapLoc[(n-1)%self.teethCount]['r']

                dt = self.gapLoc[n%self.teethCount]['t'] - self.gapLoc[(n-1)%self.teethCount]['t']
                if dt<0:
                    dt+=2.0*pi

                numerator = (r1**2 + r2**2 - 2.0*r1*r2*cos(dt) - rp1**2 - rp2**2)
                denominator = (-2.0*rp1*rp2)
                if denominator==0:
                    raise ValueError("Деление на ноль при вычислении acos")
                arg = numerator/denominator
                arg = max(min(arg,1.0), -1.0)
                dtp = math.acos(arg)
                t = self.conjugateTeethLoc[n-1]['t'] + dtp
                if t<0:
                    t+=2.0*pi
                if t>2.0*pi:
                    t-=2.0*pi

                x=rp1*cos(t)
                y=rp1*sin(t)
                dx=-sin(t)
                dy=cos(t)
                self.conjugateTeethLoc.append({'x':x,'y':y,'r':rp1,'t':t,'rc':p['rc'],'dx':dx,'dy':dy,'dx2':p['dx2'],'dy2':p['dy2']})
                n+=1

            if n<self.teethCount*self.period+1:
                self.holedistance+=self.tolerance
            elif n>self.teethCount*self.period+1:
                self.holedistance-=self.tolerance
            else:
                gap = sqrt((self.conjugateTeethLoc[-1]['x'] - self.conjugateTeethLoc[0]['x'])**2+(self.conjugateTeethLoc[-1]['y'] - self.conjugateTeethLoc[0]['y'])**2)
                if gap>=self.tolerance*10:
                    if t>=2.0*pi:
                        self.holedistance+=self.tolerance
                    else:
                        self.holedistance-=self.tolerance
                else:
                    self.conjugateTeethLoc = self.conjugateTeethLoc[:-1]
                    break

        for n in range(len(self.conjugateTeethLoc)):
            before = n-1
            after = n+1
            if before<0:
                before+=len(self.conjugateTeethLoc)
            if after>=len(self.conjugateTeethLoc):
                after-=len(self.conjugateTeethLoc)
            dx = self.conjugateTeethLoc[after]['x'] - self.conjugateTeethLoc[before]['x']
            dy = self.conjugateTeethLoc[after]['y'] - self.conjugateTeethLoc[before]['y']
            self.conjugateTeethLoc[n]['dx']=dx
            self.conjugateTeethLoc[n]['dy']=dy

    def get_lines(self):
        return self.generated_lines

# В v0.0 вы вызывали:
# e = oval(40,10,1.0,0.15,2,2,3.0,0.0625,0.25,0.001)
# e.write('ncgear1.dxf')
# Это давало нужный DXF. Теперь у вас есть get_lines() для отображения.
