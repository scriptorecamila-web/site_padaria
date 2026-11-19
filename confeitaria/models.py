from django.conf import settings
from django.db import models
from django.urls import reverse


class Produto(models.Model):
    """Catálogo de produtos da padaria (pães, bolos, doces). Sem FK para User."""

    CATEGORIA_CHOICES = [
        ("PAO", "Pão"),
        ("BOLO", "Bolo"),
        ("DOCE", "Doce"),
        ("SALGADO", "Salgado"),
        ("BEBIDA", "Bebida"),
    ]

    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    categoria = models.CharField(max_length=10, choices=CATEGORIA_CHOICES, default="PAO")
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    quantidade_estoque = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse("confeitaria:produto_detalhe", kwargs={"pk": self.pk})


class Pedido(models.Model):
    """Pedido feito por um cliente. Possui FK para User (cliente)."""

    STATUS_CHOICES = [
        ("RECEBIDO", "Recebido"),
        ("EM_PREPARO", "Em preparo"),
        ("PRONTO", "Pronto para retirada"),
        ("ENTREGUE", "Entregue"),
        ("CANCELADO", "Cancelado"),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="pedidos")
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pedidos",
    )
    quantidade = models.PositiveIntegerField(default=1)
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="RECEBIDO")
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-data_pedido"]

    def __str__(self):
        return f"Pedido de {self.produto.nome} - {self.cliente}"

    def get_absolute_url(self):
        return reverse("confeitaria:pedido_detalhe", kwargs={"pk": self.pk})


class Encomenda(models.Model):
    """Encomenda especial (ex.: bolo de aniversário) para retirada futura. FK para User."""

    STATUS_CHOICES = [
        ("PENDENTE", "Pendente"),
        ("CONFIRMADA", "Confirmada"),
        ("CANCELADA", "Cancelada"),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="encomendas")
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="encomendas",
    )
    data_retirada = models.DateField()
    observacoes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDENTE")

    class Meta:
        verbose_name = "Encomenda"
        verbose_name_plural = "Encomendas"
        ordering = ["data_retirada"]

    def __str__(self):
        return f"Encomenda de {self.produto.nome} - {self.cliente}"

    def get_absolute_url(self):
        return reverse("confeitaria:encomenda_detalhe", kwargs={"pk": self.pk})


class MovimentoEstoque(models.Model):
    """Entrada ou saída de estoque. A saída do pedido é gerada na mesma transação."""

    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    TIPO_CHOICES = [
        (ENTRADA, "Entrada"),
        (SAIDA, "Saída"),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="movimentos")
    tipo = models.CharField(max_length=8, choices=TIPO_CHOICES)
    quantidade = models.PositiveIntegerField()
    motivo = models.CharField(max_length=200)
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.SET_NULL,
        related_name="movimentos_estoque",
        null=True,
        blank=True,
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimentos_estoque",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimento de estoque"
        verbose_name_plural = "Movimentos de estoque"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.quantidade} × {self.produto}"

    def get_absolute_url(self):
        return reverse("confeitaria:estoque_lista")
