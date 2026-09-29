"""
grid_4x4_composer.py

Собирает вертикальные видеоролики (формат 9:16 каждый) в сетку 4x4
на едином вертикальном холсте 9:16, без зазоров и без обрезки —
поскольку каждая ячейка сетки 4x4 сама имеет пропорции 9:16.

Логика смены роликов:
- Первая асинхронная смена части ячеек происходит через
  --first-tick-interval секунд (по умолчанию 5), все последующие —
  через --tick-interval секунд (по умолчанию 10). На каждом тике
  случайные --cells-per-tick ячеек (по умолчанию 3) получают новый
  ролик — вся сетка не переключается разом, смена выглядит
  асинхронной.
- В любой момент времени в сетке не может быть двух одинаковых
  роликов одновременно. Если свободных уникальных роликов не
  хватает — ячейка остаётся чёрным прямоугольником, а не дублем.
- Если ролик короче своего отрезка — он либо проигрывается дважды
  подряд, либо доигрывается зацикливанием до нужной длины.

Дополнительно: ровно --feature-count раз (по умолчанию 3) за всё
видео случайный ролик показывается увеличенным — занимает область
2x2 соседних ячейки поверх базовой сетки, ровно --feature-duration
секунд (по умолчанию 10), после чего сетка 4x4 продолжает работать
как обычно.

Полноэкранные вставки: любой файл в той же папке, чьё имя начинается
с "fullscreen", считается отдельной полноэкранной вставкой — она не
участвует в сетке, а показывается на весь экран поверх абсолютно
всего на --fullscreen-duration секунд (по умолчанию 4). Вставки
воспроизводятся строго по порядку (по алфавиту имён файлов), с
промежутком --fullscreen-gap секунд между ними и перед самой первой
(по умолчанию 10). Общая длительность итогового видео автоматически
увеличивается на (число таких файлов) x --fullscreen-duration секунд.

Финальный ролик: если в папке есть файл с именем "last_video" (любое
расширение), он всегда воспроизводится самым последним, на весь
экран, в своей собственной естественной длительности — без обрезки
и без зацикливания. Общая длительность итогового видео автоматически
увеличивается на длину этого файла.

Установка зависимостей:
    pip install moviepy --break-system-packages
    (плюс системный ffmpeg, см. инструкцию отдельно)

Использование:
    python grid_4x4_composer.py --input /path/to/videos --output result.mp4
"""

import argparse                     # модуль для разбора аргументов командной строки
import math                         # нужен для округления количества тиков и сегментов
import random                       # нужен для случайного выбора ячеек, роликов и позиций
import sys                          # нужен для sys.exit() при ошибках и выхода из скрипта
from pathlib import Path            # удобная работа с путями к файлам вместо строк

from moviepy import (                # в moviepy версии 2.x классы импортируются прямо из moviepy
    VideoFileClip,                   # класс для загрузки одного видеофайла
    CompositeVideoClip,              # класс для сборки нескольких клипов в один кадр
    CompositeAudioClip,              # класс для смешивания нескольких аудиодорожек в одну
    ColorClip,                       # класс для создания сплошного цветного прямоугольника (черные пустые ячейки)
    concatenate_videoclips,          # функция для склейки клипов подряд (используем для повтора короткого ролика)
    vfx,                             # набор видеоэффектов, здесь используется vfx.Loop (зацикливание)
)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"}  # какие расширения считаем видеофайлами
FULLSCREEN_PREFIX = "fullscreen"  # файлы с таким началом имени считаются полноэкранными вставками, а не ячейками сетки
LAST_VIDEO_STEM = "last_video"   # файл с этим именем (без учёта расширения) всегда воспроизводится самым последним


def find_video_files(input_dir: Path) -> list[Path]:
    # функция принимает папку и возвращает отсортированный список путей к уникальным видеофайлам внутри неё
    files = sorted(
        p for p in input_dir.iterdir()                      # перебираем все элементы внутри папки
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS  # оставляем только файлы с нужным расширением
    )
    return files                                             # возвращаем итоговый список путей


