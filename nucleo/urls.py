from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("confeitaria.urls", namespace="confeitaria")),
    path("", include("ia.urls", namespace="ia")),
]
