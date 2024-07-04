"""
装饰器方法：这种方法简单明了，适合大多数情况，但装饰器需要额外的函数调用。
def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class SingletonClass:
    def __init__(self):
        self.value = None

# 示例用法
singleton1 = SingletonClass()
singleton2 = SingletonClass()

singleton1.value = "Hello"
print(singleton2.value)  # 输出: Hello

print(singleton1 is singleton2)  # 输出: True


类方法：这种方法更为正式，适合需要更高扩展性的情况。
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class SingletonClass(metaclass=SingletonMeta):
    def __init__(self):
        self.value = None

# 示例用法
singleton1 = SingletonClass()
singleton2 = SingletonClass()

singleton1.value = "Hello"
print(singleton2.value)  # 输出: Hello

print(singleton1 is singleton2)  # 输出: True

模块级属性：这种方法利用 Python 模块的特性，适合一些简单的单例实现。
class SingletonClass:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.value = None

# 示例用法
if __name__ == "__main__":
    singleton1 = SingletonClass()
    singleton2 = SingletonClass()

    singleton1.value = "Hello"
    print(singleton2.value)  # 输出: Hello

    print(singleton1 is singleton2)  # 输出: True
"""
def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance