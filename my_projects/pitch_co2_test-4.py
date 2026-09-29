# Импортируем библиотеку для работы с изображениями и рисования
from PIL import Image, ImageDraw, ImageFilter

# Импортируем модуль для генерации случайных чисел (случайное размещение квадратов)
import random

# Импортируем numpy для быстрого поиска самого тёмного участка изображения
import numpy as np

# Создаём словарь с ростом сотрудников (имя — ключ, рост в см — значение)
employees_height = {
    "Лана": (172),
    "Катерина": 174,
    "Олег": 188,
    "Антон К": 193,
    "Леша Я": 175,
    "Ваня К": 181,
    "Люба": 163,
    "Маша": 166,
    "Сережа": 173,
    "Дарина": 160,
    "Лада": 163,
    "Тема Е": 180,
    "Даниил": 182,
    "Яна": 169,
    "Аня": 170,
    "Дима Н": 170,
    "Артем Р": 189,
    "Никита": 176,
    "Павлик": 175,
    "Маша П": 160,
    "Ксюша К": 164,
    "Полина": 168,
    "Ярик": 180,
    "Антон Д": 177,
    "Аня По": 171,
    "Кирилл": 182,
    "Карима": 159,
    "Лилу": 165,
    "Леша Яш": 180,
    "Даня Ч": 175,
    "Илья": 180,
    "Саша П": 173,
    "Ваня Г": 168
}

# Коэффициент выброса CO2 на 1 см роста (кг в год)
CO2_COEFFICIENT = 12

# Размер холста (ширина и высота в пикселях)
CANVAS_SIZE = 5000

# Коэффициент перевода роста из см в пиксели
HEIGHT_TO_PX_SCALE = 1.86

# Минимальное расстояние между синими квадратами (в пикселях)
MIN_DISTANCE_BETWEEN_BLUE = 200

# Максимальное число попыток случайного размещения одного квадрата
MAX_PLACEMENT_ATTEMPTS = 2000

# Насколько сильно квадрат может "вылезать" за край холста (в пикселях)
EDGE_OVERFLOW_MARGIN = -110

# Цвет синих квадратов (рост сотрудника), формат RGB — это цвет передней грани куба
BLUE_COLOR = (70, 49, 235)

# Цвет серых квадратов (углеродный след), формат RGB
GRAY_COLOR = (140, 140, 140)

# Уровень непрозрачности каждого серого куба (0.2 = 20%)
GRAY_OPACITY = 0.2

# Цвет фона — белый (RGB)
BACKGROUND_COLOR = (255, 255, 255)

# Насколько глубоко "уходит" куб назад — доля от стороны квадрата (объёмность грани)
CUBE_DEPTH_RATIO = 0.35

# Цвет маркера самого тёмного места (красный, RGB)
DARK_SPOT_COLOR = (255, 0, 0)

# Размер стороны красного маркера-квадрата (в пикселях)
DARK_SPOT_SIZE = 100

# Шаг сканирования при поиске самого тёмного участка (больше — быстрее, но грубее)
DARK_SPOT_SCAN_STEP = 25

# Переводим непрозрачность (0.2) в диапазон альфа-канала (0-255)
gray_alpha = int(255 * GRAY_OPACITY)

# Создаём основной холст в режиме RGBA, фон белый и полностью непрозрачный
canvas = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), BACKGROUND_COLOR + (255,))


# Функция проверяет, что новый квадрат не ближе MIN_DISTANCE_BETWEEN_BLUE к уже размещённым синим квадратам
def has_min_distance(new_box, placed_boxes, min_distance):
    # Распаковываем координаты нового квадрата
    x1, y1, x2, y2 = new_box

    # "Раздуваем" новый квадрат на величину минимального расстояния со всех сторон
    inflated_box = (x1 - min_distance, y1 - min_distance, x2 + min_distance, y2 + min_distance)

    # Проверяем пересечение раздутого квадрата с каждым уже размещённым квадратом
    for box in placed_boxes:
        bx1, by1, bx2, by2 = box

        # Если прямоугольники пересекаются — значит, расстояние меньше требуемого
        if inflated_box[0] < bx2 and inflated_box[2] > bx1 and inflated_box[1] < by2 and inflated_box[3] > by1:
            # Возвращаем False — место занято (слишком близко)
            return False

    # Если пересечений не найдено — место подходит
    return True


# Функция осветляет цвет на заданную величину (для верхней грани куба — имитация света сверху)
def lighten_color(color, amount):
    # Распаковываем цвет на компоненты
    r, g, b = color

    # Прибавляем яркость к каждому каналу, не выходя за пределы 255
    return (min(255, r + amount), min(255, g + amount), min(255, b + amount))


