class classproperty:
    """
    Method decorator that acts like a combination @classmethod + @property
    """

    def __init__(self, func):
        self.fget = func

    def __get__(self, instance, owner):
        return self.fget(owner)


def singleton(class_):
    """
    Class decorator that only allows one instance to be created.

    ```
    @singleton
    class Test: ...

    assert Test() is Test() # True
    ```
    """

    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance
