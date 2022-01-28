class MyException(Exception):  # 继承异常类
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg