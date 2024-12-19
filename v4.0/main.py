import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from gear import Gear
from dxf_export import DXFExport

class GearApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор Зубчатых Колёс")

        self.teeth1_var = tk.IntVar(value=20)
        self.teeth2_var = tk.IntVar(value=30)
        self.module_var = tk.DoubleVar(value=2.0)
        self.pressure_angle_var = tk.DoubleVar(value=20.0)
        self.clearance_var = tk.DoubleVar(value=0.25)

        self.create_widgets()

    def create_widgets(self):
        params_frame = ttk.LabelFrame(self.root, text="Параметры Шестерни")
        params_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        ttk.Label(params_frame, text="Зубья шестерни 1:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.teeth1_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(params_frame, text="Зубья шестерни 2:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.teeth2_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(params_frame, text="Модуль:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.module_var).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(params_frame, text="Угол давления (°):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.pressure_angle_var).grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(params_frame, text="Свободный зазор:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.clearance_var).grid(row=4, column=1, padx=5, pady=5)

        buttons_frame = ttk.Frame(params_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(buttons_frame, text="Показать", command=self.show_gears).grid(row=0, column=0, padx=5)
        ttk.Button(buttons_frame, text="Экспортировать в DXF", command=self.export_dxf).grid(row=0, column=1, padx=5)

        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_aspect('equal', 'box')
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def show_gears(self):
        teeth1 = self.teeth1_var.get()
        teeth2 = self.teeth2_var.get()
        module = self.module_var.get()
        pressure_angle = self.pressure_angle_var.get()
        clearance = self.clearance_var.get()

        gear1 = Gear(teeth1, module, pressure_angle, clearance)
        gear2 = Gear(teeth2, module, pressure_angle, clearance)

        center_distance = gear1.pitch_radius + gear2.pitch_radius
        lines1 = gear1.generate_gear_geometry()
        lines2 = gear2.generate_gear_geometry(offset=(center_distance, 0))

        self.ax.clear()
        self.ax.grid(True)

        # Отображение линий шестерней
        for line in lines1:
            (x1, y1), (x2, y2) = line
            self.ax.plot([x1, x2], [y1, y2], color='black')

        for line in lines2:
            (x1, y1), (x2, y2) = line
            self.ax.plot([x1, x2], [y1, y2], color='black')

        max_radius = gear1.outer_radius + gear2.outer_radius + module * 2
        self.ax.set_xlim(-max_radius, max_radius)
        self.ax.set_ylim(-max_radius, max_radius)

        self.canvas.draw()



    def export_dxf(self):
        teeth1 = self.teeth1_var.get()
        teeth2 = self.teeth2_var.get()
        module = self.module_var.get()
        pressure_angle = self.pressure_angle_var.get()
        clearance = self.clearance_var.get()

        gear1 = Gear(teeth1, module, pressure_angle, clearance)
        gear2 = Gear(teeth2, module, pressure_angle, clearance)

        center_distance = gear1.pitch_radius + gear2.pitch_radius
        lines1 = gear1.generate_gear_geometry()
        lines2 = gear2.generate_gear_geometry(offset=(center_distance, 0))

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
