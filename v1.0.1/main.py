import math
import tkinter as tk
from tkinter import messagebox, filedialog

try:
    import ezdxf
except ImportError:
    ezdxf = None

def shift_points(points, dx, dy):
    return [(x + dx, y + dy) for (x, y) in points]

def rotate_points(points, angle_deg):
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
    if not ezdxf:
        messagebox.showerror("Ошибка", "Библиотека ezdxf не установлена.")
        return
    try:
        doc = ezdxf.new(dxfversion='R2010')
        msp = doc.modelspace()
        # Колесо 1
        msp.add_lwpolyline(gear1_points, close=True, dxfattribs={'color': 1})
        # Колесо 2
        msp.add_lwpolyline(gear2_points, close=True, dxfattribs={'color': 3})
        doc.saveas(filename)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить DXF: {str(e)}")

# =============== Генерация КРУГОВОЙ (эвольвентной) шестерни ===============
def generate_involute_gear_outline(z, m, alpha_deg=20.0, N_profile=30):
    alpha = math.radians(alpha_deg)
    d = m * z
    r_b = (d * math.cos(alpha)) / 2
    r_a = (d + 2*m) / 2
    d_f = d - 2.5*m
    r_f = max(d_f/2, 0.0)

    if r_b < 1e-9 or r_a <= r_b:
        phi_a = 0.0
    else:
        phi_a = math.sqrt((r_a / r_b)**2 - 1.0)

    if r_f >= r_b and r_b > 1e-9:
        phi_f = math.sqrt((r_f / r_b)**2 - 1.0)
    else:
        phi_f = 0.0

    def involute_point(phi):
        x = r_b * (math.cos(phi) + phi * math.sin(phi))
        y = r_b * (math.sin(phi) - phi * math.cos(phi))
        return (x, y)

    upper_profile = []
    for i in range(N_profile+1):
        t = i / N_profile
        phi_cur = phi_f + (phi_a - phi_f)*t
        upper_profile.append(involute_point(phi_cur))

    lower_profile = []
    for pt in reversed(upper_profile):
        x, y = pt
        lower_profile.append((x, -y))

    one_tooth_pts = lower_profile + upper_profile[1:]
    full_gear_points = []
    tooth_angle = 2*math.pi / z

    for k in range(z):
        angle_k = k * tooth_angle
        cosA = math.cos(angle_k)
        sinA = math.sin(angle_k)
        for (x, y) in one_tooth_pts:
            x_rot = x*cosA - y*sinA
            y_rot = x*sinA + y*cosA
            full_gear_points.append((x_rot, y_rot))

    return full_gear_points


def generate_ellipse_gear_outline(a, b, teeth, segments_per_tooth=10, tooth_height_factor=0.1):
    import math
    total_segments = teeth * segments_per_tooth
    step = 2*math.pi / total_segments

    tooth_centers = []
    for i in range(teeth):
        center_angle = (i + 0.5)*(2*math.pi / teeth)
        tooth_centers.append(center_angle)

    def nearest_tooth_center_angle(angle):
        angle_mod = angle % (2*math.pi)
        return min(tooth_centers, key=lambda c: abs((c % (2*math.pi)) - angle_mod))

    outline_points = []
    for i in range(total_segments):
        angle = i*step
        x0 = a*math.cos(angle)
        y0 = b*math.sin(angle)
        base_r = math.hypot(x0, y0)

        center_angle = nearest_tooth_center_angle(angle)
        angle_diff = abs(center_angle - angle)
        angle_diff = min(angle_diff, 2*math.pi - angle_diff)

        tooth_half_width = (2*math.pi/teeth)/4.0
        if angle_diff < tooth_half_width:
            ratio = math.cos(math.pi * angle_diff / tooth_half_width / 2)
            extend = tooth_height_factor*base_r*ratio
        else:
            extend = 0.0

        if base_r > 1e-9:
            nx, ny = x0/base_r, y0/base_r
        else:
            nx, ny = 0, 0

        x = x0 + nx*extend
        y = y0 + ny*extend
        outline_points.append((x, y))

    return outline_points

