import json
import unicodedata
import urllib.error
import urllib.request

from django.conf import settings

from confeitaria.models import Encomenda, Pedido, Produto


def _normalizar(texto):
    sem_acento = unicodedata.normalize("NFKD", texto or "")
    return "".join(caractere for caractere in sem_acento if not unicodedata.combining(caractere)).casefold()


def _catalogo():
    return list(Produto.objects.all().order_by("nome"))


def _texto_catalogo(produtos):
    if not produtos:
        return "Nenhum produto cadastrado."
    return "\n".join(
        f"- {produto.nome} | {produto.get_categoria_display()} | R$ {produto.preco} | estoque {produto.quantidade_estoque}"
        for produto in produtos
    )


def _responder_local(pergunta, produtos, usuario=None):
    texto = _normalizar(pergunta)
    citados = [produto for produto in produtos if _normalizar(produto.nome) in texto]
    if citados and "pedido" not in texto and "encomenda" not in texto:
        linhas = [
            f"{produto.nome}: R$ {produto.preco}, {produto.quantidade_estoque} em estoque ({produto.get_categoria_display()})."
            for produto in citados
        ]
        return "Encontrei no cardápio:\n" + "\n".join(linhas)

    if any(palavra in texto for palavra in ("cardapio", "produto", "estoque", "preco", "disponivel")) and "pedido" not in texto and "encomenda" not in texto:
        disponiveis = [produto for produto in produtos if produto.quantidade_estoque > 0]
        if not disponiveis:
            return "O cardápio não tem produtos com estoque no momento."
        linhas = [
            f"- {produto.nome} ({produto.get_categoria_display()}): R$ {produto.preco}, {produto.quantidade_estoque} un."
            for produto in disponiveis
        ]
        return "Produtos disponíveis agora:\n" + "\n".join(linhas)

    if "encomenda" in texto:
        return _texto_encomendas(usuario)
    if "pedido" in texto:
        return _texto_pedidos(usuario)

    return (
        "Posso consultar o cardápio, os preços e o estoque da padaria. "
        "Pergunte quais produtos estão disponíveis ou cite o nome de um item."
    )


def _texto_pedidos(usuario):
    if usuario is None or not getattr(usuario, "is_authenticated", False):
        return "Entre na sua conta para consultar pedidos."
    pedidos = list(
        Pedido.objects.filter(cliente=usuario).select_related("produto").order_by("-data_pedido")[:5]
    )
    if not pedidos:
        return (
            "Você ainda não tem pedidos. Eles ficam ligados somente à sua conta, "
            "e o estoque é baixado na mesma transação em que o pedido é salvo."
        )
    linhas = [
        f"- {pedido.produto.nome} ({pedido.quantidade}) — {pedido.get_status_display()}"
        for pedido in pedidos
    ]
    return "Estes são os seus pedidos mais recentes:\n" + "\n".join(linhas)


def _texto_encomendas(usuario):
    if usuario is None or not getattr(usuario, "is_authenticated", False):
        return "Entre na sua conta para consultar encomendas."
    encomendas = list(
        Encomenda.objects.filter(cliente=usuario).select_related("produto").order_by("data_retirada")[:5]
    )
    if not encomendas:
        return "Você ainda não tem encomendas. Cada encomenda fica visível só para quem a criou."
    linhas = [
        (
            f"- {encomenda.produto.nome} — retirada em "
            f"{encomenda.data_retirada.strftime('%d/%m/%Y')} — {encomenda.get_status_display()}"
        )
        for encomenda in encomendas
    ]
    return "Estas são as suas encomendas:\n" + "\n".join(linhas)


def _chamar_api(pergunta, produtos, usuario=None):
    corpo = {
        "model": settings.IA_MODELO or "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é o assistente da Padaria Doce & Ponto. "
                    "Responda em português e use somente o cardápio informado. "
                    "Não invente produto, preço ou estoque. "
                    "Fale de pedidos e encomendas somente com os dados deste usuário.\n\n"
                    f"Cardápio:\n{_texto_catalogo(produtos)}\n\n"
                    f"{_texto_pedidos(usuario)}\n\n{_texto_encomendas(usuario)}"
                ),
            },
            {"role": "user", "content": pergunta},
        ],
    }
    requisicao = urllib.request.Request(
        settings.IA_API_URL,
        data=json.dumps(corpo).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.IA_API_KEY}",
        },
        method="POST",
    )
    with urllib.request.urlopen(requisicao, timeout=20) as resposta:
        dados = json.loads(resposta.read().decode())
    return dados["choices"][0]["message"]["content"].strip()


def gerar_resposta(pergunta, usuario=None):
    produtos = _catalogo()
    if settings.IA_API_KEY and settings.IA_API_URL:
        try:
            return _chamar_api(pergunta, produtos, usuario)
        except (OSError, TimeoutError, ValueError, KeyError, json.JSONDecodeError, urllib.error.URLError):
            pass
    return _responder_local(pergunta, produtos, usuario)