# Функция затемняет цвет на заданную величину (для боковой грани куба — имитация тени сбоку)
def darken_color(color, amount):
    # Распаковываем цвет на компоненты
    r, g, b = color

    # Вычитаем яркость из каждого канала, не опускаясь ниже 0
    return (max(0, r - amount), max(0, g - amount), max(0, b - amount))


# Функция рисует три грани куба (перед, верх, бок) прямо на переданном draw-объекте
# в абсолютных координатах холста. Используется и для синих, и для серых кубов.
def draw_cube_faces(draw_obj, top_left_x, top_left_y, side, depth, base_color, alpha):
    # Вычисляем цвет верхней грани — светлее базового (имитация света сверху)
    top_color = lighten_color(base_color, 70)

    # Вычисляем цвет боковой (правой) грани — темнее базового (имитация тени сбоку)
    side_color = darken_color(base_color, 70)

    # Координаты передней грани (квадрат) в абсолютных координатах холста
    front_top_left = (top_left_x, top_left_y)
    front_top_right = (top_left_x + side, top_left_y)
    front_bottom_right = (top_left_x + side, top_left_y + side)
    front_bottom_left = (top_left_x, top_left_y + side)

    # Координаты "задних" точек — сдвинуты по диагонали вверх-вправо на depth, формируют объём
    back_top_left = (top_left_x + depth, top_left_y - depth)
    back_top_right = (top_left_x + side + depth, top_left_y - depth)
    back_bottom_right = (top_left_x + side + depth, top_left_y + side - depth)

    # Рисуем верхнюю грань куба (параллелограмм) — светлая, имитирует свет сверху
    draw_obj.polygon(
        [front_top_left, front_top_right, back_top_right, back_top_left],
        fill=top_color + (alpha,)
    )

    # Рисуем боковую (правую) грань куба (параллелограмм) — тёмная, имитирует тень сбоку
    draw_obj.polygon(
        [front_top_right, front_bottom_right, back_bottom_right, back_top_right],
        fill=side_color + (alpha,)
    )

    # Рисуем переднюю грань куба (обычный квадрат) — базовый цвет, самая освещённая сторона
    draw_obj.polygon(
        [front_top_left, front_top_right, front_bottom_right, front_bottom_left],
        fill=base_color + (alpha,)
    )


