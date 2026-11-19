from django.conf import settings
from django.db import models
from django.urls import reverse


class Conversa(models.Model):
    """Conversa do assistente, restrita ao usuário que a iniciou."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversas",
    )
    titulo = models.CharField(max_length=80)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Conversa"
        verbose_name_plural = "Conversas"
        ordering = ["-criada_em"]

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse("ia:assistente") + f"?conversa={self.pk}"


class Mensagem(models.Model):
    USUARIO = "USUARIO"
    ASSISTENTE = "ASSISTENTE"
    PAPEL_CHOICES = [
        (USUARIO, "Usuário"),
        (ASSISTENTE, "Assistente"),
    ]

    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE, related_name="mensagens")
    papel = models.CharField(max_length=12, choices=PAPEL_CHOICES)
    conteudo = models.TextField()
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
        ordering = ["criada_em"]

    def __str__(self):
        return f"{self.get_papel_display()}: {self.conteudo[:40]}"
