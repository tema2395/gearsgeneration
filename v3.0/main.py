import tkinter as tk
from tkinter import ttk, messagebox
import math
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

from gears.circular_gear import CircularGear
from gears.oval_gear import OvalGear

class NonRoundWheelApp:
    """Приложение на Tkinter для визуализации некруглых шестерён."""
    def __init__(self, master):
        self.master = master
        master.title("Генерация некруглого колеса")

        # Переменные, привязанные к элементам интерфейса
        self.teeth_var = tk.IntVar(value=20)
        self.module_var = tk.DoubleVar(value=1.0)
        self.e_var = tk.DoubleVar(value=0.15)  # эксцентриситет
        self.nodes_var = tk.IntVar(value=2)
        self.iradius_var = tk.DoubleVar(value=0.125)
        self.depth_var = tk.DoubleVar(value=0.2)
        self.is_circular_var = tk.BooleanVar(value=False)

        # Фрейм для параметров
        params_frame = ttk.Frame(master)
        params_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Метки и поля ввода для параметров шестерни
        ttk.Label(params_frame, text="Количество зубьев:").grid(row=0, column=0, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.teeth_var).grid(row=0, column=1, padx=5)

        ttk.Label(params_frame, text="Модуль (опред. размер шестерни):").grid(row=0, column=2, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.module_var).grid(row=0, column=3, padx=5)

        ttk.Label(params_frame, text="Эксцентриситет [0..1]:").grid(row=0, column=4, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.e_var).grid(row=0, column=5, padx=5)

        ttk.Label(params_frame, text="Узлы (для овальной):").grid(row=1, column=0, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.nodes_var).grid(row=1, column=1, padx=5)

        ttk.Label(params_frame, text="Внутренний радиус:").grid(row=1, column=2, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.iradius_var).grid(row=1, column=3, padx=5)

        ttk.Label(params_frame, text="Глубина зуба:").grid(row=1, column=4, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.depth_var).grid(row=1, column=5, padx=5)

        ttk.Checkbutton(params_frame, text="Круглая (e=0)", variable=self.is_circular_var).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)

        # Кнопка "Сгенерировать" для отображения шестерни
        generate_button = ttk.Button(params_frame, text="Сгенерировать", command=self.generate_plot)
        generate_button.grid(row=2, column=5, padx=10, pady=5, sticky=tk.E)

        # Создание рисунка matplotlib
        self.fig = Figure(figsize=(5,5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_aspect('equal', 'box')
        self.ax.grid(True)

        # Встраивание matplotlib в Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def generate_plot(self):
        """Обрабатывает нажатие кнопки "Сгенерировать": создает и отображает шестерню."""
        teeth = self.teeth_var.get()
        module = self.module_var.get()
        e = self.e_var.get()
        nodes = self.nodes_var.get()
        iradius = self.iradius_var.get()
        depth = self.depth_var.get()
        is_circular = self.is_circular_var.get()
        
        # Если выбрана "круглая", то e=0
        if is_circular:
            e = 0.0

        # Рассчитываем большую полуось a для овальной шестерни
        # Примерная зависимость: a = (module * teeth) / pi
        a = module * teeth / math.pi

        # Создаём шестерню. OvalGear поддерживает e=0 для круга.
        gear = OvalGear(teeth=teeth, ts=10, a=a, e=e, nodes=nodes, iradius=iradius, depth=depth, tolerance=0.001)
        gear.calc_points()
        lines = gear.get_lines()

        # Очищаем ось и рисуем контур шестерни
        self.ax.clear()
        for line in lines:
            (x1, y1), (x2, y2) = line
            self.ax.plot([x1, x2], [y1, y2], 'b-')
        
        self.ax.set_title(f"Шестерня: {teeth} зубьев, e={e}")
        self.ax.set_aspect('equal', 'box')
        self.ax.grid(True)
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = NonRoundWheelApp(root)
    root.mainloop()
