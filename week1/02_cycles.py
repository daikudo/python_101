"""

В этом модуле мы познакомимся:
1) с условными операторами if, elif и else;
2) с циклами for и while;  
3) с функциями range() и enumerate();
4) с функциями break и continue;

"""


# разберем самый простой цикл

for i in range(13): # создаем цикл for, который будет выполняться 13 раз
    print (i)   

for a in range (15): # создаем цикл for, который будет выполняться 15 раз
    print (a**2) # выводим на экран квадрат числа a

for cube in range (16): # создаем цикл for, который будет выполняться 16 раз
    print (cube**3) # выводим на экран куб числа cube

print ("___________________________________")

for pupa in range (5, 15, 3): # создаем цикл for, который будет выполняться 17 раз
    print (f"pupa's salary is {pupa}")

print ("___________________________________")


colors = ["red", 
         "green", 
         "blue", 
         "yellow", 
         "black", 
         "white"] # создаем список colors, который содержит 6 элементов
print (f"our colors: {colors}") # выводим на экран список colors

for fav_colors in colors: # создаем цикл for, который будет выполняться 6 раз
    print (f"my favorite color is {fav_colors}") # выводим на экран строку "my favorite color is {fav_colors}", где {fav_colors} будет заменено на значение переменной fav_colors

print ("___________________________________")

idxs = [0, 1, 2, 3, 4, 5] # создаем список idxs, который содержит 6 элементов
for my_idx in idxs:
    print (f"my current id {my_idx}: . В квадрате {my_idx**2}") # создаем цикл for, который будет выполняться 6 раз и выводить на экран строку "my current id {my_idx}: . В квадрате {my_idx**2}", где {my_idx} будет заменено на значение переменной my_idx, а {my_idx**2} будет заменено на значение переменной my_idx в квадрате

for bang in range (100):
    ostatok = bang % 4 # создаем переменную ostatok, которая будет равна остатку от деления переменной bang на 4
    if bang % 4 == 0: # проверяем, делится ли переменная bang на 4 без остатка
        print ("BANG-BANG") # выводим на экран строку "BANG"
    if bang % 4 == 1: # проверяем, делится ли переменная bang на 4 с остатком 1
        print ("MY") # выводим на экран строку "BANG!"
    if bang % 4 == 2: # проверяем, делится ли переменная bang на 4 с остатком 2
        print ("BABY") # выводим на экран строку "BABY"
    if bang % 4 == 3: # проверяем, делится ли переменная bang на 4 с остатком 3
        print ("SHUT ME DOWN") # выводим на экран строку "SHUT ME DOWN"


print ("___________________________________")


for bang in range (100):
    ostatok = bang % 4
    if bang % 4 == 0:
        print ("BANG-BANG")
    elif bang % 3 == 0:
        print ("HI-HAT")
    else:
        print ("_________"*10)




print ("___________________________________")


for bang in range (100):
    ostatok = bang % 4
    if bang % 4 == 0 and bang % 3 == 0:
        print ("BANG-BANG HI-HAT")
    elif bang % 3 == 0:
        print ("HI-HAT")
    else:
        print ("_________"*10)


print ("Hello world!") # выводим на экран строку "Hello world!"