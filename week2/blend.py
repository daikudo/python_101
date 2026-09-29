import os
import numpy
from PIL import Image
from random import randint

FOLDER = "week2/movies/"

files = os.listdir(FOLDER)
files = sorted(files)
c = 0
Image.new("RGB", (900, 1600), "#FFFFFF").save("week2/movies/blend_two_files.jpg")
for file in files:
    a=Image.open("week2/movies/blend_two_files.jpg").convert("RGB")
    b=Image.open(FOLDER + files[c]).convert("RGB").resize(a.size)
    print(file)
   # Image.blend(a,b,0.1).save("week2/movies/blend_two_files.jpg")
    c=+1


total = numpy.zeros((a.height, a.width, 3))
for f in files:
    image = Image.open(FOLDER + f).convert("RGB").resize(a.size)
    total += numpy.array(image)

average = total / len(files)
Image.fromarray(average.astype("uint8")).save("week2/movies/blend_all.jpg")


#a=Image.open(FOLDER + files[randint(0,1000)]).convert("RGB")
#b=Image.open(FOLDER + files[randint(0,1000)]).convert("RGB").resize(a.size)
#Image.blend(a,b,0.001).save("week2/movies/blend_two_files.jpg")

print("DONE")
