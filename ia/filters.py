import django_filters

from .models import Conversa


class ConversaFilter(django_filters.FilterSet):
    titulo = django_filters.CharFilter(
        field_name="titulo",
        lookup_expr="icontains",
        label="Título",
    )

    class Meta:
        model = Conversa
        fields = ["titulo"]
