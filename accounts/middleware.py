from django.shortcuts import redirect
from accounts.utils import is_health_profile_complete

_EXEMPT_PATHS = frozenset(
    {
        "/profile/edit/",
        "/login/",
        "/logout/",
        "/register/",
    },
)
_EXEMPT_PREFIXES = (
    "/admin/",
    "/static/",
    "/media/",
)


class RequireCompleteHealthProfileMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return self.get_response(request)
            path = request.path
            if path not in _EXEMPT_PATHS and not any(
                path.startswith(p) for p in _EXEMPT_PREFIXES
            ):
                if path != "/" and not is_health_profile_complete(request.user):
                    return redirect("profile_edit")
        return self.get_response(request)
