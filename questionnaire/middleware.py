from threadlocals.threadlocals import set_thread_variable

class SetUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_thread_variable('user', request.user)
        response = self.get_response(request)
        return response