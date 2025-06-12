from linescore_mod import *
import pickle
# linescore = Linescore(gameId="testGameId",linescoreData={"test":"data"})
# print(Linescore.__class__)
"""
 NOTE ON DECORATING CLASSES
    WHEN A CLASS IS DECORATED BY SOMETHING OTHER THAN @dataclass
    THE module.__class__ IS DIFFERENT THAN instance.__class__ OF SOME INSTANCE
    THAT CLASS HENCE THIS MEANS THE OBJECT CANNOT BE PICKLED SINCE THEY HAVE DIFFERENT CLASSES
    AND PICKLE REQUIRES THAT module.__class__ == instance.__class__

"""
# print(linescore.__class__,linescore.__module__,Linescore.__name__)

"""
    the decorator function runs when the decorator is applied
"""
# def myDecorator(func):
#     print("Decorating function")
#     def wrapper(*args,**kwargs):
#         return func(*args,**kwargs)
#     return wrapper

# @myDecorator
# def decoratedFunc():
#     print("Regular function running")



# decoratedFunc()
# myInstance = MyClass(name="Raman",val=0)
# print(myInstance.__class__)
# print(MyClass.__class__)
# print(pickle.dumps(myInstance))


