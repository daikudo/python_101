import math

class Circle:
    def __init__(self, radius, x,y):
        self.radius = radius
        self.x = x
        self.y = y

    def area (self):
        return math.pi * self.radius ** 2

    @property
    def diametr(self):
        return self.radius * 2

    def __str__(self):
    return (f"Обьект Circle: радиус {self.radius}")
    
circle = Circle (10, 0, 0)
print (type(circle))