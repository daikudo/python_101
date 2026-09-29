import turtle
from random import random, randint, choice

def splitter():
    print ("___"*30 + "\n")

    
colors = ["red", "green", "blue", "yellow", "purple", "orange", "pink", "brown", "gray", "black", "white"] # создаем список colors, который содержит 11 элементов


for random_colors in range (10):
   # random_number = random() # создаем переменную random_number, которая будет равна случайному числу от 0 до 1
    random_colors = choice(colors) # создаем переменную random_number, которая будет равна случайному целому числу от 0 до 10
    print (f"Случайный цвет {random_colors}") 


splitter()



# Настраиваем окно черепахи

screen = turtle.Screen() # создаем объект screen, который будет представлять окно черепахи
screen. setup (200, 200) # задаем размер окна черепахи
screen.bgcolor ("#315FdC") # задаем цвет фона окна черепахи
screen.tracer(0) # отключаем анимацию черепахи

# Создаем черепаху  

t = turtle.Turtle() # создаем объект t, который будет представлять черепаху
t.speed(0) # задаем скорость черепахи   
t.hideturtle() # скрываем черепаху
t.color ("#F5F5F5") # задаем цвет черепахи

size = 5    

for row in range (200):
    for col in range (200):
        x = -500 + col * size # задаем координату x черепахи
        y = 500 - row * size # задаем координату y черепахи

        if random () < 0.5: # проверяем, если случайное число от 0 до 1 меньше 0.5
            t.penup() # поднимаем перо черепахи
            t.goto (x, y) # перемещаем черепаху в точку (x, y)
            t.pendown() # опускаем перо черепахи

            t.begin_fill() # начинаем заливку черепахи

            for _ in range (4): # создаем цикл for, который будет выполняться 4 раза
                    t.forward (size) # перемещаем черепаху вперед на size пикселей
                    t.right (90) # поворачиваем черепаху на 90 градусов вправо


            t.end_fill() # завершаем заливку черепахи
        screen.update() # обновляем экран черепахи

screen.update() # обновляем экран черепахи
screen.exitonclick() # ждем, пока пользователь кликнет на окно черепахи, чтобы закрыть его