def extract_last_video(all_files: list[Path]) -> tuple[list[Path], Path | None]:
    # ищет среди всех найденных файлов ролик с именем LAST_VIDEO_STEM (без учёта регистра и расширения),
    # убирает его из общего списка и возвращает отдельно, чтобы позже поставить самым последним
    remaining = []                                            # сюда попадут все файлы, кроме финального ролика
    last_video_path = None                                    # сюда попадёт путь к финальному ролику, если он найден
    for path in all_files:                                    # перебираем все найденные видеофайлы
        if path.stem.lower() == LAST_VIDEO_STEM and last_video_path is None:  # сравниваем имя файла без расширения
            last_video_path = path                              # запоминаем путь к финальному ролику
        else:
            remaining.append(path)                              # остальные файлы идут в общий список дальше
    return remaining, last_video_path                          # возвращаем оставшиеся файлы и путь к финальному ролику


def split_fullscreen_files(all_files: list[Path]) -> tuple[list[Path], list[Path]]:
    # разделяет общий список видеофайлов на обычные (для ячеек сетки) и полноэкранные вставки —
    # полноэкранными считаются файлы, чьё имя начинается с FULLSCREEN_PREFIX (без учёта регистра)
    grid_files = []                                          # сюда попадут обычные видео для ячеек сетки
    fullscreen_files = []                                    # сюда попадут полноэкранные вставки
    for path in all_files:                                   # перебираем все найденные видеофайлы
        if path.name.lower().startswith(FULLSCREEN_PREFIX):   # проверяем, начинается ли имя файла с нужного префикса
            fullscreen_files.append(path)                      # такой файл идёт в список полноэкранных вставок
        else:
            grid_files.append(path)                             # остальные файлы идут в обычный пул для сетки
    return grid_files, fullscreen_files                       # возвращаем оба списка


def fit_duration(clip: VideoFileClip, target_duration: float) -> VideoFileClip:
    """
    Приводит клип к целевой длительности:
    - если клип длиннее или равен целевой длительности — просто обрезаем его с начала
    - если клип короче — проигрываем его два раза подряд (склейка сам с собой)
    - если и после повтора он всё ещё короче целевой длительности — доигрываем зацикливанием
    """
    if clip.duration >= target_duration:                     # если ролик длиннее или равен целевой длительности
        return clip.subclipped(0, target_duration)            # обрезаем его до нужной длины с начала

    doubled = concatenate_videoclips([clip, clip])            # проигрываем короткий ролик два раза подряд

    if doubled.duration >= target_duration:                   # если двух повторов уже хватает на целевую длительность
        return doubled.subclipped(0, target_duration)          # обрезаем склейку до нужной длины

    # если даже после двух повторов ролик короче целевой длительности — доигрываем зацикливанием до конца
    return doubled.with_effects([vfx.Loop(duration=target_duration)])


def get_block_positions(cols: int, rows: int, block_cols: int, block_rows: int) -> list[tuple[int, int]]:
    # возвращает список всех допустимых позиций (строка, столбец) верхнего левого угла
    # блока размером block_cols x block_rows внутри сетки cols x rows, чтобы блок не вылезал за край
    positions = []                                         # сюда будем собирать все подходящие позиции
    for row in range(rows - block_rows + 1):                # перебираем возможные строки для верхнего края блока
        for col in range(cols - block_cols + 1):             # перебираем возможные столбцы для левого края блока
            positions.append((row, col))                     # добавляем найденную позицию в список
    return positions                                         # возвращаем все варианты позиций


def build_tick_times(total_duration: float, first_interval: float, interval: float) -> list[float]:
    # строит список временных границ смены ячеек: первая граница через first_interval секунд,
    # все последующие — через interval секунд каждая, до конца общей длительности
    times = [0.0]                                             # шкала времени всегда начинается с нуля
    t = first_interval                                         # первая граница смены наступает через first_interval секунд
    while t < total_duration:                                  # пока не дошли до конца общей длительности
        times.append(t)                                         # добавляем очередную границу тика
        t += interval                                            # следующая граница будет через interval секунд после этой
    if times[-1] != total_duration:                              # если последняя добавленная граница не совпадает с концом видео
        times.append(total_duration)                              # добавляем финальную границу, чтобы закрыть последний отрезок
    return times                                                  # возвращаем полный список границ тиков


