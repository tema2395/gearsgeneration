import math
import tkinter as tk
from tkinter import messagebox, filedialog

# Если не установлено, нужно: pip install ezdxf
try:
    import ezdxf
except ImportError:
    ezdxf = None

def shift_points(points, dx, dy):
    """Сместить набор точек на (dx, dy)."""
    return [(x + dx, y + dy) for (x, y) in points]

def rotate_points(points, angle_deg):
    """Повернуть набор точек вокруг (0,0) на угол angle_deg (градусы)."""
    angle = math.radians(angle_deg)
    cosA = math.cos(angle)
    sinA = math.sin(angle)
    result = []
    for (x, y) in points:
        x_rot = x*cosA - y*sinA
        y_rot = x*sinA + y*cosA
        result.append((x_rot, y_rot))
    return result

def save_dxf_file(gear1_points, gear2_points, filename):
    """Сохранить оба набора точек (каждое - отдельная шестерня) в один DXF-файл."""
    if not ezdxf:
        messagebox.showerror("Ошибка", "Библиотека ezdxf не установлена.")
        return
    try:
        doc = ezdxf.new(dxfversion='R2010')
        msp = doc.modelspace()

        # Полилиния для первого колеса
        msp.add_lwpolyline(gear1_points, close=True, dxfattribs={'color': 1})
        # Полилиния для второго колеса
        msp.add_lwpolyline(gear2_points, close=True, dxfattribs={'color': 3})

        doc.saveas(filename)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить DXF: {str(e)}")


def generate_involute_gear_outline(z, m, alpha_deg=20.0, N_profile=30):
    """
    Генерируем 2D-контур эвольвентной шестерни (спур-колеса).

    Параметры:
    - z: число зубьев
    - m: модуль
    - alpha_deg: угол зацепления (обычно 20 градусов)
    - N_profile: количество точек на одной "ветви" эвольвенты

    Возвращает:
      список (x, y) всех вершин (замкнутый или почти замкнутый) всей шестерни.
      Упрощённый профиль: эвольвента от r_f до r_a, дублируется, тиражируется z раз.
    """
    alpha = math.radians(alpha_deg)

    # 1) Основные размеры
    d = m * z            # делительный диаметр
    r = d / 2
    d_b = d * math.cos(alpha)  # базовый диаметр
    r_b = d_b / 2
    # Диаметр вершин (аддендум)
    d_a = d + 2 * m
    r_a = d_a / 2
    # Диаметр впадин (упрощённо)
    d_f = d - 2.5 * m
    r_f = max(d_f / 2, 0)  # чтоб не было отрицательного

    # 2) Определяем угол phi, при котором r(phi) = r_a
    #    r(phi) = r_b * sqrt(1 + phi^2).
    #    Решаем: r_a = r_b * sqrt(1 + phi_a^2).
    #    => (r_a / r_b)^2 = 1 + phi_a^2 => phi_a = sqrt(...)  если r_a > r_b
    if r_b < 1e-9 or r_a <= r_b:
        phi_a = 0.0
    else:
        phi_a = math.sqrt((r_a / r_b) ** 2 - 1.0)

    # Аналогично для r_f
    #    r_f = r_b * sqrt(1 + phi_f^2)
    #    => phi_f = sqrt((r_f / r_b)^2 - 1) если r_f >= r_b
    if r_f >= r_b and r_b > 1e-9:
        phi_f = math.sqrt((r_f / r_b) ** 2 - 1.0)
    else:
        # если r_f < r_b или r_b=0, эвольвента начинается с phi=0
        phi_f = 0.0

    def involute_point(phi):
        # Параметрические уравнения эвольвенты:
        # x = r_b*(cos(phi) + phi sin(phi))
        # y = r_b*(sin(phi) - phi cos(phi))
        x = r_b * (math.cos(phi) + phi * math.sin(phi))
        y = r_b * (math.sin(phi) - phi * math.cos(phi))
        return (x, y)

    # 3) Строим "верхнюю" ветвь эвольвенты от phi_f до phi_a
    upper_profile = []
    for i in range(N_profile + 1):
        t = i / N_profile
        phi_cur = phi_f + (phi_a - phi_f) * t
        upper_profile.append(involute_point(phi_cur))

    # 4) Делаем "нижнюю" ветвь (зеркало по X–оси)
    lower_profile = []
    # Разворачиваем upper_profile, чтобы идти "сверху вниз"
    for pt in reversed(upper_profile):
        x, y = pt
        lower_profile.append((x, -y))

    # Склеиваем их в одну полилинию (убирая дубликат центральной точки)
    one_tooth_pts = lower_profile + upper_profile[1:]

    # 5) Тиражируем зуб по окружности z раз
    full_gear_points = []
    tooth_angle = 2 * math.pi / z

    for k in range(z):
        angle_k = k * tooth_angle
        cosA = math.cos(angle_k)
        sinA = math.sin(angle_k)
        for (x, y) in one_tooth_pts:
            x_rot = x * cosA - y * sinA
            y_rot = x * sinA + y * cosA
            full_gear_points.append((x_rot, y_rot))

    return full_gear_points


class GearApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Генерация двух эвольвентных зубчатых колёс (зацепление)")
        self.geometry("700x600")

        row = 0
        # ==== Шестерня №1 ====
        tk.Label(self, text="Шестерня №1:", font=("Arial", 10, "bold")) \
            .grid(row=row, column=0, padx=5, pady=5, sticky="w")
        row += 1

        tk.Label(self, text="Число зубьев (Z1):").grid(row=row, column=0, sticky="e")
        self.entry_teeth1 = tk.Entry(self)
        self.entry_teeth1.insert(0, "20")  # по умолчанию 20 зубьев
        self.entry_teeth1.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Label(self, text="Модуль (m1):").grid(row=row, column=0, sticky="e")
        self.entry_mod1 = tk.Entry(self)
        self.entry_mod1.insert(0, "2")  # по умолчанию 2 мм
        self.entry_mod1.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # ==== Шестерня №2 ====
        tk.Label(self, text="Шестерня №2:", font=("Arial", 10, "bold")) \
            .grid(row=row, column=0, padx=5, pady=5, sticky="w")
        row += 1

        tk.Label(self, text="Число зубьев (Z2):").grid(row=row, column=0, sticky="e")
        self.entry_teeth2 = tk.Entry(self)
        self.entry_teeth2.insert(0, "40")
        self.entry_teeth2.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Label(self, text="Модуль (m2):").grid(row=row, column=0, sticky="e")
        self.entry_mod2 = tk.Entry(self)
        self.entry_mod2.insert(0, "2")
        self.entry_mod2.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # ==== Параметры для расчёта эвольвенты ====
        tk.Label(self, text="Сегментов на эвольвенту:").grid(row=row, column=0, sticky="e")
        self.entry_segments_per_tooth = tk.Entry(self)
        self.entry_segments_per_tooth.insert(0, "30")
        self.entry_segments_per_tooth.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # ==== Кнопки ====
        self.preview_button = tk.Button(self, text="Просмотр", command=self.preview_gears)
        self.preview_button.grid(row=row, column=0, columnspan=2, pady=5)
        row += 1

        self.generate_button = tk.Button(self, text="Генерация DXF", command=self.generate_dxf)
        self.generate_button.grid(row=row, column=0, columnspan=2, pady=5)
        row += 1

        # ==== Canvas ====
        self.canvas = tk.Canvas(self, width=650, height=300, bg="white")
        self.canvas.grid(row=row, column=0, columnspan=3, padx=10, pady=10)
        row += 1

        # Для хранения точек:
        self.gear1_points = []
        self.gear2_points = []

    def preview_gears(self):
        """Генерируем и отображаем оба колеса на Canvas так, чтобы делительные окружности касались."""
        try:
            z1 = int(self.entry_teeth1.get())
            m1 = float(self.entry_mod1.get())

            z2 = int(self.entry_teeth2.get())
            m2 = float(self.entry_mod2.get())

            segments_pt = int(self.entry_segments_per_tooth.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Параметры заданы неверно. Введите числа.")
            return

        # 1) Генерация контуров (по эвольвенте)
        self.gear1_points = generate_involute_gear_outline(z1, m1, alpha_deg=20.0,
                                                           N_profile=segments_pt)
        self.gear2_points = generate_involute_gear_outline(z2, m2, alpha_deg=20.0,
                                                           N_profile=segments_pt)

        # 2) Межцентровое расстояние (для внешнего зацепления)
        #    a = 0.5 * (d1 + d2) = 0.5 * ((m1*z1) + (m2*z2))
        #    Это позволяет делительным окружностям (диаметрам d1 и d2) касаться.
        dx = 0.5 * ((m1 * z1) + (m2 * z2))

        # Если хотим "красиво повернуть" одну из шестерён, чтобы зуб заходил во впадину,
        # можно сделать, например, gear2_points = rotate_points(self.gear2_points, some_angle)
        # Пока оставим без поворота.

        self.gear2_points = shift_points(self.gear2_points, dx, 0)

        # 3) Рисуем оба колеса на Canvas
        self.canvas.delete("all")
        all_points = self.gear1_points + self.gear2_points
        if not all_points:
            return

        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        padding = 20
        gear_width = (max_x - min_x) if max_x != min_x else 1
        gear_height = (max_y - min_y) if max_y != min_y else 1
        scale_x = (width - 2*padding) / gear_width
        scale_y = (height - 2*padding) / gear_height
        scale = min(scale_x, scale_y)

        def transform(pt):
            x, y = pt
            # Переводим в координаты canvas (ось Y идёт вниз)
            x_t = (x - min_x) * scale + padding
            y_t = (max_y - y) * scale + padding
            return (x_t, y_t)

        gear1_transformed = [transform(p) for p in self.gear1_points]
        gear2_transformed = [transform(p) for p in self.gear2_points]

        self.canvas.create_polygon(gear1_transformed, fill="#cccccc", outline="black")
        self.canvas.create_polygon(gear2_transformed, fill="#aaaaff", outline="black")

    def generate_dxf(self):
        """Сохраняем оба колеса в один DXF-файл (две отдельные полилинии)."""
        if not self.gear1_points or not self.gear2_points:
            messagebox.showwarning("Внимание", "Сначала нажмите «Просмотр» для генерации колёс.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".dxf",
            filetypes=[("DXF files", "*.dxf"), ("All files", "*.*")]
        )
        if not filename:
            return  # пользователь отменил

        try:
            save_dxf_file(self.gear1_points, self.gear2_points, filename)
            messagebox.showinfo("Успех", f"Файл {filename} успешно сохранён.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    app = GearApp()
    app.mainloop()
