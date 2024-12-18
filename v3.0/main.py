import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from gears.conjugate_oval_gear import ConjugateOvalGearFull

class NonRoundWheelApp:
    def __init__(self, master):
        self.master = master
        master.title("Генерация некруглого колеса")

        # Параметры по умолчанию как в v0.0
        self.teeth_var = tk.IntVar(value=40)
        self.a_var = tk.DoubleVar(value=1.0)
        self.e_var = tk.DoubleVar(value=0.15)
        self.nodes_var = tk.IntVar(value=2)
        self.period_var = tk.IntVar(value=2)
        self.holedistance_var = tk.DoubleVar(value=3.0)
        self.iradius_var = tk.DoubleVar(value=0.0625)
        self.depth_var = tk.DoubleVar(value=0.25)
        self.tolerance_var = tk.DoubleVar(value=0.001)

        params_frame = ttk.Frame(master)
        params_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(params_frame, text="Teeth:").grid(row=0, column=0, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.teeth_var).grid(row=0, column=1, padx=5)

        ttk.Label(params_frame, text="a:").grid(row=0, column=2, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.a_var).grid(row=0, column=3, padx=5)

        ttk.Label(params_frame, text="e:").grid(row=0, column=4, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.e_var).grid(row=0, column=5, padx=5)

        ttk.Label(params_frame, text="nodes:").grid(row=1, column=0, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.nodes_var).grid(row=1, column=1, padx=5)

        ttk.Label(params_frame, text="period:").grid(row=1, column=2, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.period_var).grid(row=1, column=3, padx=5)

        ttk.Label(params_frame, text="holedistance:").grid(row=1, column=4, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.holedistance_var).grid(row=1, column=5, padx=5)

        ttk.Label(params_frame, text="iradius:").grid(row=2, column=0, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.iradius_var).grid(row=2, column=1, padx=5)

        ttk.Label(params_frame, text="depth:").grid(row=2, column=2, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.depth_var).grid(row=2, column=3, padx=5)

        ttk.Label(params_frame, text="tolerance:").grid(row=2, column=4, sticky=tk.E)
        ttk.Entry(params_frame, textvariable=self.tolerance_var).grid(row=2, column=5, padx=5)

        generate_button = ttk.Button(params_frame, text="Сгенерировать DXF", command=self.save_dxf)
        generate_button.grid(row=3, column=5, padx=10, pady=5, sticky=tk.E)

        show_button = ttk.Button(params_frame, text="Показать в окне", command=self.show_in_window)
        show_button.grid(row=3, column=4, padx=10, pady=5, sticky=tk.E)

        self.fig = Figure(figsize=(5,5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_aspect('equal', 'box')
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def save_dxf(self):
        gear = ConjugateOvalGearFull(
            self.teeth_var.get(),
            10,
            self.a_var.get(),
            self.e_var.get(),
            self.nodes_var.get(),
            self.period_var.get(),
            self.holedistance_var.get(),
            self.iradius_var.get(),
            self.depth_var.get(),
            self.tolerance_var.get()
        )
        gear.write('output.dxf')
        messagebox.showinfo("DXF", "DXF успешно сгенерирован: output.dxf")

    def show_in_window(self):
        gear = ConjugateOvalGearFull(
            self.teeth_var.get(),
            10,
            self.a_var.get(),
            self.e_var.get(),
            self.nodes_var.get(),
            self.period_var.get(),
            self.holedistance_var.get(),
            self.iradius_var.get(),
            self.depth_var.get(),
            self.tolerance_var.get()
        )
        gear.calcPoints()
        lines = gear.get_lines()

        self.ax.clear()
        self.ax.set_aspect('equal', 'box')
        self.ax.grid(True)
        for line in lines:
            (x1,y1),(x2,y2) = line
            self.ax.plot([x1,x2],[y1,y2],color='gray')

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = NonRoundWheelApp(root)
    root.mainloop()
