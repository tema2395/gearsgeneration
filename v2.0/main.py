import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class NonRoundWheelApp:
    def __init__(self, master):
        self.master = master
        master.title("Генерация некруглого колеса")
        
        # Рамка с пояснениями
        desc_frame = ttk.Frame(master)
        desc_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        desc_label = ttk.Label(desc_frame, text=(
            "Полуось X: определяет ширину фигуры\n"
            "Полуось Y: определяет высоту фигуры\n"
            "Параметр формы: при n=2 – эллипс, при больших n – более угловатая форма\n\n"
            "Количество зубьев: число периодов зубчатой модуляции\n"
            "Модуль: амплитуда (величина) зубчатой модуляции"
        ))
        desc_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Рамка для параметров
        params_frame = ttk.Frame(master)
        params_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Полуось X (a)
        ttk.Label(params_frame, text="Полуось X:").grid(row=0, column=0, padx=5, pady=5, sticky='E')
        self.a_entry = ttk.Entry(params_frame)
        self.a_entry.insert(0, "1.0")
        self.a_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Полуось Y (b)
        ttk.Label(params_frame, text="Полуось Y:").grid(row=0, column=2, padx=5, pady=5, sticky='E')
        self.b_entry = ttk.Entry(params_frame)
        self.b_entry.insert(0, "1.0")
        self.b_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Параметр формы (n)
        ttk.Label(params_frame, text="Параметр формы:").grid(row=0, column=4, padx=5, pady=5, sticky='E')
        self.n_entry = ttk.Entry(params_frame)
        self.n_entry.insert(0, "2.5")
        self.n_entry.grid(row=0, column=5, padx=5, pady=5)

        # Количество зубьев
        ttk.Label(params_frame, text="Количество зубьев:").grid(row=0, column=6, padx=5, pady=5, sticky='E')
        self.teeth_entry = ttk.Entry(params_frame)
        self.teeth_entry.insert(0, "8")
        self.teeth_entry.grid(row=0, column=7, padx=5, pady=5)

        # Модуль
        ttk.Label(params_frame, text="Модуль:").grid(row=0, column=8, padx=5, pady=5, sticky='E')
        self.module_entry = ttk.Entry(params_frame)
        self.module_entry.insert(0, "0.1")
        self.module_entry.grid(row=0, column=9, padx=5, pady=5)
        
        # Кнопка "Сгенерировать"
        generate_button = ttk.Button(params_frame, text="Сгенерировать", command=self.generate_plot)
        generate_button.grid(row=0, column=10, padx=10, pady=5)
        
        # Рамка для графика
        self.fig = Figure(figsize=(5,5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Начальный пустой график
        self.ax.set_title("Некруглое колесо")
        self.ax.set_aspect('equal', 'box')
        self.ax.grid(True)
        self.canvas.draw()

    def generate_plot(self):
        a = float(self.a_entry.get())
        b = float(self.b_entry.get())
        n = float(self.n_entry.get())
        teeth_count = int(self.teeth_entry.get())
        module = float(self.module_entry.get())
        
        t = np.linspace(0, 2*np.pi, 400)
        # Базовый суперэллипс: (|x/a|)^n + (|y/b|)^n = 1
        x_base = a * np.sign(np.cos(t)) * (np.abs(np.cos(t)))**(2/n)
        y_base = b * np.sign(np.sin(t)) * (np.abs(np.sin(t)))**(2/n)
        
        # Радиальная модуляция (зубцы)
        modulation = 1 + module*np.sin(teeth_count * t)
        
        # Применяем модуляцию к координатам
        x = x_base * modulation
        y = y_base * modulation
        
        self.ax.clear()
        self.ax.plot(x, y, 'b-', linewidth=2)
        self.ax.set_title(f"a={a}, b={b}, n={n}, зубьев={teeth_count}, модуль={module}")
        self.ax.set_aspect('equal', 'box')
        self.ax.grid(True)
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = NonRoundWheelApp(root)
    root.mainloop()
