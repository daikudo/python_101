"""
Здесь в этом файле мы будем изучать синтаксис языка программирования Python.

"""
import math # импортируем модуль math, который содержит математические функции и константы

# так мы будем писать комментарии в одну строку

variable = 100 
print (variable**2 + 13) # возводим переменную в квадрат и прибавляем 13
print (variable*13 + 16) # умножаем переменную на 13 и прибавляем 16

print (f"Наш ответ №1: {variable**2 + 25}")
print ("Наш ответ №1: ", variable**2 + 25) # выводим на экран строку "Наш ответ №1: " и результат вычисления выражения variable**2 + 25

seconds_in_min = 60 # создаем переменную seconds_in_min и присваиваем ей значение 60
mins_in_hour = 60 # создаем переменную mins_in_hour и присваиваем ей значение 60
hours_in_day = 24 # создаем переменную hours_in_day и присваиваем ей значение 24
days_in_year = 365 # создаем переменную days_in_year и присваиваем ей значение 365
seconds_in_year = seconds_in_min * mins_in_hour * hours_in_day * days_in_year # создаем переменную seconds_in_year и присваиваем ей значение произведения переменных seconds_in_min, mins_in_hour, hours_in_day и days_in_year
print (f"В одном году {seconds_in_year} секунд") # выводим на экран строку "В одном году {seconds_in_year} секунд", где {seconds_in_year} будет заменено на значение переменной seconds_in_year


# Необычная арифметика Питона

our_number = 42
print (our_number**2)
print (our_number**3)

print(our_number / 7) # делим переменную our_number на 7
print(our_number * 10) # умножаем переменную our_number на 10

print(our_number // 10) # делим переменную our_number на 10 и округляем результат до целого числа
print(our_number % 10) # делим переменную our_number на 10 и выводим остаток от деления


our_sine = math.sin(math.pi)
our_cosine = math.cos(math.pi)
print (f"Синус числа Пи равен {our_sine}, а косинус числа Пи равен {our_cosine}") # выводим на экран строку "Синус числа Пи равен {our_sine}, а косинус числа Пи равен {our_cosine}", где {our_sine} и {our_cosine} будут заменены на значения переменных our_sine и our_cosine


my_name = "John Jhonson"
my_age = 42
my_city = "Moscow"
my_wine = "Cabernet Sauvignon"

first_row_group = ["Максим", 
                   "Алексей", 
                   "Иван", 
                   "Дмитрий"]

second_row_group = ["Сергей", 
                    "Андрей", 
                    "Николай", 
                    "Владимир"]


print   (type(my_name)) # проверяем тип переменной my_name
print (type(my_age)) # проверяем тип переменной my_age
print (type(my_city)) # проверяем тип переменной my_city
print (type(my_wine)) # проверяем тип переменной my_wine

print (type(first_row_group)) # проверяем тип переменной first_row_group
print (type(second_row_group)) # проверяем тип переменной second_row_group

my_secret_system = {
    0: "Выходи",
    1: "Не выходи",
    2: "Иди домой",
    3: "Иди в магазин",
    4: "Иди в кино",
    5: "Иди в театр",
    6: "Спи",
}

print (type(my_secret_system)) # проверяем тип переменной my_secret_system

print (my_secret_system[0]) # выводим на экран значение по ключу 0 в словаре my_secret_system
print (my_secret_system[6]) # выводим на экран значение по ключу 6 в словаре my_secret_system

# тест с именем

name = "Ясельский Алексей Анатольевич"
smth = name.split() # разбиваем строку name на список слов по пробелам

print(smth [0])
print(smth [1])
print(smth [2])


print ("Hello, World!") # выводим на экран строку "Hello, World!"
