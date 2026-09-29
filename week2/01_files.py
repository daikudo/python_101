file = open("sandbox/notes.txt", "w", encoding = "utf-8")
file.write ("первая строка ЧТО ЖЕ СЮДА НАПИСАТЬ?!\n")
file.write ("вторая строка ВОПРОСОВ ЕЩЕ БОЛЬШЕ МДА \n")
file.close ()

file = open ("sandbox/notes.txt", "a", encoding = "utf-8") # "a" - append (добавить, а не перезаписать)
file.write ("третья строка: НЕ ПЕРЕЗАПИСЫВАЕМ, а дополняем то, что уже есть\n") 
file.close ()

file = open ("sandbox/notes.txt", "r", encoding = "utf-8")
text = file.read ()
file.close ()


print (text)


print ("Hello World!")