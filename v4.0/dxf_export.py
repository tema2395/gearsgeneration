# dxf_export.py
import ezdxf

class DXFExport:
    def __init__(self, filename="gear.dxf"):
        self.filename = filename
        self.doc = ezdxf.new(dxfversion='R2010')
        self.doc.layers.add(name='GEAR', color=7)  # Белый цвет
        self.msp = self.doc.modelspace()

    def add_lines(self, lines):
        """
        Добавляет линии в DXF файл.
        :param lines: Список линий, каждая линия представлена парой точек ((x1, y1), (x2, y2))
        """
        for line in lines:
            (x1, y1), (x2, y2) = line
            self.msp.add_line((x1, y1), (x2, y2), dxfattribs={'layer': 'GEAR'})

    def save(self):
        """
        Сохраняет DXF файл.
        """
        self.doc.saveas(self.filename)