def build_cell_schedule(
    video_paths: list[Path],        # список путей к уникальным видеофайлам (может быть меньше 16)
    num_cells: int,                 # общее число ячеек сетки (16 для сетки 4x4)
    total_duration: float,          # общая длительность итогового видео в секундах
    first_tick_interval: float,     # через сколько секунд происходит самая первая смена части ячеек
    tick_interval: float,           # через сколько секунд происходят все последующие смены части ячеек
    cells_per_tick: int,            # сколько случайных ячеек меняют ролик на каждом тике
) -> dict[int, list[list]]:
    """
    Строит расписание для каждой ячейки: список отрезков вида
    [начало, конец, путь_к_видео_или_None]. None означает, что в этом
    отрезке ячейка остаётся чёрным прямоугольником (свободных
    уникальных роликов не хватило). В любой момент времени ни один
    путь к видео не встречается активным сразу в двух ячейках.
    """
    tick_times = build_tick_times(total_duration, first_tick_interval, tick_interval)  # границы тиков: первая через 5с, дальше каждые 10с
    num_ticks = len(tick_times) - 1                          # число отрезков между соседними границами тиков

    active: dict[int, Path | None] = {}                      # текущий активный ролик для каждой ячейки (или None = чёрный)
    schedule: dict[int, list[list]] = {i: [] for i in range(num_cells)}  # итоговое расписание отрезков по каждой ячейке

    # --- начальное распределение роликов по ячейкам в момент времени 0 ---
    cell_order = list(range(num_cells))                       # список индексов всех ячеек
    random.shuffle(cell_order)                                # перемешиваем порядок, чтобы распределение было случайным
    pool = list(video_paths)                                  # копия списка уникальных видео для начального распределения
    random.shuffle(pool)                                      # перемешиваем сам список видео

    for position, cell in enumerate(cell_order):              # проходим по перемешанным ячейкам по порядку
        active[cell] = pool[position] if position < len(pool) else None  # назначаем видео, если хватает, иначе оставляем пустой (черный)

    # --- проходим по всем тикам, записывая текущее состояние и меняя часть ячеек перед следующим тиком ---
    for tick_index in range(num_ticks):                       # перебираем все тики по порядку
        seg_start = tick_times[tick_index]                    # начало текущего отрезка времени
        seg_end = tick_times[tick_index + 1]                  # конец текущего отрезка времени
        if seg_end <= seg_start:                              # на всякий случай пропускаем нулевые отрезки
            continue

        for cell in range(num_cells):                          # для каждой ячейки фиксируем её текущее состояние на этот отрезок
            schedule[cell].append([seg_start, seg_end, active[cell]])  # записываем отрезок (начало, конец, путь или None)

        if tick_index == num_ticks - 1:                        # на последнем тике менять уже нечего — это финальный отрезок
            break

        cells_to_change = random.sample(                       # выбираем случайные ячейки, которые сменят ролик на следующем тике
            range(num_cells), k=min(cells_per_tick, num_cells)
        )
        for cell in cells_to_change:                            # перебираем выбранные для смены ячейки по очереди
            currently_used = {                                  # собираем все ролики, занятые прямо сейчас в ДРУГИХ ячейках
                path for other_cell, path in active.items()
                if other_cell != cell and path is not None
            }
            candidates = [                                      # доступные для назначения ролики: свободные и отличные от текущего в этой ячейке
                p for p in video_paths
                if p not in currently_used and p != active[cell]
            ]
            if candidates:                                       # если есть из чего выбрать
                active[cell] = random.choice(candidates)         # выбираем новый случайный ролик для этой ячейки
            else:                                                 # если свободных уникальных роликов не осталось
                active[cell] = None                               # ячейка становится чёрным прямоугольником

    return schedule                                              # возвращаем готовое расписание по всем ячейкам


def merge_segments(segments: list[list]) -> list[list]:
    # объединяет подряд идущие отрезки с одинаковым роликом в один более длинный отрезок,
    # чтобы не загружать один и тот же файл несколько раз без необходимости
    merged: list[list] = []                                     # сюда складываем объединённые отрезки
    for seg in segments:                                        # перебираем исходные отрезки по порядку
        if merged and merged[-1][2] == seg[2] and merged[-1][1] == seg[0]:  # если путь совпадает и отрезки идут подряд без разрыва
            merged[-1][1] = seg[1]                                # просто расширяем конец предыдущего отрезка
        else:
            merged.append(list(seg))                              # иначе добавляем как новый отдельный отрезок
    return merged                                                 # возвращаем объединённый список отрезков


