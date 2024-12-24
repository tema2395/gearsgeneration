import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from gear import Gear
from noncircular_gear import EllipticalGear
from dxf_export import DXFExport
import math

class GearApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор Зубчатых Колёс (Circular / Non-Circular)")

        # Переменные для круговой/некруглой шестерни
        self.gear_type_var = tk.StringVar(value="circular")  # или "elliptical"
        
        self.teeth1_var = tk.IntVar(value=20)
        self.teeth2_var = tk.IntVar(value=30)
        self.module_var = tk.DoubleVar(value=2.0)
        self.pressure_angle_var = tk.DoubleVar(value=20.0)
        self.clearance_var = tk.DoubleVar(value=0.25)

        # Для эллиптического варианта
        self.ellipse_a1_var = tk.DoubleVar(value=30.0)  # полуось A для 1-го
        self.ellipse_b1_var = tk.DoubleVar(value=20.0)  # полуось B для 1-го
        self.ellipse_a2_var = tk.DoubleVar(value=40.0)  # полуось A для 2-го
        self.ellipse_b2_var = tk.DoubleVar(value=25.0)  # полуось B для 2-го

        self.create_widgets()

    def create_widgets(self):
        # Создадим фрейм для выбора типа шестерни
        type_frame = ttk.LabelFrame(self.root, text="Тип шестерни")
        type_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        ttk.Radiobutton(type_frame, text="Круговая (Circular)", 
                        variable=self.gear_type_var, value="circular").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Эллиптическая (Non-Circular)", 
                        variable=self.gear_type_var, value="elliptical").pack(side=tk.LEFT, padx=5)
        
        # Параметры
        params_frame = ttk.LabelFrame(self.root, text="Параметры шестерен")
        params_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Круговые параметры
        row = 0
        ttk.Label(params_frame, text="Зубья шестерни 1:").grid(row=row, column=0, padx=5, pady=2, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.teeth1_var).grid(row=row, column=1, padx=5, pady=2)
        row += 1

        ttk.Label(params_frame, text="Зубья шестерни 2:").grid(row=row, column=0, padx=5, pady=2, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.teeth2_var).grid(row=row, column=1, padx=5, pady=2)
        row += 1

        ttk.Label(params_frame, text="Модуль:").grid(row=row, column=0, padx=5, pady=2, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.module_var).grid(row=row, column=1, padx=5, pady=2)
        row += 1

        ttk.Label(params_frame, text="Угол давления (°):").grid(row=row, column=0, padx=5, pady=2, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.pressure_angle_var).grid(row=row, column=1, padx=5, pady=2)
        row += 1

        ttk.Label(params_frame, text="Свободный зазор:").grid(row=row, column=0, padx=5, pady=2, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.clearance_var).grid(row=row, column=1, padx=5, pady=2)
        row += 1

        # Эллиптические параметры
        # (примем, что a,b - это "полуоси" эллипса, т.е. x^2/a^2 + y^2/b^2 = 1)
        ttk.Label(params_frame, text="Эллипс шестерня1: A,B").grid(row=row, column=0, padx=5, pady=2, sticky=tk.E)
        subframe1 = ttk.Frame(params_frame)
        subframe1.grid(row=row, column=1, padx=5, pady=2)
        ttk.Entry(subframe1, textvariable=self.ellipse_a1_var, width=5).pack(side=tk.LEFT)
        ttk.Label(subframe1, text=" , ").pack(side=tk.LEFT)
        ttk.Entry(subframe1, textvariable=self.ellipse_b1_var, width=5).pack(side=tk.LEFT)
        row += 1

        ttk.Label(params_frame, text="Эллипс шестерня2: A,B").grid(row=row, column=0, padx=5, pady=2, sticky=tk.E)
        subframe2 = ttk.Frame(params_frame)
        subframe2.grid(row=row, column=1, padx=5, pady=2)
        ttk.Entry(subframe2, textvariable=self.ellipse_a2_var, width=5).pack(side=tk.LEFT)
        ttk.Label(subframe2, text=" , ").pack(side=tk.LEFT)
        ttk.Entry(subframe2, textvariable=self.ellipse_b2_var, width=5).pack(side=tk.LEFT)
        row += 1

        # Кнопки
        buttons_frame = ttk.Frame(params_frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(buttons_frame, text="Показать", command=self.show_gears).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Экспортировать в DXF", command=self.export_dxf).pack(side=tk.LEFT, padx=5)

        # График
        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_aspect('equal', 'box')
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def show_gears(self):
        gear_type = self.gear_type_var.get()
        # Читаем общие параметры
        teeth1 = self.teeth1_var.get()
        teeth2 = self.teeth2_var.get()
        module = self.module_var.get()
        pressure_angle = self.pressure_angle_var.get()
        clearance = self.clearance_var.get()

        # Создаем два объекта "шестерен"
        if gear_type == "circular":
            gear1 = Gear(teeth1, module, pressure_angle, clearance)
            gear2 = Gear(teeth2, module, pressure_angle, clearance)
            # Центр просто = сумма pitch_radius
            center_distance = gear1.pitch_radius + gear2.pitch_radius
            lines1 = gear1.generate_gear_geometry()
            lines2 = gear2.generate_gear_geometry(offset=(center_distance, 0))

        else:  # elliptical
            # Прочитаем параметры эллипса
            a1, b1 = self.ellipse_a1_var.get(), self.ellipse_b1_var.get()
            a2, b2 = self.ellipse_a2_var.get(), self.ellipse_b2_var.get()
            gear1 = EllipticalGear(teeth1, module, pressure_angle, clearance, a1, b1)
            gear2 = EllipticalGear(teeth2, module, pressure_angle, clearance, a2, b2)

            # Для наглядности разместим их рядом (условно)
            # Реальная передача "должна" иметь переменный центр, 
            # но мы упростим и просто сместим вторую на a1+b1+a2+b2, чтобы не пересекались.
            # Или же поставим их так, чтобы в точке фазы 0 они касались внешними радиусами.
            # Возьмем, например, dx = gear1.max_radius + gear2.max_radius + 10
            dx = gear1.max_radius + gear2.max_radius + 10
            lines1 = gear1.generate_gear_geometry()
            lines2 = gear2.generate_gear_geometry(offset=(dx, 0))

        # Рисуем
        self.ax.clear()
        self.ax.grid(True)
        for (x1, y1), (x2, y2) in lines1:
            self.ax.plot([x1, x2], [y1, y2], color='black')
        for (x1, y1), (x2, y2) in lines2:
            self.ax.plot([x1, x2], [y1, y2], color='black')

        # Определим границы
        all_x = [p[0] for seg in (lines1+lines2) for p in seg]
        all_y = [p[1] for seg in (lines1+lines2) for p in seg]
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        # Добавим небольшой отступ
        pad = 0.05 * (max_x - min_x + max_y - min_y)
        self.ax.set_xlim(min_x - pad, max_x + pad)
        self.ax.set_ylim(min_y - pad, max_y + pad)

        self.canvas.draw()

    def export_dxf(self):
        gear_type = self.gear_type_var.get()
        teeth1 = self.teeth1_var.get()
        teeth2 = self.teeth2_var.get()
        module = self.module_var.get()
        pressure_angle = self.pressure_angle_var.get()
        clearance = self.clearance_var.get()

        if gear_type == "circular":
            gear1 = Gear(teeth1, module, pressure_angle, clearance)
            gear2 = Gear(teeth2, module, pressure_angle, clearance)
            center_distance = gear1.pitch_radius + gear2.pitch_radius
            lines1 = gear1.generate_gear_geometry()
            lines2 = gear2.generate_gear_geometry(offset=(center_distance, 0))
        else:
            a1, b1 = self.ellipse_a1_var.get(), self.ellipse_b1_var.get()
            a2, b2 = self.ellipse_a2_var.get(), self.ellipse_b2_var.get()
            gear1 = EllipticalGear(teeth1, module, pressure_angle, clearance, a1, b1)
            gear2 = EllipticalGear(teeth2, module, pressure_angle, clearance, a2, b2)
            dx = gear1.max_radius + gear2.max_radius + 10
            lines1 = gear1.generate_gear_geometry()
            lines2 = gear2.generate_gear_geometry(offset=(dx, 0))

        dxf = DXFExport()
        dxf.add_lines(lines1 + lines2)

        file_path = filedialog.asksaveasfilename(defaultextension=".dxf",
                                                 filetypes=[("DXF files", "*.dxf")],
                                                 title="Сохранить как")
        if file_path:
            dxf.filename = file_path
            dxf.save()
            messagebox.showinfo("Успех", f"DXF файл успешно сохранён:\n{file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GearApp(root)
    root.mainloop()
