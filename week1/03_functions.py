# import turtle

# # Настраиваем экран

# screen = turtle.Screen()
# screen.setup (600,600)
# screen.title("Прыгающий мяч")
# screen.tracer(0)

# ball = turtle.Turtle()
# ball.shape("circle")
# ball.shapesize(2)
# ball.color("red")
# ball.penup()
# ball.pendown()

# LIMIT = 260
# velocity = [10, 4]

# def central_university ():  
#     x, y = ball.position()
#     x = x + velocity [0]
#     y = y + velocity [1]

#     if x > LIMIT or x < -LIMIT:
#         velocity [0] = -velocity [0]
#     if y > LIMIT or y < -LIMIT:
#         velocity[1] = -velocity[1]

#     ball.goto (x, y)
#     screen.update()
#     screen.ontimer(central_university, 1000)

# central_university()
# screen.mainloop()

from week1.our_f import give_me_squared_number, give_me_any_power

# for i in range (10):
#     print (f"Квадрат числа {i} = {i**2}") # выводим на экран

my_var = give_me_squared_number (9)
my_other_var = give_me_any_power(9,9)

print(f"my_var = {my_var}")
print(f"my_other_var = {my_other_var}")