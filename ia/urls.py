from django.urls import path

from . import views

app_name = "ia"

urlpatterns = [
    path("assistente/", views.Assistente.as_view(), name="assistente"),
    path("assistente/conversas/", views.ListaConversas.as_view(), name="conversa_lista"),
]