def schedule_sequential_events(
    count: int,                     # сколько событий нужно расставить по порядку
    duration_each: float,           # длительность каждого отдельного события
    gap_between: float,             # промежуток времени между концом одного события и началом следующего
    start_offset: float,            # с какого момента на общей шкале времени начинается самое первое событие
) -> list[tuple[float, float]]:
    # расставляет count событий строго по порядку друг за другом: первое начинается через start_offset секунд,
    # каждое следующее начинается через gap_between секунд после конца предыдущего
    events: list[tuple[float, float]] = []                    # сюда складываем пары (начало, конец) для каждого события
    if count <= 0 or duration_each <= 0:                       # если событий не нужно вовсе — возвращаем пустой список
        return events

    current_start = start_offset                                # момент начала самого первого события
    for _ in range(count):                                       # перебираем все нужные события по очереди
        current_end = current_start + duration_each                # момент конца текущего события
        events.append((current_start, current_end))                 # добавляем готовую пару (начало, конец) в список
        current_start = current_end + gap_between                    # следующее событие начнётся через gap_between секунд после конца этого

    return events                                                     # возвращаем список всех запланированных событий


def schedule_feature_events(
    total_duration: float,          # общая длительность итогового видео
    feature_duration: float,        # длительность одного показа увеличенного блока 2x2
    feature_count: int,             # сколько раз всего должен показаться увеличенный блок за всё видео
) -> list[tuple[float, float]]:
    # делит общую длительность на feature_count примерно равных окон и в каждом
    # окне выбирает случайный момент для показа увеличенного блока 2x2
    events: list[tuple[float, float]] = []                       # сюда складываем пары (начало, конец) для каждого показа
    if feature_count <= 0 or feature_duration <= 0:               # если показов не нужно вовсе — возвращаем пустой список
        return events

    window_len = total_duration / feature_count                  # длина одного окна для одного показа
    for i in range(feature_count):                                # перебираем все нужные показы по очереди
        window_start = i * window_len                             # начало окна для текущего показа
        window_end = (i + 1) * window_len                         # конец окна для текущего показа
        latest_start = max(window_start, window_end - feature_duration)  # самый поздний старт, чтобы показ уместился в окно
        if latest_start > window_start:                            # если внутри окна есть свобода для случайного смещения
            start = random.uniform(window_start, latest_start)      # выбираем случайный момент старта внутри окна
        else:
            start = window_start                                    # иначе показ занимает окно от самого начала
        end = min(start + feature_duration, total_duration)          # конец показа, не выходя за пределы общей длительности
        events.append((start, end))                                  # добавляем готовую пару (начало, конец) в список

    return events                                                     # возвращаем список всех запланированных показов


def get_active_videos_in_window(
    schedule: dict[int, list[list]],   # готовое расписание ячеек сетки (после merge_segments)
    window_start: float,                # начало интересующего нас временного окна
    window_end: float,                  # конец интересующего нас временного окна
) -> set[Path]:
    # возвращает множество всех роликов, которые хотя бы частично показываются
    # в какой-либо ячейке сетки в течение заданного временного окна
    active_videos: set[Path] = set()                          # сюда собираем все занятые в этом окне ролики
    for segments in schedule.values():                         # перебираем расписание каждой ячейки
        for seg_start, seg_end, path in segments:                # перебираем все отрезки этой ячейки
            if path is None:                                      # пустые (чёрные) отрезки нас не интересуют
                continue
            if seg_start < window_end and seg_end > window_start:  # проверяем пересечение отрезка с нашим окном
                active_videos.add(path)                              # ролик пересекается с окном — считаем его занятым
    return active_videos                                        # возвращаем итоговое множество занятых роликов


