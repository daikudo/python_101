import turtle   
from random import random

CANVAS_W = 1000
CANVAS_H = 1000

screen = turtle.Screen()
screen.setup (CANVAS_W, CANVAS_H)
screen.tracer (0)

t = turtle.Turtle ()
t.hideturtle ()
t.speed ()

num_rows = 50
num_cols = 50
start_x = -CANVAS_W / 2
start_y = CANVAS_H /2

#количество рядов, начальная координата, количество ячеек
cell_w = CANVAS_W / num_cols
cell_h = CANVAS_H / num_rows

#два цвета
color_a = (1, 0, 0)
color_b = (0.16, 0.2, 0.36)

def mix(a, b, k):
    return a + (b-a)*k

def between (color1, color2, k):
    r = mix (color1[0], color2[0], k)
    g = mix (color1[1], color2[1], k)
    b = mix (color1[2], color2 [2], k)
    return (r,g,b)

#Функция для ячейки
def cell (x, y, color):
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.fillcolor(color)
    t.pencolor (color)

    t. begin_fill()

    for i in range (2):
        t.forward(cell_w)
        t.right(90)
        t.forward(cell_h)
        t.right(90)
    t.end_fill()

num_cells = num_cols * num_rows
for i in range (num_cells):
    row = i //num_cols
    col = i % num_cols

    #k = (row + col) % 2
    #k = row / (num_rows - 1)
    k = (row + col) / (num_rows + num_cols - 2)

    x = start_x + col * cell_w
    y = start_y - row * cell_h

    color = between(color_a, color_b, k)
    cell(x, y, color)
    screen.update()

screen.update()
screen.exitonclick()
