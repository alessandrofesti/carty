
class parentclass:
        b = 31

        def __init__(self):
                self.a = 21
        def add(self, a, b):
                self.c = a+b
                print(self.c)


class childclass(parentclass):
        pass

child1 = childclass()

child1.add(10,20)
print(child1.b)
print(child1.a)
print(child1.c)