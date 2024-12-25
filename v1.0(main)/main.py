import math
import tkinter as tk
from tkinter import messagebox, filedialog
try:
    import ezdxf
except ImportError:
    pass

def generate_ellipse_gear_outline(a, b, teeth, segments_per_tooth=10, tooth_height_factor=0.1):
    """
    Генерирует список (x, y) точек, образующих замкнутый контур "эллиптической шестерни".
    
    Параметры:
    - a, b: большие и малые полуоси эллипса
    - teeth: число зубьев
    - segments_per_tooth: сколько сегментов эллипса будет между соседними зубьями
    - tooth_height_factor: насколько сильно "выпирает" зуб (доля от радиального расстояния)
    
    Идея:
    1) Всю окружность (0..2π) делим на teeth * segments_per_tooth равных кусочков.
    2) Для каждого шага вычисляем базовую точку эллипса (x0, y0).
    3) Определяем, насколько близко текущий угол к центру зуба. Центр зуба расположен
       на углах: angle_center = (i + 0.5)*2π/teeth, i=0..teeth-1.
    4) Если мы «близко» к центру зуба, расширяем точку в направлении нормали на некий процент
       (tooth_height_factor).
    5) Таким образом формируем одну замкнутую кривую без лишних «перебросов» через центр.
    """
    total_segments = teeth * segments_per_tooth
    step = 2 * math.pi / total_segments
    
    # Углы, где находятся «центры зубьев»
    tooth_centers = [(i + 0.5) * (2 * math.pi / teeth) for i in range(teeth)]
    
    # Функция для поиска ближайшего центра зуба
    def nearest_tooth_center_angle(angle):
        """
        Возвращает угол центра зуба, который ближе всего к данному angle.
        """
        # Нормируем угол в диапазон [0, 2π)
        angle = angle % (2 * math.pi)
        # Ищем ближайший центр
        return min(tooth_centers, key=lambda c: abs((c % (2*math.pi)) - angle))
    
    outline_points = []
    
    for i in range(total_segments):
        angle = i * step
        # Исходная точка на эллипсе
        x0 = a * math.cos(angle)
        y0 = b * math.sin(angle)
        
        # Радиус (от центра до эллипса)
        base_radius = math.sqrt(x0**2 + y0**2)  # длина вектора (x0, y0)
        
        # Ищем ближайший центр зуба
        center_angle = nearest_tooth_center_angle(angle)
        
        # Насколько мы «близко» к центру зуба (по углу) -- 0 означает совпадение с центром
        angle_diff = abs(center_angle - angle)
        # Но угол может "заходить" за 2π, учитываем зеркально
        angle_diff = min(angle_diff, 2*math.pi - angle_diff)
        
        # Для плавного подъёма зуба используем простую «треугольную» или «колоколообразную» функцию.
        # Чем меньше angle_diff, тем выше зуб.
        # Например, зададим ширину активной зоны зуба (в радианах):
        tooth_half_width = (math.pi*2 / teeth) / 4.0  # четверть межзубового шага
        
        if angle_diff < tooth_half_width:
            # от 0 до tooth_half_width => плавная функция (например cos)
            # max высота зуба в центре, 0 — на краях
            # здесь берём от 0..1
            ratio = math.cos(math.pi * angle_diff / tooth_half_width / 2)
            # ratio ~ 1 в центре зуба, ~ 0 на краю
            extend = tooth_height_factor * base_radius * ratio
        else:
            extend = 0
        
        # Вычисляем координату с учётом выступа зуба
        # Направление от (0,0) к (x0, y0)
        if base_radius > 1e-9:
            # нормализованный вектор
            nx, ny = x0 / base_radius, y0 / base_radius
        else:
            nx, ny = 0, 0
        
        x = x0 + nx * extend
        y = y0 + ny * extend
        
        outline_points.append((x, y))
    
    return outline_points

def shift_points(points, dx, dy):
    """Сместить набор точек на (dx, dy)."""
    return [(x + dx, y + dy) for (x, y) in points]

def save_dxf_file(gear1_points, gear2_points, filename):
    """Сохранить оба набора точек (каждое - отдельная шестерня) в один DXF-файл."""
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


class GearApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Генерация двух некруглых зубчатых колёс")
        self.geometry("700x600")

        # ==== Шестерня №1 ====
        row = 0
        tk.Label(self, text="Шестерня №1:", font=("Arial", 10, "bold")).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        row += 1

        tk.Label(self, text="Большая полуось (a1):").grid(row=row, column=0, sticky="e")
        self.entry_a1 = tk.Entry(self)
        self.entry_a1.insert(0, "100")
        self.entry_a1.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Label(self, text="Малая полуось (b1):").grid(row=row, column=0, sticky="e")
        self.entry_b1 = tk.Entry(self)
        self.entry_b1.insert(0, "60")
        self.entry_b1.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Label(self, text="Число зубьев (Z1):").grid(row=row, column=0, sticky="e")
        self.entry_teeth1 = tk.Entry(self)
        self.entry_teeth1.insert(0, "6")
        self.entry_teeth1.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # ==== Шестерня №2 ====
        tk.Label(self, text="Шестерня №2:", font=("Arial", 10, "bold")).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        row += 1

        tk.Label(self, text="Большая полуось (a2):").grid(row=row, column=0, sticky="e")
        self.entry_a2 = tk.Entry(self)
        self.entry_a2.insert(0, "80")
        self.entry_a2.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Label(self, text="Малая полуось (b2):").grid(row=row, column=0, sticky="e")
        self.entry_b2 = tk.Entry(self)
        self.entry_b2.insert(0, "50")
        self.entry_b2.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Label(self, text="Число зубьев (Z2):").grid(row=row, column=0, sticky="e")
        self.entry_teeth2 = tk.Entry(self)
        self.entry_teeth2.insert(0, "6")
        self.entry_teeth2.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # ==== Параметры зубьев (общие) ====
        tk.Label(self, text="Высота зуба (доля от радиуса):").grid(row=row, column=0, sticky="e")
        self.entry_tooth_factor = tk.Entry(self)
        self.entry_tooth_factor.insert(0, "0.1")  # 10% от радиуса
        self.entry_tooth_factor.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Label(self, text="Сегментов на один зуб (детализация):").grid(row=row, column=0, sticky="e")
        self.entry_segments_per_tooth = tk.Entry(self)
        self.entry_segments_per_tooth.insert(0, "10")
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
        """
        Генерируем и отображаем оба колеса на Canvas.
        """
        try:
            a1 = float(self.entry_a1.get())
            b1 = float(self.entry_b1.get())
            teeth1 = int(self.entry_teeth1.get())

            a2 = float(self.entry_a2.get())
            b2 = float(self.entry_b2.get())
            teeth2 = int(self.entry_teeth2.get())

            tooth_factor = float(self.entry_tooth_factor.get())
            segments_pt = int(self.entry_segments_per_tooth.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Параметры заданы неверно. Введите числа.")
            return

        # Генерация контуров (единый замкнутый контур для каждого колеса)
        self.gear1_points = generate_ellipse_gear_outline(a1, b1, teeth1, 
                                                          segments_per_tooth=segments_pt,
                                                          tooth_height_factor=tooth_factor)
        self.gear2_points = generate_ellipse_gear_outline(a2, b2, teeth2, 
                                                          segments_per_tooth=segments_pt,
                                                          tooth_height_factor=tooth_factor)
        # Смещаем вторую шестерню вправо
        # Минимально можно взять a1 + a2 + небольшой зазор
        dx = a1 + a2 + 20
        self.gear2_points = shift_points(self.gear2_points, dx, 0)

        # Рисуем оба колеса на Canvas
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
        gear_width = max_x - min_x if max_x != min_x else 1
        gear_height = max_y - min_y if max_y != min_y else 1
        scale_x = (width - 2*padding) / gear_width
        scale_y = (height - 2*padding) / gear_height
        scale = min(scale_x, scale_y)

        def transform(pt):
            x, y = pt
            # Переводим в координаты canvas (ось Y идёт вниз)
            x_t = (x - min_x) * scale + padding
            y_t = (max_y - y) * scale + padding
            return (x_t, y_t)

        # Трансформируем и рисуем многоугольники
        gear1_transformed = [transform(p) for p in self.gear1_points]
        gear2_transformed = [transform(p) for p in self.gear2_points]

        # Заливка первым цветом
        self.canvas.create_polygon(gear1_transformed, fill="#cccccc", outline="black")
        # Заливка вторым цветом
        self.canvas.create_polygon(gear2_transformed, fill="#aaaaff", outline="black")

    def generate_dxf(self):
        """
        Сохраняем оба колеса в один DXF-файл (два отдельных полилинейных контура).
        """
        if not self.gear1_points or not self.gear2_points:
            messagebox.showwarning("Внимание", "Сначала нажмите «Просмотр» для генерации колёс.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".dxf",
            filetypes=[("DXF files", "*.dxf"), ("All files", "*.*")]
        )
        if not filename:
            return  # отмена

        try:
            save_dxf_file(self.gear1_points, self.gear2_points, filename)
            messagebox.showinfo("Успех", f"Файл {filename} успешно сохранён.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    app = GearApp()
    app.mainloop()
