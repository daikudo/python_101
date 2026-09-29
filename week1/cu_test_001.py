import math
from PIL import Image

def single_spike(t, center, amplitude, sharpness):
    d = abs(t - center)
    return -amplitude * math.exp(-d / sharpness)

def local_cell_width(x, center_x, base_size, shrink_amplitude, half_range):
    min_size = max(1.0, base_size - shrink_amplitude)
    k = (base_size - min_size) / (half_range ** 2)
    return min_size + k * (x - center_x) ** 2      # обычная: минимум в центре, рост к краям

def local_cell_height(y, center_y, base_size, grow_amplitude, half_range):
    max_size = base_size
    min_size = max(1.0, base_size - grow_amplitude)
    k = (max_size - min_size) / (half_range ** 2)
    return max_size - k * (y - center_y) ** 2      # обратная: максимум в центре, уменьшение к краям

def create_xy_checkerboard(width, height,
                            base_size_x, shrink_amplitude,
                            base_size_y, grow_amplitude,
                            amplitude, sharpness, spike_center,
                            color1=(255, 255, 255), color2=(0, 0, 0)):
    img = Image.new("RGB", (width, height), color1)
    pixels = img.load()

    center_x = width / 2
    center_y = height / 2
    half_range_x = width / 2
    half_range_y = height / 2

    warped_x = [0.0] * width
    acc_x = 0.0
    for x in range(width):
        w = local_cell_width(x, center_x, base_size_x, shrink_amplitude, half_range_x)
        acc_x += 1 / w
        warped_x[x] = acc_x

    warped_y = [0.0] * height
    acc_y = 0.0
    for y in range(height):
        h = local_cell_height(y, center_y, base_size_y, grow_amplitude, half_range_y)
        acc_y += 1 / h
        warped_y[y] = acc_y

    for y in range(height):
        offset_x = single_spike(y, spike_center, amplitude, sharpness)
        cell_y = int(warped_y[y])
        for x in range(width):
            shifted_index = x + offset_x
            shifted_index = max(0, min(width - 1, int(shifted_index)))
            cell_x = int(warped_x[shifted_index])
            if (cell_x + cell_y) % 2 == 1:
                pixels[x, y] = color2

    return img

width, height = 3500, 1200
center_y_pos = height / 2
center_x_pos = width / 2
spike_center = center_y_pos


img = create_xy_checkerboard(
    width=width, height=height,
    base_size_x=200, shrink_amplitude=191,   # по X: сжатие к центру (мин. 5px)
    base_size_y=200, grow_amplitude=164,     # по Y: обратный эффект (мин. 10px у краёв)
    amplitude=0, sharpness=300,
    spike_center=spike_center
)
img.show()