def build_grid(
    video_paths: list[Path],        # список путей к уникальным видеофайлам для ячеек сетки
    canvas_width: int,              # ширина итогового холста в пикселях
    canvas_height: int,             # высота итогового холста в пикселях
    target_duration: float,         # целевая длительность итогового видео в секундах (уже с учётом полноэкранных вставок)
    first_tick_interval: float,     # через сколько секунд происходит самая первая смена части ячеек
    tick_interval: float,           # через сколько секунд происходят все последующие смены части ячеек
    cells_per_tick: int,            # сколько ячеек меняются на каждом тике
    feature_duration: float,        # длительность одного показа увеличенного блока 2x2
    feature_count: int,             # сколько раз всего показывается увеличенный блок за всё видео
    fullscreen_files: list[Path],   # список полноэкранных вставок (файлы с префиксом fullscreen)
    fullscreen_duration: float,     # длительность показа каждой полноэкранной вставки в секундах
    fullscreen_gap: float,          # промежуток времени между полноэкранными вставками (и перед самой первой)
    last_video_path: Path | None,   # путь к финальному ролику (last_video), который всегда идёт самым последним, или None
    last_video_start: float,        # момент на общей шкале времени, с которого начинается финальный ролик
    keep_audio_index: int | None,   # индекс ячейки (0-15), чей звук нужно оставить (или None)
    mix_audio: bool,                # флаг: смешивать ли звук всех звучащих ячеек вместе
) -> CompositeVideoClip:
    cols, rows = 4, 4                # фиксированная сетка 4 столбца на 4 строки
    cell_w = canvas_width // cols    # ширина одной ячейки = ширина холста делённая на число столбцов
    cell_h = canvas_height // rows   # высота одной ячейки = высота холста делённая на число строк

    schedule = build_cell_schedule(                              # строим расписание асинхронной смены роликов по ячейкам
        video_paths,
        num_cells=cols * rows,
        total_duration=target_duration,
        first_tick_interval=first_tick_interval,
        tick_interval=tick_interval,
        cells_per_tick=cells_per_tick,
    )
    for cell in schedule:                                         # проходим по всем ячейкам расписания
        schedule[cell] = merge_segments(schedule[cell])            # объединяем соседние одинаковые отрезки для экономии загрузок

    positioned_clips = []            # сюда будем складывать все готовые клипы (и видео, и чёрные заглушки) для финальной сборки
    audio_tracks = []                # сюда будем складывать аудиодорожки, если включено смешивание звука

    for cell_index in range(cols * rows):                          # перебираем все 16 ячеек сетки по порядку
        row = cell_index // cols                                    # номер строки ячейки в сетке
        col = cell_index % cols                                     # номер столбца ячейки в сетке

        for seg_start, seg_end, path in schedule[cell_index]:        # перебираем все отрезки времени для этой ячейки
            seg_len = seg_end - seg_start                            # длительность текущего отрезка
            if seg_len <= 0:                                         # пропускаем отрезки нулевой или отрицательной длины
                continue

            if path is None:                                         # если в этом отрезке ячейка должна быть чёрной
                black_block = (                                        # создаём сплошной чёрный прямоугольник нужного размера
                    ColorClip(size=(cell_w, cell_h), color=(0, 0, 0))
                    .with_duration(seg_len)                             # задаём длительность равной длине отрезка
                    .with_position((col * cell_w, row * cell_h))         # ставим его на позицию соответствующей ячейки
                    .with_start(seg_start)                                # задаём момент появления на общей шкале времени
                )
                positioned_clips.append(black_block)                     # добавляем чёрную заглушку в общий список клипов
                continue                                                  # переходим к следующему отрезку

            raw_clip = VideoFileClip(str(path))                          # загружаем видеофайл, назначенный на этот отрезок
            clip = fit_duration(raw_clip, seg_len)                       # подгоняем его длительность под длину отрезка
            clip = clip.resized(new_size=(cell_w, cell_h))               # меняем размер клипа под размер ячейки сетки
            clip = clip.with_position((col * cell_w, row * cell_h))      # задаём позицию клипа на холсте по координатам ячейки
            clip = clip.with_start(seg_start)                            # задаём момент появления этого отрезка на общей шкале времени

            keep_this_audio = mix_audio or (                             # решаем, нужно ли оставлять звук у этого отрезка
                keep_audio_index is not None and cell_index == keep_audio_index
            )
            if mix_audio and clip.audio is not None:                     # если включено смешивание и у клипа есть звук
                audio_tracks.append(clip.audio)                          # добавляем его аудиодорожку в список для сведения
            if not keep_this_audio:                                     # если звук у этого отрезка оставлять не нужно
                clip = clip.without_audio()                              # отключаем звук

            positioned_clips.append(clip)                                # добавляем готовый отрезок в общий список клипов

    # --- увеличенные блоки 2x2: показываются ровно feature_count раз за всё видео ---
    block_positions = get_block_positions(cols, rows, block_cols=2, block_rows=2)  # все варианты позиций блока 2x2 в сетке 4x4
    feature_events = schedule_feature_events(target_duration, feature_duration, feature_count)  # моменты показа увеличенного блока

    for f_start, f_end in feature_events:                             # перебираем все запланированные показы увеличенного блока
        seg_len = f_end - f_start                                      # длительность текущего показа
        if seg_len <= 0:                                                # пропускаем показы нулевой длины
            continue

        row, col = random.choice(block_positions)                       # случайно выбираем позицию блока 2x2 для этого показа

        occupied = get_active_videos_in_window(schedule, f_start, f_end)  # ролики, уже занятые в сетке в это же время
        candidates = [p for p in video_paths if p not in occupied]        # доступные для увеличенного блока ролики — без дублей с сеткой
        if not candidates:                                                 # если свободных уникальных роликов не осталось вовсе
            continue                                                        # пропускаем этот показ, чтобы не нарушать правило "без дублей"
        source_path = random.choice(candidates)                            # случайно выбираем, какой ролик будет увеличенным

        feature_clip = VideoFileClip(str(source_path))                  # заново загружаем выбранный ролик для увеличенной версии
        feature_clip = fit_duration(feature_clip, seg_len)               # подгоняем его длительность под длину показа
        feature_clip = feature_clip.resized(new_size=(cell_w * 2, cell_h * 2))  # увеличиваем ролик до размера блока 2x2 ячеек
        feature_clip = feature_clip.without_audio()                      # отключаем звук у увеличенного ролика
        feature_clip = feature_clip.with_position((col * cell_w, row * cell_h))  # ставим блок на выбранную позицию в сетке
        feature_clip = feature_clip.with_start(f_start)                  # задаём момент появления блока на общей шкале времени

        positioned_clips.append(feature_clip)                             # добавляем увеличенный блок поверх базовой сетки

    # --- полноэкранные вставки: каждая из fullscreen_files показывается на весь экран, поверх абсолютно всего ---
    fullscreen_events = schedule_sequential_events(                        # находим моменты показа для каждой полноэкранной вставки по порядку
        len(fullscreen_files), fullscreen_duration, fullscreen_gap, fullscreen_gap
    )
    for (fs_start, fs_end), source_path in zip(fullscreen_events, fullscreen_files):  # сопоставляем моменты показа с файлами по порядку
        seg_len = fs_end - fs_start                                        # длительность текущей полноэкранной вставки
        if seg_len <= 0:                                                   # пропускаем вставки нулевой длины
            continue

        fullscreen_clip = VideoFileClip(str(source_path))                  # загружаем полноэкранный ролик
        fullscreen_clip = fit_duration(fullscreen_clip, seg_len)            # подгоняем его длительность под отведённый отрезок
        fullscreen_clip = fullscreen_clip.resized(new_size=(canvas_width, canvas_height))  # растягиваем ролик на весь холст
        fullscreen_clip = fullscreen_clip.with_position((0, 0))            # ставим его в самый угол холста, чтобы закрыть весь кадр
        fullscreen_clip = fullscreen_clip.with_start(fs_start)              # задаём момент появления вставки на общей шкале времени

        positioned_clips.append(fullscreen_clip)                            # добавляем вставку последней, чтобы она перекрыла всё остальное

    # --- финальный ролик: воспроизводится в самом конце, на весь экран, в своей естественной длительности ---
    if last_video_path is not None:                                        # если файл last_video был найден в папке
        last_clip = VideoFileClip(str(last_video_path))                    # загружаем финальный ролик без обрезки и зацикливания
        last_clip = last_clip.resized(new_size=(canvas_width, canvas_height))  # растягиваем его на весь холст
        last_clip = last_clip.with_position((0, 0))                         # ставим его в самый угол холста, чтобы закрыть весь кадр
        last_clip = last_clip.with_start(last_video_start)                   # задаём момент появления — после всего остального контента

        positioned_clips.append(last_clip)                                   # добавляем финальный ролик самым последним в списке клипов

    final = CompositeVideoClip(
        positioned_clips, size=(canvas_width, canvas_height), bg_color=(0, 0, 0)  # собираем все клипы в один кадр на чёрном фоне
    ).with_duration(target_duration)                                       # задаём общую длительность итогового видео

    if mix_audio and audio_tracks:                                        # если включено смешивание и есть что смешивать
        final = final.with_audio(CompositeAudioClip(audio_tracks))         # накладываем сведённую аудиодорожку на итоговое видео

    return final                                                           # возвращаем готовый итоговый клип


