# Импортируем библиотеку для работы с изображениями и рисования
from PIL import Image, ImageDraw, ImageFilter

# Импортируем модуль для генерации случайных чисел (случайное размещение квадратов)
import random

# Создаём словарь с ростом сотрудников (имя — ключ, рост в см — значение)
employees_height = {
    "Лана": 172,
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
}

# Коэффициент выброса CO2 на 1 см роста (кг в год)
CO2_COEFFICIENT = 12

# Размер холста (ширина и высота в пикселях)
CANVAS_SIZE = 4000

# Коэффициент перевода роста из см в пиксели, увеличенный в 2 раза
HEIGHT_TO_PX_SCALE = 2.12

# Минимальное расстояние между синими квадратами (в пикселях)
MIN_DISTANCE_BETWEEN_BLUE = 150

# Максимальное число попыток случайного размещения одного квадрата
MAX_PLACEMENT_ATTEMPTS = 2000

# Насколько сильно квадрат может "вылезать" за край холста (в пикселях)
EDGE_OVERFLOW_MARGIN = 200

# Цвет синих квадратов (рост сотрудника), формат RGB
BLUE_COLOR = (70, 49, 235)

# Цвет серых квадратов (углеродный след), формат RGB
GRAY_COLOR = (140, 140, 140)

# Уровень непрозрачности каждого серого квадрата (95%)
GRAY_OPACITY = 0.12

# Цвет фона — белый (RGB)
BACKGROUND_COLOR = (255, 255, 255)

# Переводим непрозрачность (0.95) в диапазон альфа-канала (0-255)
gray_alpha = int(255 * GRAY_OPACITY)

# Формируем цвет серого квадрата с учётом прозрачности (RGBA)
gray_color_rgba = GRAY_COLOR + (gray_alpha,)

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


# Функция создаёт "объёмный" квадрат: мягкая тень + бевел (светлая/тёмная грань по краям)
def create_volumetric_square(side, base_color):
    # Вычисляем отступ вокруг квадрата под тень, чтобы она не обрезалась
    padding = max(15, side // 15)

    # Вычисляем смещение тени (насколько она сдвинута вниз-вправо)
    shadow_offset = max(6, side // 30)

    # Вычисляем толщину грани бевела (светлая/тёмная полоска по краю)
    bevel_thickness = max(3, side // 40)

    # Полный размер временного изображения с учётом отступа под тень
    full_size = side + padding * 2

    # Создаём итоговый прозрачный слой под квадрат
    square_layer = Image.new("RGBA", (full_size, full_size), (0, 0, 0, 0))

    # Создаём отдельный слой только под тень
    shadow_layer = Image.new("RGBA", (full_size, full_size), (0, 0, 0, 0))

    # Создаём объект для рисования тени
    draw_shadow = ImageDraw.Draw(shadow_layer)

    # Рисуем тёмный полупрозрачный прямоугольник тени, смещённый вниз-вправо
    draw_shadow.rectangle(
        [padding + shadow_offset, padding + shadow_offset,
         padding + side + shadow_offset, padding + side + shadow_offset],
        fill=(0, 0, 0, 100)
    )

    # Размываем тень гауссовым блюром для мягкости краёв
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=max(4, side // 25)))

    # Накладываем размытую тень на итоговый слой
    square_layer = Image.alpha_composite(square_layer, shadow_layer)

    # Распаковываем базовый цвет квадрата (R, G, B)
    r, g, b = base_color

    # Вычисляем светлый оттенок для верхней/левой грани (имитация блика/света)
    light_color = (min(255, r + 60), min(255, g + 60), min(255, b + 60), 255)

    # Вычисляем тёмный оттенок для нижней/правой грани (имитация тени на объекте)
    dark_color = (max(0, r - 60), max(0, g - 60), max(0, b - 60), 255)

    # Создаём объект для рисования основного квадрата и граней бевела
    draw_square = ImageDraw.Draw(square_layer)

    # Рисуем базовый непрозрачный квадрат основного цвета
    draw_square.rectangle(
        [padding, padding, padding + side, padding + side],
        fill=base_color + (255,)
    )

    # Рисуем светлую грань сверху (тонкая полоска у верхнего края квадрата)
    draw_square.rectangle(
        [padding, padding, padding + side, padding + bevel_thickness],
        fill=light_color
    )

    # Рисуем светлую грань слева (тонкая полоска у левого края квадрата)
    draw_square.rectangle(
        [padding, padding, padding + bevel_thickness, padding + side],
        fill=light_color
    )

    # Рисуем тёмную грань снизу (тонкая полоска у нижнего края квадрата)
    draw_square.rectangle(
        [padding, padding + side - bevel_thickness, padding + side, padding + side],
        fill=dark_color
    )

    # Рисуем тёмную грань справа (тонкая полоска у правого края квадрата)
    draw_square.rectangle(
        [padding + side - bevel_thickness, padding, padding + side, padding + side],
        fill=dark_color
    )

    # Возвращаем готовое изображение квадрата с тенью и бевелом, а также величину отступа
    return square_layer, padding


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
    gray_side = int((height * CO2_COEFFICIENT) / 2)

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

# ЭТАП 1: рисуем серые квадраты — каждый на своём отдельном прозрачном слое
# и по очереди накладываем на холст через alpha_composite,
# чтобы прозрачность визуально накапливалась при перекрытии квадратов
for item in squares_data:

    # Создаём временный прозрачный слой размером с холст под один серый квадрат
    gray_layer = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))

    # Создаём объект для рисования на этом временном слое
    draw_gray_layer = ImageDraw.Draw(gray_layer)

    # Рисуем один серый полупрозрачный квадрат на временном слое (координаты за краем — PIL обрежет автоматически)
    draw_gray_layer.rectangle(item["gray_box"], fill=gray_color_rgba)

    # Накладываем этот слой на основной холст — прозрачность корректно смешивается с уже имеющимся слоем
    canvas = Image.alpha_composite(canvas, gray_layer)

# ЭТАП 2: рисуем объёмные синие квадраты поверх всего (тень + бевел)
# Проходим по каждому сотруднику ещё раз, чтобы отрисовать синие квадраты финальным слоем
for item in squares_data:

    # Достаём координаты синего квадрата
    bx1, by1, bx2, by2 = item["blue_box"]

    # Вычисляем сторону квадрата (целое число)
    side = int(bx2 - bx1)

    # Пропускаем, если сторона получилась некорректной (например, 0 после обрезки)
    if side <= 0:
        continue

    # Создаём объёмное изображение квадрата (тень + бевел)
    volumetric_square, padding = create_volumetric_square(side, BLUE_COLOR)

    # Вычисляем координаты вставки с учётом отступа под тень
    paste_x = int(bx1) - padding
    paste_y = int(by1) - padding

    # Вставляем объёмный квадрат на холст, используя его альфа-канал как маску
    canvas.paste(volumetric_square, (paste_x, paste_y), volumetric_square)

# Конвертируем итоговое изображение обратно в RGB (убираем альфа-канал для сохранения)
result = canvas.convert("RGB")

# Сохраняем итоговое изображение в файл
result.save("co2_visualization.png")

# Выводим сообщение об успешном сохранении
print("Изображение сохранено как co2_visualization.png")