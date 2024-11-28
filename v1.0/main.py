# main.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from gears.oval_gear import OvalGear 
import threading
import math


class OvalGearApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор Некруглых Шестерён")

        # Параметры по умолчанию
        self.teeth = tk.IntVar(value=10)
        self.module = tk.DoubleVar(value=1.0)
        self.eccentricity = tk.DoubleVar(value=0.3)
        self.inner_radius = tk.DoubleVar(value=0.5)
        self.depth = tk.DoubleVar(value=0.2)
        self.tolerance = tk.DoubleVar(value=0.001)
        self.nodes = tk.IntVar(value=1)  
        self.angle = tk.DoubleVar(value=0.0)

        # Флаг остановки
        self.stop_generation = False

        # Создание интерфейса
        self.create_widgets()

        # Инициализация шестерни
        self.gear = None

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Параметры шестерни
        ttk.Label(frame, text="Количество зубьев:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.teeth).grid(row=0, column=1, sticky=tk.E)

        ttk.Label(frame, text="Модуль:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.module).grid(row=1, column=1, sticky=tk.E)

        ttk.Label(frame, text="Эксцентриситет:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.eccentricity).grid(row=2, column=1, sticky=tk.E)

        ttk.Label(frame, text="Внутренний радиус:").grid(row=3, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.inner_radius).grid(row=3, column=1, sticky=tk.E)

        ttk.Label(frame, text="Глубина зуба:").grid(row=4, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.depth).grid(row=4, column=1, sticky=tk.E)

        ttk.Label(frame, text="Толеранс:").grid(row=5, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.tolerance).grid(row=5, column=1, sticky=tk.E)

        ttk.Label(frame, text="Количество узлов:").grid(row=6, column=0, sticky=tk.W)
        nodes_entry = ttk.Entry(frame, textvariable=self.nodes, state='readonly')  # Сделать поле только для чтения
        nodes_entry.grid(row=6, column=1, sticky=tk.E)
        ttk.Button(frame, text="Изменить", command=self.change_nodes).grid(row=6, column=2, sticky=tk.W)

        ttk.Label(frame, text="Угол поворота (°):").grid(row=7, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.angle).grid(row=7, column=1, sticky=tk.E)

        # Кнопки
        self.generate_button = ttk.Button(frame, text="Генерировать", command=self.start_generation)
        self.generate_button.grid(row=8, column=0, pady=10)

        self.stop_button = ttk.Button(frame, text="Стоп", command=self.stop_generation_func, state=tk.DISABLED)
        self.stop_button.grid(row=8, column=1, pady=10)

        # Индикатор прогресса
        self.progress = ttk.Progressbar(frame, mode='indeterminate')
        self.progress.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Канвас для отображения шестерни
        self.canvas = tk.Canvas(self.root, width=600, height=600, bg="white")
        self.canvas.grid(row=1, column=0, padx=10, pady=10)

    def change_nodes(self):
        # Функция для изменения количества узлов, если это необходимо
        new_value = simpledialog.askinteger("Изменить количество узлов", "Введите количество узлов (целое число ≥1):", minvalue=1)
        if new_value:
            self.nodes.set(new_value)

    def start_generation(self):
        # Валидация ввода
        if not self.validate_input():
            return

        # Блокировка кнопки генерации и активация кнопки стоп
        self.generate_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Сброс флага остановки
        self.stop_generation = False

        # Очистка канваса перед рисованием новой шестерни
        self.canvas.delete("all")

        # Запуск индикатора прогресса
        self.progress.start()

        # Запуск генерации в отдельном потоке
        threading.Thread(target=self.generate_gear_thread, daemon=True).start()

    def stop_generation_func(self):
        self.stop_generation = True
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        self.generate_button.config(state=tk.NORMAL)
        print("Генерация остановлена пользователем.")

    def validate_input(self):
        try:
            # Проверка на пустые поля
            entries = [self.teeth, self.module, self.eccentricity, self.inner_radius,
                       self.depth, self.tolerance, self.nodes, self.angle]
            entry_names = ["Количество зубьев", "Модуль", "Эксцентриситет",
                          "Внутренний радиус", "Глубина зуба", "Толеранс",
                          "Количество узлов", "Угол поворота"]
            for var, name in zip(entries, entry_names):
                if var.get() == "" or var.get() is None:
                    raise ValueError(f"Поле '{name}' не может быть пустым.")

            teeth = self.teeth.get()
            if teeth <= 0:
                raise ValueError("Количество зубьев должно быть положительным целым числом.")

            module = self.module.get()
            if module <= 0:
                raise ValueError("Модуль должен быть положительным числом.")

            eccentricity = self.eccentricity.get()
            if not (0.0 <= eccentricity <= 1.0):
                raise ValueError("Эксцентриситет должен быть в диапазоне [0, 1].")

            inner_radius = self.inner_radius.get()
            if inner_radius < 0:
                raise ValueError("Внутренний радиус не может быть отрицательным.")

            depth = self.depth.get()
            if depth < 0:
                raise ValueError("Глубина зуба не может быть отрицательной.")

            tolerance = self.tolerance.get()
            if tolerance <= 0:
                raise ValueError("Толеранс должен быть положительным числом.")

            nodes = self.nodes.get()
            if nodes < 1:
                raise ValueError("Количество узлов должно быть целым числом ≥1.")

            angle = self.angle.get()
            if not (0.0 <= angle < 360.0):
                raise ValueError("Угол поворота должен быть в диапазоне [0, 360).")

            return True

        except Exception as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return False

    def generate_gear_thread(self):
        try:
            # Получение параметров
            teeth = self.teeth.get()
            module = self.module.get()
            eccentricity = self.eccentricity.get()
            inner_radius = self.inner_radius.get()
            depth = self.depth.get()
            tolerance = self.tolerance.get()
            nodes = self.nodes.get()
            angle_deg = self.angle.get()
            angle_rad = math.radians(angle_deg)

            # Создание овальной шестерни
            self.gear = OvalGear(teeth=teeth, ts=10, a=module * teeth / math.pi, e=eccentricity, nodes=nodes,
                                 iradius=inner_radius, depth=depth, tolerance=tolerance)
            self.gear.calc_points()

            if self.stop_generation:
                print("Генерация была остановлена.")
                return

            # Получение линий шестерни
            lines = self.gear.get_lines()

            if self.stop_generation:
                print("Генерация была остановлена.")
                return

            # Определение масштаба и центра
            all_x = [x for line in lines for x, y in line]
            all_y = [y for line in lines for x, y in line]
            if all_x and all_y:
                max_coord = max(max(abs(x) for x in all_x), max(abs(y) for y in all_y))
                scale = 250 / max_coord if max_coord != 0 else 1
            else:
                scale = 1
            center_x, center_y = 300, 300

            cos_ang = math.cos(angle_rad)
            sin_ang = math.sin(angle_rad)

            # Рисование шестерни на канвасе
            for line in lines:
                if self.stop_generation:
                    print("Генерация была остановлена.")
                    return
                (x1, y1), (x2, y2) = line
                # Поворот
                x1_rot = x1 * cos_ang - y1 * sin_ang
                y1_rot = x1 * sin_ang + y1 * cos_ang
                x2_rot = x2 * cos_ang - y2 * sin_ang
                y2_rot = x2 * sin_ang + y2 * cos_ang
                # Масштабирование и смещение
                x1_shift = x1_rot * scale + center_x
                y1_shift = -y1_rot * scale + center_y
                x2_shift = x2_rot * scale + center_x
                y2_shift = -y2_rot * scale + center_y
                # Рисование линии
                self.canvas.create_line(x1_shift, y1_shift, x2_shift, y2_shift, fill="blue")

            # После рисования показать сообщение
            self.root.after(0, lambda: messagebox.showinfo("Успех", "Шестерня успешно сгенерирована."))

        except Exception as err:
            # Показать сообщение об ошибке
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Произошла ошибка при генерации шестерни:\n{err}"))
        finally:
            # Остановка индикатора прогресса и разблокировка кнопок
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.generate_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))


if __name__ == "__main__":
    root = tk.Tk()
    app = OvalGearApp(root)
    root.mainloop()
