from PIL import Image
from random import randint

path_original = "data/1665_Girl_with_a_Pearl_Earring.jpg"
path_gen = "week2/jpeg_code/output/GEN_1665_Girl_with_a_Pearl_Earring.jpg"

img =Image.open (path_original)

#img.save(path_gen, quality = 75)

for i in range (10000):
    q = randint(70,80)
    print(f"Итерация №{i}")
    img.save(path_gen, quality = q)
    if i % 100 == 0 and i > 100:
        img.save (path_gen)
    img = Image.open(path_gen)
    #img.load()



print ("Hello world")