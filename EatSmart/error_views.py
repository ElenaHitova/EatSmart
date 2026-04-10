from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token


@requires_csrf_token
def server_error(request):

    return render(request, "500.html", status=500)