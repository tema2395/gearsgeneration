import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from elliptical_gears import EllipticalPairBuilder
from dxf_export import DXFExport

class GearApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сопряжённые Эллиптические Шестерни – Полная версия")

        # Параметры первой шестерни
        self.teeth1_var = tk.IntVar(value=20)
        self.a1_var = tk.DoubleVar(value=30)
        self.b1_var = tk.DoubleVar(value=20)

        # Параметры второй шестерни
        self.teeth2_var = tk.IntVar(value=30)
        self.a2_var = tk.DoubleVar(value=45)
        self.b2_var = tk.DoubleVar(value=25)

        # Общие параметры
        self.module_var = tk.DoubleVar(value=2.0)
        self.pressure_var = tk.DoubleVar(value=20.0)
        self.clearance_var = tk.DoubleVar(value=0.25)

        # Создадим UI
        self.create_widgets()

    def create_widgets(self):
        frame_params = ttk.LabelFrame(self.root, text="Параметры Эллиптических Шестерён")
        frame_params.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        row = 0
        # Шестерня1
        ttk.Label(frame_params, text="Шестерня1: зубьев").grid(row=row, column=0, sticky=tk.E)
        ttk.Entry(frame_params, textvariable=self.teeth1_var, width=8).grid(row=row, column=1)
        ttk.Label(frame_params, text="a1,b1").grid(row=row, column=2, sticky=tk.E)
        f1 = ttk.Frame(frame_params)
        f1.grid(row=row, column=3)
        ttk.Entry(f1, textvariable=self.a1_var, width=5).pack(side=tk.LEFT)
        ttk.Label(f1, text=",").pack(side=tk.LEFT)
        ttk.Entry(f1, textvariable=self.b1_var, width=5).pack(side=tk.LEFT)
        row+=1

        # Шестерня2
        ttk.Label(frame_params, text="Шестерня2: зубьев").grid(row=row, column=0, sticky=tk.E)
        ttk.Entry(frame_params, textvariable=self.teeth2_var, width=8).grid(row=row, column=1)
        ttk.Label(frame_params, text="a2,b2").grid(row=row, column=2, sticky=tk.E)
        f2 = ttk.Frame(frame_params)
        f2.grid(row=row, column=3)
        ttk.Entry(f2, textvariable=self.a2_var, width=5).pack(side=tk.LEFT)
        ttk.Label(f2, text=",").pack(side=tk.LEFT)
        ttk.Entry(f2, textvariable=self.b2_var, width=5).pack(side=tk.LEFT)
        row+=1

        # Общие
        ttk.Label(frame_params, text="Модуль:").grid(row=row, column=0, sticky=tk.E)
        ttk.Entry(frame_params, textvariable=self.module_var, width=8).grid(row=row, column=1)
        ttk.Label(frame_params, text="Угол давления(°):").grid(row=row, column=2, sticky=tk.E)
        ttk.Entry(frame_params, textvariable=self.pressure_var, width=5).grid(row=row, column=3)
        row+=1

        ttk.Label(frame_params, text="Зазор:").grid(row=row, column=0, sticky=tk.E)
        ttk.Entry(frame_params, textvariable=self.clearance_var, width=8).grid(row=row, column=1)
        row+=1

        btns = ttk.Frame(frame_params)
        btns.grid(row=row, column=0, columnspan=4, pady=5)
        ttk.Button(btns, text="Показать", command=self.show_gears).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Экспорт в DXF", command=self.export_dxf).pack(side=tk.LEFT, padx=5)

        self.fig = Figure(figsize=(7,6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_aspect('equal')
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def show_gears(self):
        # Считываем
        t1 = self.teeth1_var.get()
        a1,b1 = self.a1_var.get(), self.b1_var.get()
        t2 = self.teeth2_var.get()
        a2,b2 = self.a2_var.get(), self.b2_var.get()
        m  = self.module_var.get()
        pa = self.pressure_var.get()
        cl = self.clearance_var.get()

        builder = EllipticalPairBuilder(t1, a1, b1, t2, a2, b2, m, pa, cl)

        try:
            lines1, lines2 = builder.build_pair()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Сбой построения шестерён:\n{e}")
            return

        self.ax.clear()
        self.ax.grid(True)

        # рисуем
        for seg in lines1:
            (x1,y1),(x2,y2) = seg
            self.ax.plot([x1,x2],[y1,y2], color='blue')
        for seg in lines2:
            (x1,y1),(x2,y2) = seg
            self.ax.plot([x1,x2],[y1,y2], color='red')

        # определим границы
        allx = [p[0] for seg in (lines1+lines2) for p in seg]
        ally = [p[1] for seg in (lines1+lines2) for p in seg]
        if allx and ally:
            mnx, mxx = min(allx), max(allx)
            mny, mxy = min(ally), max(ally)
            dx = mxx - mnx
            dy = mxy - mny
            pad = 0.05*(dx+dy)
            self.ax.set_xlim(mnx - pad, mxx + pad)
            self.ax.set_ylim(mny - pad, mxy + pad)

        self.canvas.draw()

    def export_dxf(self):
        # Считываем
        t1 = self.teeth1_var.get()
        a1,b1 = self.a1_var.get(), self.b1_var.get()
        t2 = self.teeth2_var.get()
        a2,b2 = self.a2_var.get(), self.b2_var.get()
        m  = self.module_var.get()
        pa = self.pressure_var.get()
        cl = self.clearance_var.get()

        builder = EllipticalPairBuilder(t1, a1, b1, t2, a2, b2, m, pa, cl)
        lines1, lines2 = builder.build_pair()

        fn = filedialog.asksaveasfilename(defaultextension=".dxf",
                                          filetypes=[("DXF files","*.dxf")],
                                          title="Сохранить DXF")
        if fn:
            dxf = DXFExport(fn)
            dxf.add_lines(lines1)
            dxf.add_lines(lines2)
            dxf.save()
            messagebox.showinfo("Успех", f"DXF сохранён:\n{fn}")

if __name__=="__main__":
    root = tk.Tk()
    app = GearApp(root)
    root.mainloop()
