from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from confeitaria.models import Produto

from .models import Conversa, Mensagem


class AssistenteTests(TestCase):
    def setUp(self):
        self.cliente = get_user_model().objects.create_user(
            username="cliente-ia",
            email="ia@example.com",
            password="senha-segura-123",
        )
        self.outro = get_user_model().objects.create_user(
            username="outro-ia",
            email="outro-ia@example.com",
            password="senha-segura-123",
        )
        Produto.objects.create(
            nome="Pão francês",
            categoria="PAO",
            preco="1.50",
            quantidade_estoque=20,
        )

    def test_assistente_responde_com_o_cardapio_e_isola_a_conversa(self):
        self.client.force_login(self.cliente)

        resposta = self.client.post(
            reverse("ia:assistente"),
            {"pergunta": "Quanto custa o Pão francês?"},
            follow=True,
        )

        self.assertContains(resposta, "O assistente respondeu à sua pergunta.")
        self.assertContains(resposta, "R$ 1.50")
        self.assertContains(resposta, "Pão")
        self.assertEqual(Conversa.objects.filter(usuario=self.cliente).count(), 1)
        self.assertEqual(Mensagem.objects.filter(papel=Mensagem.ASSISTENTE).count(), 1)

        conversa = Conversa.objects.get()
        self.client.force_login(self.outro)
        resposta_alheia = self.client.get(reverse("ia:assistente"), {"conversa": conversa.pk})
        self.assertNotContains(resposta_alheia, "Pão francês: R$ 1.50")

        resposta_post = self.client.post(
            reverse("ia:assistente"),
            {"pergunta": "E o estoque?", "conversa": conversa.pk},
        )
        self.assertEqual(resposta_post.status_code, 404)

    def test_pedidos_do_assistente_nao_mostram_outro_cliente(self):
        from confeitaria.models import Pedido

        produto = Produto.objects.get()
        Pedido.objects.create(cliente=self.outro, produto=produto, quantidade=4)
        self.client.force_login(self.cliente)

        resposta = self.client.post(
            reverse("ia:assistente"),
            {"pergunta": "Como estão meus pedidos?"},
            follow=True,
        )

        self.assertContains(resposta, "Você ainda não tem pedidos")
        self.assertNotContains(resposta, "Pão francês (4)")
