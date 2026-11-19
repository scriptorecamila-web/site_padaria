from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save


def associar_grupo_clientes(sender, instance, created, **kwargs):
    if not created or instance.is_staff or instance.is_superuser:
        return
    grupo, _ = Group.objects.get_or_create(name="Clientes")
    instance.groups.add(grupo)


def conectar():
    post_save.connect(
        associar_grupo_clientes,
        sender=get_user_model(),
        dispatch_uid="confeitaria.associar_grupo_clientes",
    )
