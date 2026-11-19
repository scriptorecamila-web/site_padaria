from django.db import transaction

from .models import MovimentoEstoque, Pedido, Produto


class EstoqueInsuficiente(Exception):
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(mensagem)


def _produtos_bloqueados(*produto_ids):
    ids = [pk for pk in dict.fromkeys(produto_ids) if pk]
    return {
        produto.pk: produto
        for produto in Produto.objects.select_for_update().filter(pk__in=ids).order_by("pk")
    }


def _aplicar(produto, tipo, quantidade, motivo, usuario, pedido):
    if quantidade <= 0:
        return None
    if tipo == MovimentoEstoque.SAIDA:
        if produto.quantidade_estoque < quantidade:
            raise EstoqueInsuficiente("Estoque insuficiente para esta quantidade.")
        produto.quantidade_estoque -= quantidade
    else:
        produto.quantidade_estoque += quantidade
    produto.save(update_fields=["quantidade_estoque"])
    return MovimentoEstoque.objects.create(
        produto=produto,
        tipo=tipo,
        quantidade=quantidade,
        motivo=motivo,
        usuario=usuario,
        pedido=pedido,
    )


def _comprometido(status, quantidade):
    if status in (None, "", "CANCELADO"):
        return 0
    return quantidade


def _sincronizar(*, pedido, status_anterior, quantidade_anterior, produto_anterior_id, usuario):
    antes = _comprometido(status_anterior, quantidade_anterior)
    depois = _comprometido(pedido.status, pedido.quantidade)
    produtos = _produtos_bloqueados(produto_anterior_id, pedido.produto_id)

    if produto_anterior_id != pedido.produto_id:
        if antes:
            _aplicar(
                produtos[produto_anterior_id],
                MovimentoEstoque.ENTRADA,
                antes,
                "Estorno por troca de produto no pedido",
                usuario,
                pedido,
            )
        if depois:
            _aplicar(
                produtos[pedido.produto_id],
                MovimentoEstoque.SAIDA,
                depois,
                "Baixa pela troca de produto no pedido",
                usuario,
                pedido,
            )
        return

    delta = depois - antes
    if delta > 0:
        _aplicar(
            produtos[pedido.produto_id],
            MovimentoEstoque.SAIDA,
            delta,
            "Baixa automática do pedido",
            usuario,
            pedido,
        )
    elif delta < 0:
        _aplicar(
            produtos[pedido.produto_id],
            MovimentoEstoque.ENTRADA,
            -delta,
            "Estorno de estoque do pedido",
            usuario,
            pedido,
        )


@transaction.atomic
def salvar_novo_pedido(form, usuario):
    form.instance.cliente = usuario
    pedido = form.save()
    _sincronizar(
        pedido=pedido,
        status_anterior=None,
        quantidade_anterior=0,
        produto_anterior_id=pedido.produto_id,
        usuario=usuario,
    )
    return pedido


@transaction.atomic
def salvar_pedido_editado(form, usuario):
    anterior = Pedido.objects.select_for_update().get(pk=form.instance.pk, cliente=usuario)
    form.instance.cliente = anterior.cliente
    pedido = form.save()
    _sincronizar(
        pedido=pedido,
        status_anterior=anterior.status,
        quantidade_anterior=anterior.quantidade,
        produto_anterior_id=anterior.produto_id,
        usuario=usuario,
    )
    return pedido


def estornar_estoque_do_pedido(pedido, usuario):
    """Devolve o estoque de um pedido ainda ativo. Deve rodar dentro de transaction.atomic."""
    bloqueado = Pedido.objects.select_for_update().get(pk=pedido.pk, cliente=usuario)
    if bloqueado.status == "CANCELADO":
        return
    produtos = _produtos_bloqueados(bloqueado.produto_id)
    _aplicar(
        produtos[bloqueado.produto_id],
        MovimentoEstoque.ENTRADA,
        bloqueado.quantidade,
        "Estorno pela exclusão do pedido",
        usuario,
        bloqueado,
    )


@transaction.atomic
def registrar_movimento_manual(*, produto, tipo, quantidade, motivo, usuario):
    produtos = _produtos_bloqueados(produto.pk)
    return _aplicar(produtos[produto.pk], tipo, quantidade, motivo, usuario, None)
