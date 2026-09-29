"""
15. Одна волна — знакомство с синусом (продвинутый уровень, шаг 1).

Синус — это «качели»: math.sin(угол) плавно ходит от -1 до 1 и обратно,
пока угол растёт от 0° до 360°. Больше ничего знать не нужно.
Если по горизонтали идти шагами, а высоту брать из синуса — получится волна.
"""
import turtle
import math

# Сначала посмотрим на числа: угол -> синус
for angle in range(0, 361, 45):
    print(angle, "°  ->", round(math.sin(math.radians(angle)), 2))

screen = turtle.Screen()
screen.setup(800, 400)
screen.title("15: одна волна")

t = turtle.Turtle()
t.hideturtle()
# t.speed(0)
t.penup()

AMPLITUDE = 60          # высота волны в пикселях

for x in range(-360, 361, 5):
    angle = x            # пусть угол равен координате x: 720 px = 720° = две волны
    y = AMPLITUDE * math.sin(math.radians(angle))
    t.goto(x, y)
    t.pendown()          # первый goto — прыжок, дальше рисуем

AMPLITUDE = 120          # высота волны в пикселях

for x in range(-360, 361, 5):
    angle = x  * 2          # пусть угол равен координате x: 720 px = 720° = две волны
    y = AMPLITUDE * math.sin(math.radians(angle))
    t.goto(x, y)
    t.pendown()          # первый goto — прыжок, дальше рисуем

# Попробуй: AMPLITUDE = 150; angle = x * 2 (волн станет вдвое больше); angle = x / 2.
screen.exitonclick()
