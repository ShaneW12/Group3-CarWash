from django.http import HttpResponseRedirect


class RemoveChatTrackingMiddleware:
    """Drop the optional chat referral query parameter from GET page URLs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "GET" and request.GET.get("utm_source") == "chatgpt.com":
            params = request.GET.copy()
            params.pop("utm_source", None)
            query = params.urlencode()
            url = request.path + ("?" + query if query else "")
            return HttpResponseRedirect(url)
        return self.get_response(request)
