import traceback
from django.http import HttpResponse

class ForceDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            return HttpResponse(
                f"<h1>Ultimate Debugger Triggered</h1><pre>{traceback.format_exc()}</pre>",
                status=500
            )
