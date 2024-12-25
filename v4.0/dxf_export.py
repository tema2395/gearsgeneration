import ezdxf

class DXFExport:
    def __init__(self, filename="gear.dxf"):
        self.filename = filename
        self.doc = ezdxf.new(dxfversion="R2010")
        self.doc.layers.add(name="GEAR", color=7)  # белый
        self.msp = self.doc.modelspace()

    def add_lines(self, lines):
        """
        lines: список отрезков [((x1,y1),(x2,y2)), ...]
        """
        for (x1,y1),(x2,y2) in lines:
            self.msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer":"GEAR"})

    def save(self):
        self.doc.saveas(self.filename)