# =============== Главное окно ===============
class GearApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Круговые / Некруглые шестерни")
        self.geometry("1000x700")

        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.frame_gear1 = tk.LabelFrame(top_frame, text="Шестерня №1")
        self.frame_gear1.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)

        self.frame_gear2 = tk.LabelFrame(top_frame, text="Шестерня №2")
        self.frame_gear2.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)

        buttons_frame = tk.Frame(self)
        buttons_frame.pack(side=tk.TOP, padx=5, pady=5)

        canvas_frame = tk.Frame(self)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # ---- Шестерня №1 ----
        self.gear_type1 = tk.StringVar(value="circle")
        row1 = 0
        tk.Radiobutton(self.frame_gear1, text="Круговая (эвольв.)",
                       variable=self.gear_type1, value="circle") \
            .grid(row=row1, column=0, columnspan=2, sticky="w")
        row1 += 1
        tk.Radiobutton(self.frame_gear1, text="Эллиптическая",
                       variable=self.gear_type1, value="ellipse") \
            .grid(row=row1, column=0, columnspan=2, sticky="w")
        row1 += 1

        tk.Label(self.frame_gear1, text="(Круг) Число зубьев Z1:").grid(row=row1, column=0, sticky="e")
        self.entry_z1 = tk.Entry(self.frame_gear1); self.entry_z1.insert(0, "20")
        self.entry_z1.grid(row=row1, column=1, padx=5, pady=2)
        row1 += 1

        tk.Label(self.frame_gear1, text="(Круг) Модуль m1:").grid(row=row1, column=0, sticky="e")
        self.entry_m1 = tk.Entry(self.frame_gear1); self.entry_m1.insert(0, "2")
        self.entry_m1.grid(row=row1, column=1, padx=5, pady=2)
        row1 += 1

        tk.Label(self.frame_gear1, text="(Эллипс) Большая полуось a1:").grid(row=row1, column=0, sticky="e")
        self.entry_a1 = tk.Entry(self.frame_gear1); self.entry_a1.insert(0, "100")
        self.entry_a1.grid(row=row1, column=1, padx=5, pady=2)
        row1 += 1

        tk.Label(self.frame_gear1, text="(Эллипс) Малая полуось b1:").grid(row=row1, column=0, sticky="e")
        self.entry_b1 = tk.Entry(self.frame_gear1); self.entry_b1.insert(0, "60")
        self.entry_b1.grid(row=row1, column=1, padx=5, pady=2)
        row1 += 1

        tk.Label(self.frame_gear1, text="(Эллипс) Число зубьев Z1:").grid(row=row1, column=0, sticky="e")
        self.entry_ellipse_z1 = tk.Entry(self.frame_gear1); self.entry_ellipse_z1.insert(0, "6")
        self.entry_ellipse_z1.grid(row=row1, column=1, padx=5, pady=2)
        row1 += 1

        # ---- Шестерня №2 ----
        self.gear_type2 = tk.StringVar(value="circle")
        row2 = 0
        tk.Radiobutton(self.frame_gear2, text="Круговая (эвольв.)",
                       variable=self.gear_type2, value="circle") \
            .grid(row=row2, column=0, columnspan=2, sticky="w")
        row2 += 1
        tk.Radiobutton(self.frame_gear2, text="Эллиптическая",
                       variable=self.gear_type2, value="ellipse") \
            .grid(row=row2, column=0, columnspan=2, sticky="w")
        row2 += 1

        tk.Label(self.frame_gear2, text="(Круг) Число зубьев Z2:").grid(row=row2, column=0, sticky="e")
        self.entry_z2 = tk.Entry(self.frame_gear2); self.entry_z2.insert(0, "40")
        self.entry_z2.grid(row=row2, column=1, padx=5, pady=2)
        row2 += 1

        tk.Label(self.frame_gear2, text="(Круг) Модуль m2:").grid(row=row2, column=0, sticky="e")
        self.entry_m2 = tk.Entry(self.frame_gear2); self.entry_m2.insert(0, "2")
        self.entry_m2.grid(row=row2, column=1, padx=5, pady=2)
        row2 += 1

        tk.Label(self.frame_gear2, text="(Эллипс) Большая полуось a2:").grid(row=row2, column=0, sticky="e")
        self.entry_a2 = tk.Entry(self.frame_gear2); self.entry_a2.insert(0, "80")
        self.entry_a2.grid(row=row2, column=1, padx=5, pady=2)
        row2 += 1

        tk.Label(self.frame_gear2, text="(Эллипс) Малая полуось b2:").grid(row=row2, column=0, sticky="e")
        self.entry_b2 = tk.Entry(self.frame_gear2); self.entry_b2.insert(0, "50")
        self.entry_b2.grid(row=row2, column=1, padx=5, pady=2)
        row2 += 1

        tk.Label(self.frame_gear2, text="(Эллипс) Число зубьев Z2:").grid(row=row2, column=0, sticky="e")
        self.entry_ellipse_z2 = tk.Entry(self.frame_gear2); self.entry_ellipse_z2.insert(0, "6")
        self.entry_ellipse_z2.grid(row=row2, column=1, padx=5, pady=2)
        row2 += 1

        tk.Label(self.frame_gear2, text="(Эллипс) Высота зуба (доля):").grid(row=row2, column=0, sticky="e")
        self.entry_tooth_factor = tk.Entry(self.frame_gear2); self.entry_tooth_factor.insert(0, "0.1")
        self.entry_tooth_factor.grid(row=row2, column=1, padx=5, pady=2)
        row2 += 1

        tk.Label(self.frame_gear2, text="(Эллипс) Сегментов на 1 зуб:").grid(row=row2, column=0, sticky="e")
        self.entry_ellipse_segments = tk.Entry(self.frame_gear2); self.entry_ellipse_segments.insert(0, "10")
        self.entry_ellipse_segments.grid(row=row2, column=1, padx=5, pady=2)
        row2 += 1

        tk.Label(self.frame_gear2, text="(Круг) Сегментов на эвольв.:").grid(row=row2, column=0, sticky="e")
        self.entry_involute_segments = tk.Entry(self.frame_gear2); self.entry_involute_segments.insert(0, "30")
        self.entry_involute_segments.grid(row=row2, column=1, padx=5, pady=2)
        row2 += 1

        # Кнопки
        self.preview_button = tk.Button(buttons_frame, text="Просмотр", command=self.preview_gears)
        self.preview_button.pack(side=tk.LEFT, padx=10)
        self.generate_button = tk.Button(buttons_frame, text="Генерация DXF", command=self.generate_dxf)
        self.generate_button.pack(side=tk.LEFT, padx=10)

        # Canvas
        self.canvas = tk.Canvas(canvas_frame, width=700, height=300, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Хранение точек
        self.gear1_points = []
        self.gear2_points = []

    def preview_gears(self):
        type1 = self.gear_type1.get()
        type2 = self.gear_type2.get()

        try:
            z1_circle = int(self.entry_z1.get())
            m1_circle = float(self.entry_m1.get())
            z2_circle = int(self.entry_z2.get())
            m2_circle = float(self.entry_m2.get())
            involute_segments = int(self.entry_involute_segments.get())

            a1_ellipse = float(self.entry_a1.get())
            b1_ellipse = float(self.entry_b1.get())
            z1_ellipse = int(self.entry_ellipse_z1.get())

            a2_ellipse = float(self.entry_a2.get())
            b2_ellipse = float(self.entry_b2.get())
            z2_ellipse = int(self.entry_ellipse_z2.get())

            tooth_factor = float(self.entry_tooth_factor.get())
            ellipse_segments = int(self.entry_ellipse_segments.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные числовые параметры.")
            return

        # Генерируем контуры
        if type1 == "circle":
            self.gear1_points = generate_involute_gear_outline(
                z1_circle, m1_circle, alpha_deg=20.0, N_profile=involute_segments
            )
        else:
            self.gear1_points = generate_ellipse_gear_outline(
                a1_ellipse, b1_ellipse, z1_ellipse,
                segments_per_tooth=ellipse_segments,
                tooth_height_factor=tooth_factor
            )

        if type2 == "circle":
            self.gear2_points = generate_involute_gear_outline(
                z2_circle, m2_circle, alpha_deg=20.0, N_profile=involute_segments
            )
        else:
            self.gear2_points = generate_ellipse_gear_outline(
                a2_ellipse, b2_ellipse, z2_ellipse,
                segments_per_tooth=ellipse_segments,
                tooth_height_factor=tooth_factor
            )

        # -------- Расставляем колёса «в зацеплении» --------

        # 1) Если оба круговые — пусть делительные окружности касаются
        dx = 0.0
        if type1 == "circle" and type2 == "circle":
            d1 = m1_circle * z1_circle
            d2 = m2_circle * z2_circle
            dx = 0.5*(d1 + d2)
            # -- Для "зуб-в-выемку" сделаем небольшой поворот второй шестерни:
            tooth_angle_deg = 360.0 / z2_circle
            half_tooth_deg = tooth_angle_deg / 2.0
            # Повернём вторую колёсико (подбирайте знак "-", "+", величину)
            self.gear2_points = rotate_points(self.gear2_points, -half_tooth_deg)

        else:
            # 2) Если есть хотя бы одно эллиптическое — сделаем поменьше зазор,
            #    чтобы они "соприкасались" более-менее.
            #    Берём просто (a1 + a2), если обе эллиптические, или (r1 + r2), если одна круг.
            dist1 = 0
            if type1 == "ellipse":
                # Пусть "средний радиус" ~ (a1+b1)/2
                dist1 = (a1_ellipse + b1_ellipse)/2
            else:
                # Круг
                dist1 = (m1_circle * z1_circle)/2.0

            dist2 = 0
            if type2 == "ellipse":
                dist2 = (a2_ellipse + b2_ellipse)/2
            else:
                dist2 = (m2_circle * z2_circle)/2.0

            # делаем небольшую "скидку", чтобы чуть соприкасались
            dx = (dist1 + dist2) - 10  # подвинуть "плотнее", на 10 ед. меньше

            # Если нужно, можно тоже слегка повернуть второе колесо,
            self.gear2_points = rotate_points(self.gear2_points, -10.0)

        # Сдвигаем 2-е колесо
        self.gear2_points = shift_points(self.gear2_points, dx, 0)

        # -------------- Рисуем --------------
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
            x_t = (x - min_x)*scale + padding
            y_t = (max_y - y)*scale + padding
            return (x_t, y_t)

        gear1_t = [transform(p) for p in self.gear1_points]
        gear2_t = [transform(p) for p in self.gear2_points]

        self.canvas.create_polygon(gear1_t, fill="#cccccc", outline="black")
        self.canvas.create_polygon(gear2_t, fill="#aaaaff", outline="black")

    def generate_dxf(self):
        if not self.gear1_points or not self.gear2_points:
            messagebox.showwarning("Внимание", "Сначала нажмите «Просмотр» для генерации колёс.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".dxf",
            filetypes=[("DXF files", "*.dxf"), ("All files", "*.*")]
        )
        if not filename:
            return
        try:
            save_dxf_file(self.gear1_points, self.gear2_points, filename)
            messagebox.showinfo("Успех", f"Файл {filename} успешно сохранён.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    app = GearApp()
    app.mainloop()
