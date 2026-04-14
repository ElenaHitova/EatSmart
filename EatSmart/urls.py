"""
URL configuration for EatSmart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.defaults import page_not_found
from EatSmart import error_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("accounts.urls")),
    path("ingredients/", include("ingredients.urls")),
    path("api/ingredients/", include("ingredients.api_urls")),
    path("recipes/", include("recipes.urls")),
    path("api/recipes/", include("recipes.api_urls")),
    path("meal-plans/", include("mealplans.urls")),
    path("django-rq/", include("django_rq.urls")),
    path("", include("accounts.urls")),
    path("shopping/", include("shopping.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


    def preview_404(request):
        return page_not_found(request, Exception("Preview"))


    urlpatterns += [
        path("404/", preview_404),
        path("500/", error_views.server_error),
    ]

handler404 = "django.views.defaults.page_not_found"
handler500 = "EatSmart.error_views.server_error"
