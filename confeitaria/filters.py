import django_filters

from .models import Encomenda, MovimentoEstoque, Pedido, Produto


class ProdutoFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(
        field_name="nome",
        lookup_expr="icontains",
        label="Nome do produto",
    )

    class Meta:
        model = Produto
        fields = ["nome", "categoria"]


class PedidoFilter(django_filters.FilterSet):
    produto = django_filters.CharFilter(
        field_name="produto__nome",
        lookup_expr="icontains",
        label="Produto",
    )

    class Meta:
        model = Pedido
        fields = ["produto", "status"]


class EncomendaFilter(django_filters.FilterSet):
    produto = django_filters.CharFilter(
        field_name="produto__nome",
        lookup_expr="icontains",
        label="Produto",
    )

    class Meta:
        model = Encomenda
        fields = ["produto", "status"]


class MovimentoEstoqueFilter(django_filters.FilterSet):
    produto = django_filters.CharFilter(
        field_name="produto__nome",
        lookup_expr="icontains",
        label="Produto",
    )

    class Meta:
        model = MovimentoEstoque
        fields = ["produto", "tipo"]
