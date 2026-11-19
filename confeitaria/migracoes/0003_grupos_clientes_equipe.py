from django.db import migrations


def criar_grupos(apps, schema_editor):
    grupo = apps.get_model("auth", "Group")
    grupo.objects.get_or_create(name="Clientes")
    grupo.objects.get_or_create(name="Equipe")


def remover_grupos(apps, schema_editor):
    grupo = apps.get_model("auth", "Group")
    grupo.objects.filter(name__in=["Clientes", "Equipe"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("confeitaria", "0002_movimentoestoque"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(criar_grupos, remover_grupos),
    ]
