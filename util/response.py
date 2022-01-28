from django.http import JsonResponse


class response:  # 继承异常类
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def result(self):
        responseData = {'code': self.code, 'msg': self.msg}
        return JsonResponse(responseData, safe=False, json_dumps_params={'ensure_ascii': False})