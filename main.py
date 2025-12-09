import tkinter as tk
from tkinter import messagebox
import math


def compute_degrees(n, a):
    deg = [0] * n
    for i in range(n):
        for j in range(n):
            if i != j:
                deg[i] += a[i][j]
        # петлі дають +2 до ступеня за кожну
        deg[i] += 2 * a[i][i]
    return deg


def dfs_connectivity(v, n, a, visited):
    visited[v] = True
    for u in range(n):
        # є ребро між v та u (для петель – a[v][v] > 0)
        if a[v][u] > 0 or (v == u and a[v][v] > 0):
            if not visited[u]:
                dfs_connectivity(u, n, a, visited)


def is_connected_ignoring_isolated(n, a, deg):
    # шукаємо першу вершину з ненульовим ступенем
    start = -1
    for i in range(n):
        if deg[i] > 0:
            start = i
            break

    if start == -1:
        # немає жодного ребра – формально вважаємо зв'язним
        return True

    visited = [False] * n
    dfs_connectivity(start, n, a, visited)

    for i in range(n):
        if deg[i] > 0 and not visited[i]:
            return False
    return True


def find_euler(n, a, deg):
    # Перевірка зв'язності
    if not is_connected_ignoring_isolated(n, a, deg):
        return "none", []

    # Вершини з непарним ступенем
    odd_vertices = [i for i in range(n) if deg[i] % 2 == 1]
    odd_count = len(odd_vertices)

    if odd_count > 2:
        return "none", []

    # Визначаємо тип (цикл/шлях) і стартову вершину
    if odd_count == 0:
        euler_type = "cycle"
        start = 0
        for i in range(n):
            if deg[i] > 0:
                start = i
                break
    else:
        euler_type = "path"
        start = odd_vertices[0]

    # Копія матриці для побудови шляху
    b = [row[:] for row in a]
    path = []

    def hierholzer(v):
        for u in range(n):
            # поки є ребра між v та u
            while b[v][u] > 0:
                if v == u:
                    # петля: знімаємо тільки раз з діагоналі
                    b[v][v] -= 1
                else:
                    # звичайне ребро: симетрично
                    b[v][u] -= 1
                    b[u][v] -= 1
                hierholzer(u)
        path.append(v)

    hierholzer(start)
    path.reverse()
    return euler_type, path


def parse_matrix(n_str, matrix_text):
    try:
        n = int(n_str.strip())
    except ValueError:
        raise ValueError("n має бути цілим числом.")

    if n <= 0:
        raise ValueError("n має бути додатнім цілим числом.")

    lines = [line.strip() for line in matrix_text.strip().splitlines() if line.strip()]
    if len(lines) != n:
        raise ValueError(f"Очікується {n} рядків матриці, отримано {len(lines)}.")

    a = []
    for idx, line in enumerate(lines):
        parts = line.split()
        if len(parts) != n:
            raise ValueError(f"У рядку {idx + 1} очікується {n} чисел, отримано {len(parts)}.")
        try:
            row = [int(x) for x in parts]
        except ValueError:
            raise ValueError(f"У рядку {idx + 1} всі елементи мають бути цілими числами.")
        if any(x < 0 for x in row):
            raise ValueError(f"Матриця суміжності не може містити від'ємних значень (рядок {idx + 1}).")
        a.append(row)

    # перевірка симетричності для неорієнтованого графа (ігноруємо петлі)
    for i in range(len(a)):
        for j in range(len(a)):
            if i != j and a[i][j] != a[j][i]:
                raise ValueError("Матриця має бути симетричною для неорієнтованого графа (a[i][j] = a[j][i]).")

    return n, a


def draw_graph(n, a, canvas):
    # Очищаємо попередній малюнок
    canvas.delete("all")

    if n == 0:
        return

    # Розміри canvas
    width = int(canvas["width"])
    height = int(canvas["height"])

    # Центр і радіус кола для розташування вершин
    cx = width // 2
    cy = height // 2
    radius = min(width, height) // 2 - 40  # відступ від країв

    # Координати вершин
    positions = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        positions.append((x, y))

    # Спочатку малюємо ребра
    # Для кратних ребер просто підписуємо їх кількість посередині
    for i in range(n):
        for j in range(i + 1, n):
            multiplicity = a[i][j]
            if multiplicity > 0:
                x1, y1 = positions[i]
                x2, y2 = positions[j]
                canvas.create_line(x1, y1, x2, y2)
                if multiplicity > 1:
                    mx = (x1 + x2) / 2
                    my = (y1 + y2) / 2
                    canvas.create_text(mx, my, text=str(multiplicity))

    # Петлі малюємо як маленькі овали біля вершини
    for i in range(n):
        loops = a[i][i]
        if loops > 0:
            x, y = positions[i]
            r = 15
            canvas.create_oval(x - r, y - 2 * r, x + r, y, outline="black")
            if loops > 1:
                canvas.create_text(x, y - 2 * r - 10, text=str(loops))

    # Потім малюємо вершини (щоб вони були поверх ребер)
    vertex_radius = 12
    for i, (x, y) in enumerate(positions):
        canvas.create_oval(
            x - vertex_radius,
            y - vertex_radius,
            x + vertex_radius,
            y + vertex_radius,
            fill="white",
            outline="black"
        )
        canvas.create_text(x, y, text=str(i + 1))  # нумерація з 1


def on_check():
    n_str = entry_n.get()
    matrix_text = text_matrix.get("1.0", tk.END)

    try:
        n, a = parse_matrix(n_str, matrix_text)
    except ValueError as e:
        messagebox.showerror("Помилка введення", str(e))
        return

    deg = compute_degrees(n, a)

    # формуємо текст результату
    result_lines = []
    result_lines.append("Ступені вершин:")
    for i in range(n):
        result_lines.append(f"Вершина {i + 1}: ступінь = {deg[i]}")

    euler_type, path = find_euler(n, a, deg)
    result_lines.append("")

    if euler_type == "none":
        result_lines.append("Граф не є ейлеровим: немає ні ейлерового циклу, ні ейлерового шляху.")
    else:
        if euler_type == "cycle":
            result_lines.append("Граф МАЄ ЕЙЛЕРІВ ЦИКЛ.")
        else:
            result_lines.append("Граф МАЄ ЕЙЛЕРІВ ШЛЯХ.")
        if path:
            path_1based = " -> ".join(str(v + 1) for v in path)
            result_lines.append("Послідовність вершин:")
            result_lines.append(path_1based)
        else:
            result_lines.append("Не вдалося побудувати шлях/цикл (path порожній).")

    text_result.config(state="normal")
    text_result.delete("1.0", tk.END)
    text_result.insert(tk.END, "\n".join(result_lines))
    text_result.config(state="disabled")

    # Малюємо граф на canvas
    draw_graph(n, a, canvas_graph)


# ----------------- ГРАФІЧНИЙ ІНТЕРФЕЙС -----------------

root = tk.Tk()
root.title("Ейлерів цикл / шлях у мультиграфі")

# Головний фрейм: ліво/право
frame_main = tk.Frame(root)
frame_main.pack(fill="both", expand=True)

# Ліва частина: ввід даних
frame_left = tk.Frame(frame_main)
frame_left.pack(side="left", padx=10, pady=10, fill="both", expand=True)

# Права частина: результат + граф
frame_right = tk.Frame(frame_main)
frame_right.pack(side="right", padx=10, pady=10, fill="both", expand=True)

# Верхній блок з n
frame_top = tk.Frame(frame_left)
frame_top.pack(pady=5, fill="x")

label_n = tk.Label(frame_top, text="Кількість вершин n:")
label_n.pack(side="left")

entry_n = tk.Entry(frame_top, width=10)
entry_n.pack(side="left", padx=5)

# Матриця суміжності
frame_matrix = tk.LabelFrame(frame_left, text="Матриця суміжності (n рядків по n чисел)")
frame_matrix.pack(pady=5, fill="both", expand=True)

text_matrix = tk.Text(frame_matrix, height=12, width=40)
text_matrix.pack(padx=5, pady=5, fill="both", expand=True)

# Кнопка
button_check = tk.Button(frame_left, text="Перевірити граф", command=on_check)
button_check.pack(pady=5)

# Результат (праворуч, зверху)
frame_result = tk.LabelFrame(frame_right, text="Результат")
frame_result.pack(pady=5, fill="both", expand=True)

text_result = tk.Text(frame_result, height=10, width=40, state="disabled")
text_result.pack(padx=5, pady=5, fill="both", expand=True)

# Canvas для малювання графа (праворуч, знизу)
frame_canvas = tk.LabelFrame(frame_right, text="Граф")
frame_canvas.pack(pady=5, fill="both", expand=True)

canvas_graph = tk.Canvas(frame_canvas, width=400, height=400, bg="white")
canvas_graph.pack(padx=5, pady=5, fill="both", expand=True)

root.mainloop()
