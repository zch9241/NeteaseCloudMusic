class B():
    def __init__(self) -> None:
        pass
    def fun(self):
        print('ok')


class A():

    def __init__(self) -> None:
        global b,a
        b = B()
        a = 1
    def funb(self):
        b.fun()
    def funa(self):
        global a
        a = self.funa.__name__
    def funa_(self):
        print(a)

_ = A()
_.funa()
_.funa_()