def main():
    parser = argparse.ArgumentParser(description="Сборка видео в сетку 4x4")  # создаём парсер аргументов командной строки
    parser.add_argument(
        "--input",
        default=r"O:\work\dotEXE\videos",  # путь к папке с видео на компьютере по умолчанию
        help="Папка с видеофайлами",
    )
    parser.add_argument(
        "--output",
        default=r"O:\work\dotEXE\out\result.mp4",  # путь для сохранения итогового видео по умолчанию
        help="Путь к итоговому файлу, например result.mp4",
    )
    parser.add_argument("--width", type=int, default=1080, help="Ширина холста")   # ширина итогового видео, по умолчанию 1080
    parser.add_argument("--height", type=int, default=1920, help="Высота холста")  # высота итогового видео, по умолчанию 1920 (9:16)
    parser.add_argument(
        "--duration",
        type=float,
        default=60.0,  # общая длительность итогового видео в секундах по умолчанию
        help="Общая длительность итогового видео в секундах",
    )
    parser.add_argument(
        "--first-tick-interval",
        type=float,
        default=5.0,  # через сколько секунд происходит самая первая смена части ячеек, по умолчанию 5
        help="Через сколько секунд происходит самая первая асинхронная смена части ячеек",
    )
    parser.add_argument(
        "--tick-interval",
        type=float,
        default=10.0,  # через сколько секунд происходят все последующие смены части ячеек, по умолчанию 10
        help="Через сколько секунд происходят все последующие асинхронные смены части ячеек",
    )
    parser.add_argument(
        "--cells-per-tick",
        type=int,
        default=3,  # сколько ячеек меняют ролик на каждом тике, по умолчанию 3
        help="Сколько случайных ячеек меняют ролик на каждом тике",
    )
    parser.add_argument(
        "--feature-duration",
        type=float,
        default=10.0,  # длительность одного показа увеличенного блока 2x2, по умолчанию 10 секунд
        help="Длительность одного показа увеличенного блока 2x2 в секундах",
    )
    parser.add_argument(
        "--feature-count",
        type=int,
        default=3,  # сколько раз всего показывается увеличенный блок за всё видео, по умолчанию 3
        help="Сколько раз за всё видео показывается увеличенный блок 2x2",
    )
    parser.add_argument(
        "--fullscreen-duration",
        type=float,
        default=4.0,  # длительность показа каждой полноэкранной вставки, по умолчанию 4 секунды
        help="Длительность показа каждого ролика с префиксом fullscreen на весь экран, в секундах",
    )
    parser.add_argument(
        "--fullscreen-gap",
        type=float,
        default=10.0,  # промежуток между полноэкранными вставками (и перед самой первой), по умолчанию 10 секунд
        help="Промежуток в секундах между полноэкранными вставками (и перед самой первой из них)",
    )
    parser.add_argument("--keep-audio", type=int, default=None, help="Индекс ячейки (0-15), чей звук оставить")  # опциональный индекс со звуком
    parser.add_argument("--mix-audio", action="store_true", help="Смешать звук всех звучащих ячеек")  # флаг смешивания звука
    parser.add_argument("--fps", type=int, default=30)  # частота кадров итогового видео, по умолчанию 30
    args = parser.parse_args()          # разбираем аргументы, переданные пользователем при запуске скрипта

    input_dir = Path(args.input)        # превращаем строку пути в объект Path для удобной работы
    if not input_dir.is_dir():          # проверяем, что указанная папка действительно существует
        sys.exit(f"Папка не найдена: {input_dir}")  # если папки нет — завершаем скрипт с понятным сообщением

    all_files = find_video_files(input_dir)     # получаем список всех видеофайлов из указанной папки
    if len(all_files) == 0:                     # проверяем, что папка вообще не пустая
        sys.exit(f"В папке {input_dir} не найдено ни одного видеофайла.")  # если видео нет вообще — выходим с ошибкой

    all_files, last_video_path = extract_last_video(all_files)  # отделяем финальный ролик (last_video), если он есть в папке
    video_files, fullscreen_files = split_fullscreen_files(all_files)  # отделяем полноэкранные вставки от обычных роликов сетки

    if len(video_files) == 0:                    # проверяем, что для самой сетки хоть что-то осталось
        sys.exit(f"В папке {input_dir} не найдено обычных видео для сетки (все файлы — полноэкранные вставки).")

    if len(video_files) < 16:                    # предупреждаем, если уникальных видео меньше, чем ячеек в сетке
        print(
            f"Найдено {len(video_files)} уникальных видео для сетки — "     # сообщаем, сколько нашлось
            f"часть ячеек будет оставаться чёрной, пока роликов не хватает."  # и что пустые ячейки будут чёрными, а не дублями
        )

    total_duration = args.duration + len(fullscreen_files) * args.fullscreen_duration  # добавляем к базовой длительности время всех полноэкранных вставок

    if fullscreen_files:                          # если нашлись полноэкранные вставки
        print(
            f"Найдено {len(fullscreen_files)} полноэкранных вставок (fullscreen) — "  # сообщаем, сколько их нашлось
            f"общая длительность увеличена до {total_duration:.1f} секунд."           # и на сколько это увеличило итоговую длительность
        )
        print("Полноэкранные вставки:")            # выводим заголовок списка полноэкранных файлов
        for i, f in enumerate(fullscreen_files):    # перебираем найденные полноэкранные файлы с их индексом
            print(f"  [{i:2d}] {f.name}")           # печатаем индекс и имя каждого файла для наглядности

    last_video_start = total_duration              # финальный ролик начинается ровно там, где заканчивается всё остальное

    if last_video_path is not None:                # если файл last_video найден
        probe_clip = VideoFileClip(str(last_video_path))  # временно загружаем его, чтобы узнать длительность
        last_video_duration = probe_clip.duration        # считываем длительность финального ролика
        probe_clip.close()                                # закрываем временный клип, освобождая ресурсы
        total_duration += last_video_duration             # увеличиваем общую длительность на длину финального ролика
        print(
            f"Найден финальный ролик last_video ({last_video_path.name}), "  # сообщаем, что финальный ролик найден
            f"длительность {last_video_duration:.1f} секунд — "               # и его длительность
            f"он будет добавлен в самый конец, общая длительность станет {total_duration:.1f} секунд."  # и итоговый эффект на общий тайминг
        )

    print("Используются файлы сетки:")           # выводим заголовок списка используемых файлов сетки в консоль
    for i, f in enumerate(video_files):         # перебираем найденные файлы с их индексом
        print(f"  [{i:2d}] {f.name}")           # печатаем индекс и имя каждого файла для наглядности

    final_clip = build_grid(                    # вызываем функцию сборки сетки со всеми параметрами
        video_files,                             # список путей к уникальным видео для ячеек сетки
        canvas_width=args.width,                 # ширина холста из аргументов
        canvas_height=args.height,               # высота холста из аргументов
        target_duration=total_duration,          # итоговая длительность видео, уже с учётом полноэкранных вставок
        first_tick_interval=args.first_tick_interval,  # интервал до первой смены ячеек из аргументов
        tick_interval=args.tick_interval,        # интервал всех последующих смен ячеек из аргументов
        cells_per_tick=args.cells_per_tick,      # число ячеек, меняющихся за один тик, из аргументов
        feature_duration=args.feature_duration,  # длительность одного показа увеличенного блока из аргументов
        feature_count=args.feature_count,        # сколько раз показывается увеличенный блок из аргументов
        fullscreen_files=fullscreen_files,       # список полноэкранных вставок
        fullscreen_duration=args.fullscreen_duration,  # длительность показа каждой полноэкранной вставки из аргументов
        fullscreen_gap=args.fullscreen_gap,      # промежуток между полноэкранными вставками из аргументов
        last_video_path=last_video_path,         # путь к финальному ролику (last_video), если он найден
        last_video_start=last_video_start,       # момент, с которого начинается финальный ролик
        keep_audio_index=args.keep_audio,        # индекс со звуком из аргументов
        mix_audio=args.mix_audio,                # флаг смешивания звука из аргументов
    )

    output_path = Path(args.output)              # превращаем путь к итоговому файлу в объект Path
    output_path.parent.mkdir(parents=True, exist_ok=True)  # создаём папку назначения, если её ещё нет

    final_clip.write_videofile(                  # запускаем рендер и сохранение итогового видео в файл
        str(output_path),                         # путь к выходному файлу
        fps=args.fps,                             # частота кадров рендера
        codec="libx264",                          # видеокодек для сохранения (стандартный H.264)
        audio_codec="aac" if final_clip.audio is not None else None,  # аудиокодек, только если есть звук
    )


if __name__ == "__main__":     # проверяем, что скрипт запущен напрямую, а не импортирован как модуль
    main()                      # запускаем основную функцию скрипта