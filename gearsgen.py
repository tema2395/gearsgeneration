# gearsgen.py
#!/usr/bin/python

import getopt, sys
from math import *
from circular_gear import circle
from oval_gear import oval

def print_help():
    print("")
    print(f"Использование: python {sys.argv[0]} [опции]")
    print("")
    print("Опции:")
    print("  -g TYPE   Тип шестерёнки (circular, oval) (обязательно)")
    print("  -i        Генерация внутренней шестерёнки")
    print("  -n N      Количество зубьев (по умолчанию 5)")
    print("  -m U      Модуль (по умолчанию 1.0)")
    print("  -c X      Люфт (по умолчанию 0.0)")
    print("  -a X      Смещение добавления (по умолчанию 0.0)")
    print("  -p X      Питч (по умолчанию 0.0)")
    print("  -s X      Расстояние между зубьями (по умолчанию 0.0)")
    print("  -t U      Уменьшение вершины зуба (по умолчанию 0.0)")
    print("  -D U      Множитель дедендума (по умолчанию 0.5)")
    print("  -A U      Множитель адендума (по умолчанию 0.5)")
    print("  -e        Генерация только DXF-сущностей без заголовка/футера")
    print("  -l T      Имя слоя в DXF")
    print("  -x X      Смещение по оси X")
    print("  -y X      Смещение по оси Y")
    print("  -r X      Поворот шестерёнки на угол X (в градусах)")
    print("  -f T      Имя выходного файла DXF")
    print("  -h        Показать эту справку")
    print("")
    print("Примеры:")
    print(f"  python {sys.argv[0]} -g circular -n 20 -m 1.5 -f circular_gear.dxf")
    print(f"  python {sys.argv[0]} -g oval -n 30 -m 2.0 -f oval_gear.dxf")
    print("")

def parse_args():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hg:i:n:m:c:a:p:s:t:D:A:el:x:y:r:f:")
    except getopt.GetoptError:
        print_help()
        sys.exit(1)

    gear_type = None
    internal = False
    N = 5
    m = 1.0
    c = 0.0
    off_a = 0.0
    p = 0.0
    s = 0.0
    tr = 0.0
    mul_d = 0.5
    mul_a = 0.5
    e_mode = False
    layername = ""
    off_x = 0.0
    off_y = 0.0
    off_r = 0.0
    outfile = ""

    for o, a in opts:
        if o == "-h":
            print_help()
            sys.exit()
        elif o == "-g":
            gear_type = a.lower()
        elif o == "-i":
            internal = True
        elif o == "-n":
            N = int(a)
        elif o == "-m":
            m = float(a)
        elif o == "-c":
            c = float(a)
        elif o == "-a":
            off_a = float(a)
        elif o == "-p":
            p = float(a)
        elif o == "-s":
            s = float(a)
        elif o == "-t":
            tr = float(a)
        elif o == "-D":
            mul_d = float(a)
        elif o == "-A":
            mul_a = float(a)
        elif o == "-e":
            e_mode = True
        elif o == "-l":
            layername = a
        elif o == "-x":
            off_x = float(a)
        elif o == "-y":
            off_y = float(a)
        elif o == "-r":
            off_r = float(a)
        elif o == "-f":
            outfile = a

    if not gear_type:
        print("Ошибка: Тип шестерёнки не указан.")
        print_help()
        sys.exit(1)

    return {
        "gear_type": gear_type,
        "internal": internal,
        "N": N,
        "m": m,
        "c": c,
        "off_a": off_a,
        "p": p,
        "s": s,
        "tr": tr,
        "mul_d": mul_d,
        "mul_a": mul_a,
        "e_mode": e_mode,
        "layername": layername,
        "off_x": off_x,
        "off_y": off_y,
        "off_r": off_r,
        "outfile": outfile
    }

def main():
    params = parse_args()

    gear_type = params["gear_type"]
    internal = params["internal"]
    N = params["N"]
    m = params["m"]
    c = params["c"]
    off_a = params["off_a"]
    p = params["p"]
    s = params["s"]
    tr = params["tr"]
    mul_d = params["mul_d"]
    mul_a = params["mul_a"]
    e_mode = params["e_mode"]
    layername = params["layername"]
    off_x = params["off_x"]
    off_y = params["off_y"]
    off_r = params["off_r"]
    outfile = params["outfile"]

    # Выбор типа шестерёнки
    if gear_type == "circular":
        # Создание экземпляра класса circle
        oradius = m * N / 2
        iradius = 0.125  # Можно сделать параметром
        depth = 0.2       # Можно сделать параметром
        tolerance = 0.001 # Можно сделать параметром

        gear = circle(teeth=N, ts=10, oradius=oradius, iradius=iradius, depth=depth, tolerance=tolerance)
    
    elif gear_type == "oval":
        # Создание экземпляра класса oval
        a = m * N / (2 * pi)  # Пример расчёта большой полуоси
        e = 0.15              # Эксцентриситет, можно сделать параметром
        nodes = 2             # Количество узлов, можно сделать параметром
        # holedistance = 3.0    # Расстояние до отверстия, можно сделать параметром (удалено)
        iradius = 0.0625      # Внутренний радиус, можно сделать параметром
        depth = 0.25          # Глубина зуба, можно сделать параметром
        tolerance = 0.001     # Точность расчётов

        gear = oval(teeth=N, ts=10, a=a, e=e, nodes=nodes, iradius=iradius, depth=depth, tolerance=tolerance)
    
    else:
        print(f"Тип шестерёнки '{gear_type}' не поддерживается.")
        print_help()
        sys.exit(1)

    # Генерация и экспорт шестерёнки
    if outfile:
        gear.write(outfile)
    else:
        # Вызов calcPoints() перед get_lines()
        gear.calcPoints()

        # Отображение в Tkinter, если файл не указан
        import tkinter

        # Получение линий для рисования
        lines = gear.get_lines()

        if not lines:
            print("Ошибка: Не удалось получить линии для отображения.")
            sys.exit(1)

        tk = tkinter.Tk()
        tk.title("Gear Viewer")
        tk.geometry("600x600")

        canvas = tkinter.Canvas(tk, width=600, height=600, bg="white")
        canvas.pack()

        # Определение масштаба и центра
        all_x = [x for line in lines for x, y in line]
        all_y = [y for line in lines for x, y in line]
        if all_x and all_y:
            max_coord = max(max(abs(x) for x in all_x), max(abs(y) for y in all_y))
            scale = 250 / max_coord if max_coord != 0 else 1
        else:
            scale = 1
        center_x, center_y = 300, 300

        # Поворот шестерёнки
        rotated_lines = []
        angle_rad = radians(off_r)
        cos_ang = cos(angle_rad)
        sin_ang = sin(angle_rad)
        for line in lines:
            (x1, y1), (x2, y2) = line
            # Поворот
            x1_rot = x1 * cos_ang - y1 * sin_ang
            y1_rot = x1 * sin_ang + y1 * cos_ang
            x2_rot = x2 * cos_ang - y2 * sin_ang
            y2_rot = x2 * sin_ang + y2 * cos_ang
            rotated_lines.append(((x1_rot, y1_rot), (x2_rot, y2_rot)))

        # Смещение
        for line in rotated_lines:
            (x1, y1), (x2, y2) = line
            x1_shift = x1 * scale + off_x * scale + center_x
            y1_shift = -y1 * scale + off_y * scale + center_y
            x2_shift = x2 * scale + off_x * scale + center_x
            y2_shift = -y2 * scale + off_y * scale + center_y
            canvas.create_line(
                x1_shift,
                y1_shift,
                x2_shift,
                y2_shift,
                fill="blue"
            )

        tk.mainloop()

if __name__ == "__main__":
    main()