# Функция рисует объёмный куб (с тенью) вместо плоского квадрата — используется для синих кубов
def create_cube_square(side, base_color):
    # Вычисляем глубину куба (насколько "уходит" верхняя/боковая грань назад)
    depth = max(10, int(side * CUBE_DEPTH_RATIO))

    # Общий размер временного слоя — с запасом под верхнюю и боковую грань
    layer_width = side + depth
    layer_height = side + depth

    # Создаём прозрачный слой под будущий куб
    cube_layer = Image.new("RGBA", (layer_width, layer_height), (0, 0, 0, 0))

    # Создаём отдельный слой под мягкую тень от куба (для ощущения, что он стоит на поверхности)
    shadow_layer = Image.new("RGBA", (layer_width + depth, layer_height + depth), (0, 0, 0, 0))

    # Создаём объект для рисования тени
    draw_shadow = ImageDraw.Draw(shadow_layer)

    # Рисуем тёмный полупрозрачный эллипс-тень под нижней гранью куба
    draw_shadow.ellipse(
        [depth // 2, layer_height - depth // 3, layer_width + depth, layer_height + depth],
        fill=(0, 0, 0, 70)
    )

    # Размываем тень для мягкости краёв
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=max(4, depth // 3)))

    # Создаём объект для рисования на слое куба
    draw_cube = ImageDraw.Draw(cube_layer)

    # Рисуем три грани куба (перед, верх, бок) внутри локального слоя, передняя грань сдвинута вниз на depth
    draw_cube_faces(draw_cube, 0, depth, side, depth, base_color, 255)

    # Создаём итоговый слой размером с тень (побольше, чтобы куб поместился по центру)
    final_layer = Image.new("RGBA", shadow_layer.size, (0, 0, 0, 0))

    # Накладываем тень на итоговый слой
    final_layer = Image.alpha_composite(final_layer, shadow_layer)

    # Вставляем куб поверх тени (с небольшим отступом слева-сверху, чтобы тень была видна по краям)
    cube_offset = (depth // 4, depth // 4)
    final_layer.paste(cube_layer, cube_offset, cube_layer)

    # Возвращаем итоговое изображение куба с тенью, а также отступ, на который сдвинута передняя грань внутри слоя
    top_left_offset = (cube_offset[0], cube_offset[1] + depth)

    return final_layer, top_left_offset


# Функция находит координаты самого тёмного участка размером square_size x square_size на изображении
def find_darkest_square(image, square_size, step):
    # Конвертируем изображение в RGB-массив numpy (float32 для точных вычислений суммы)
    arr = np.array(image.convert("RGB"), dtype=np.float32)

    # Вычисляем яркость каждого пикселя как среднее по каналам R, G, B
    brightness = arr.mean(axis=2)

    # Получаем высоту и ширину изображения
    h, w = brightness.shape

    # Строим интегральное изображение (сумма яркости по прямоугольнику от (0,0) до (y,x))
    # Это позволяет быстро считать сумму яркости в любом окне без повторного суммирования пикселей
    integral = np.zeros((h + 1, w + 1), dtype=np.float64)
    integral[1:, 1:] = np.cumsum(np.cumsum(brightness, axis=0), axis=1)

    # Переменная для хранения минимальной найденной суммы яркости (самый тёмный участок)
    best_sum = None

    # Переменная для хранения координат левого верхнего угла самого тёмного участка
    best_pos = (0, 0)

    # Проходим по изображению с заданным шагом, проверяя яркость каждого окна square_size x square_size
    for y in range(0, h - square_size, step):
        for x in range(0, w - square_size, step):

            # Считаем сумму яркости в окне через интегральное изображение (формула площади прямоугольника)
            total = (
                integral[y + square_size, x + square_size]
                - integral[y, x + square_size]
                - integral[y + square_size, x]
                + integral[y, x]
            )

            # Если это самая тёмная сумма из найденных — запоминаем её и координаты
            if best_sum is None or total < best_sum:
                best_sum = total
                best_pos = (x, y)

    # Возвращаем координаты (x, y) левого верхнего угла самого тёмного участка
    return best_pos


# Заранее рассчитываем позиции квадратов, чтобы использовать их на разных этапах отрисовки
squares_data = []

# Список уже размещённых синих прямоугольников (для проверки расстояния)
placed_blue_boxes = []

# Проходим по каждому сотруднику и его росту, чтобы вычислить координаты квадратов
for name, height in employees_height.items():

    # Вычисляем сторону синего квадрата — переводим рост в пиксели, округляем до целого числа
    blue_side = int(height * HEIGHT_TO_PX_SCALE)

    # Флаг успешного размещения квадрата
    placed = False

    # Пытаемся найти случайное место, где квадрат не нарушит минимальное расстояние
    for attempt in range(MAX_PLACEMENT_ATTEMPTS):

        # Случайно выбираем координату X левого верхнего угла — разрешаем частичный выход за край холста
        x = random.randint(-EDGE_OVERFLOW_MARGIN, CANVAS_SIZE + EDGE_OVERFLOW_MARGIN - blue_side)

        # Случайно выбираем координату Y левого верхнего угла — разрешаем частичный выход за край холста
        y = random.randint(-EDGE_OVERFLOW_MARGIN, CANVAS_SIZE + EDGE_OVERFLOW_MARGIN - blue_side)

        # Формируем координаты прямоугольника кандидата
        candidate_box = (x, y, x + blue_side, y + blue_side)

        # Проверяем, соблюдается ли минимальное расстояние до уже размещённых квадратов
        if has_min_distance(candidate_box, placed_blue_boxes, MIN_DISTANCE_BETWEEN_BLUE):

            # Место подходит — отмечаем успешное размещение
            placed = True

            # Прекращаем попытки для этого сотрудника
            break

    # Если за все попытки не нашлось свободного места — пропускаем сотрудника с предупреждением
    if not placed:
        print(f"Не удалось разместить квадрат для {name} с соблюдением минимального расстояния")
        continue

    # Добавляем прямоугольник в список уже размещённых синих квадратов
    placed_blue_boxes.append(candidate_box)

    # Вычисляем координату X центра синего квадрата (пригодится для центрирования серого)
    center_x = x + blue_side / 2

    # Вычисляем координату Y центра синего квадрата
    center_y = y + blue_side / 2

    # Вычисляем сторону серого квадрата — рост умножаем на коэффициент CO2, делим на 2, округляем до целого
    gray_side = int((height * CO2_COEFFICIENT) / 1.45)

    # Вычисляем координату X левого верхнего угла серого квадрата (центрируем по синему)
    gray_x = center_x - gray_side / 2

    # Вычисляем координату Y левого верхнего угла серого квадрата (центрируем по синему)
    gray_y = center_y - gray_side / 2

    # Сохраняем все вычисленные данные по сотруднику для дальнейшей отрисовки
    # (координаты могут выходить за пределы холста — PIL сам обрежет лишнее при отрисовке)
    squares_data.append({
        "name": name,
        "blue_box": [x, y, x + blue_side, y + blue_side],
        "gray_box": [gray_x, gray_y, gray_x + gray_side, gray_y + gray_side],
    })

# ЭТАП 1: рисуем серые кубы (углеродный след) — каждый на своём отдельном прозрачном слое
# размером с весь холст и по очереди накладываем через alpha_composite,
# чтобы прозрачность граней визуально накапливалась там, где кубы перекрываются
for item in squares_data:

    # Достаём координаты серого квадрата (верхний левый угол — как у передней грани куба)
    gx1, gy1, gx2, gy2 = item["gray_box"]

    # Вычисляем сторону серого куба (целое число пикселей)
    gray_side = int(gx2 - gx1)

    # Пропускаем, если сторона получилась некорректной (0 или меньше)
    if gray_side <= 0:
        continue

    # Вычисляем глубину серого куба — пропорционально его стороне
    gray_depth = max(6, int(gray_side * CUBE_DEPTH_RATIO))

    # Создаём временный прозрачный слой размером с холст под один серый куб
    gray_layer = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))

    # Создаём объект для рисования на этом временном слое
    draw_gray_layer = ImageDraw.Draw(gray_layer)

    # Рисуем три грани серого куба прямо в абсолютных координатах холста
    # (координаты за краем холста PIL обрежет автоматически при финальном composite)
    draw_cube_faces(draw_gray_layer, int(gx1), int(gy1), gray_side, gray_depth, GRAY_COLOR, gray_alpha)

    # Накладываем этот слой на основной холст — прозрачность граней корректно смешивается с уже имеющимся слоем
    canvas = Image.alpha_composite(canvas, gray_layer)

# Делаем "снимок" холста сразу после отрисовки серых кубов (до синих),
# чтобы искать самое тёмное место именно среди серых кубов, не учитывая синие
gray_only_snapshot = canvas.copy()

# Находим координаты (x, y) левого верхнего угла самого тёмного участка среди серых кубов
darkest_x, darkest_y = find_darkest_square(gray_only_snapshot, DARK_SPOT_SIZE, DARK_SPOT_SCAN_STEP)

print(f"Самое тёмное место среди серых кубов найдено в координатах: ({darkest_x}, {darkest_y})")

# ЭТАП 2: рисуем объёмные синие кубы поверх всего (передняя, верхняя и боковая грани + тень)
# Проходим по каждому сотруднику ещё раз, чтобы отрисовать кубы финальным слоем
for item in squares_data:

    # Достаём координаты исходного квадрата (соответствуют передней грани куба)
    bx1, by1, bx2, by2 = item["blue_box"]

    # Вычисляем сторону квадрата (целое число)
    side = int(bx2 - bx1)

    # Пропускаем, если сторона получилась некорректной (например, 0 после обрезки)
    if side <= 0:
        continue

    # Создаём изображение куба (три грани + тень) и получаем смещение передней грани внутри изображения
    cube_image, front_offset = create_cube_square(side, BLUE_COLOR)

    # Вычисляем координаты вставки так, чтобы передняя грань куба совпала с исходным положением квадрата
    paste_x = int(bx1) - front_offset[0]
    paste_y = int(by1) - front_offset[1]

    # Вставляем куб на холст, используя его альфа-канал как маску
    canvas.paste(cube_image, (paste_x, paste_y), cube_image)

# ЭТАП 3: рисуем плоский (2D) красный квадрат-маркер в самом тёмном месте среди серых кубов
# Создаём объект для рисования поверх итогового холста
draw_marker = ImageDraw.Draw(canvas)

# Рисуем красный непрозрачный квадрат размером DARK_SPOT_SIZE x DARK_SPOT_SIZE в найденных координатах
draw_marker.rectangle(
    [darkest_x, darkest_y, darkest_x + DARK_SPOT_SIZE, darkest_y + DARK_SPOT_SIZE],
    fill=DARK_SPOT_COLOR + (255,)
)

# Конвертируем итоговое изображение обратно в RGB (убираем альфа-канал для сохранения)
result = canvas.convert("RGB")

# Сохраняем итоговое изображение в файл
result.save("co2_visualization_cube_grey_red_sq.png")

# Выводим сообщение об успешном сохранении
print("Изображение сохранено как co2_visualization_cube_grey_red_sq.png")