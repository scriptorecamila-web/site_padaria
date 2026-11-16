from django.contrib import admin

from .models import Encomenda, Pedido, Produto


class ClienteProprietarioAdminMixin:
    exclude = ("cliente",)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(cliente=request.user)

    def save_model(self, request, obj, form, change):
        obj.cliente = request.user
        super().save_model(request, obj, form, change)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "preco", "quantidade_estoque")
    list_filter = ("categoria",)
    search_fields = ("nome", "descricao")


@admin.register(Pedido)
class PedidoAdmin(ClienteProprietarioAdminMixin, admin.ModelAdmin):
    list_display = ("produto", "cliente", "quantidade", "data_pedido", "status")
    list_filter = ("status",)


@admin.register(Encomenda)
class EncomendaAdmin(ClienteProprietarioAdminMixin, admin.ModelAdmin):
    list_display = ("produto", "cliente", "data_retirada", "status")
    list_filter = ("status",)
