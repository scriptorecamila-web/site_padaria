from datetime import date, timedelta

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from .admin import PedidoAdmin
from .forms import FormularioProduto
from .models import Encomenda, Pedido, Produto


class FuncionalidadesProjetoTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.cliente = user_model.objects.create_user(
            username="cliente",
            email="cliente@example.com",
            password="senha-segura-123",
        )
        self.produto = Produto.objects.create(
            nome="Bolo de cenoura",
            categoria="BOLO",
            preco="12.50",
            quantidade_estoque=5,
        )

    def test_pedido_e_encomenda_sao_criados_para_usuario_autenticado(self):
        self.client.force_login(self.cliente)

        resposta_pedido = self.client.post(
            reverse("confeitaria:pedido_criar"),
            {"produto": self.produto.pk, "quantidade": 2, "observacoes": ""},
        )
        resposta_encomenda = self.client.post(
            reverse("confeitaria:encomenda_criar"),
            {
                "produto": self.produto.pk,
                "data_retirada": (date.today() + timedelta(days=2)).isoformat(),
                "observacoes": "",
            },
        )

        self.assertEqual(resposta_pedido.status_code, 302)
        self.assertEqual(resposta_encomenda.status_code, 302)
        self.assertEqual(Pedido.objects.get().cliente, self.cliente)
        self.assertEqual(Encomenda.objects.get().cliente, self.cliente)

    def test_usuario_staff_nao_acessa_registro_de_outro_cliente(self):
        administrador = get_user_model().objects.create_user(
            username="admin-staff",
            email="staff@example.com",
            password="senha-segura-123",
            is_staff=True,
        )
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            produto=self.produto,
            quantidade=1,
        )
        self.client.force_login(administrador)

        resposta_lista = self.client.get(reverse("confeitaria:pedido_lista"))
        resposta_detalhe = self.client.get(
            reverse("confeitaria:pedido_detalhe", args=[pedido.pk])
        )
        resposta_edicao = self.client.get(
            reverse("confeitaria:pedido_editar", args=[pedido.pk])
        )
        resposta_exclusao = self.client.get(
            reverse("confeitaria:pedido_excluir", args=[pedido.pk])
        )

        self.assertNotContains(resposta_lista, "Bolo de cenoura")
        self.assertEqual(resposta_detalhe.status_code, 404)
        self.assertEqual(resposta_edicao.status_code, 404)
        self.assertEqual(resposta_exclusao.status_code, 404)

    def test_admin_tambem_restringe_pedidos_ao_proprietario(self):
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            produto=self.produto,
            quantidade=1,
        )
        request = RequestFactory().get("/admin/confeitaria/pedido/")
        request.user = get_user_model().objects.create_user(
            username="staff",
            password="senha-segura-123",
            is_staff=True,
        )
        admin_pedido = PedidoAdmin(Pedido, AdminSite())

        self.assertNotIn(pedido, admin_pedido.get_queryset(request))

    def test_filtro_de_produtos_e_paginacao_preservam_parametros(self):
        for numero in range(21):
            Produto.objects.create(
                nome=f"Bolo teste {numero:02}",
                categoria="BOLO",
                preco="10.00",
                quantidade_estoque=1,
            )
        self.client.force_login(self.cliente)

        resposta = self.client.get(
            reverse("confeitaria:produto_lista"),
            {"nome": "Bolo teste", "page": 2},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context["paginator"].count, 21)
        self.assertContains(resposta, "nome=Bolo+teste&amp;page=1")

    def test_preco_brasileiro_com_virgula_e_aceito(self):
        formulario = FormularioProduto(
            data={
                "nome": "Pão doce",
                "descricao": "",
                "categoria": "PAO",
                "preco": "12,50",
                "quantidade_estoque": 3,
            }
        )

        self.assertTrue(formulario.is_valid(), formulario.errors)
        self.assertEqual(str(formulario.cleaned_data["preco"]), "12.50")

    def test_cadastro_de_produto_exibe_mensagem_de_sucesso(self):
        self.client.force_login(self.cliente)

        resposta = self.client.post(
            reverse("confeitaria:produto_criar"),
            {
                "nome": "Pão doce",
                "descricao": "",
                "categoria": "PAO",
                "preco": "12,50",
                "quantidade_estoque": 3,
            },
            follow=True,
        )

        self.assertContains(resposta, "Produto cadastrado com sucesso.")
        self.assertTrue(Produto.objects.filter(nome="Pão doce").exists())

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_recuperacao_de_usuario_envia_email_sem_revelar_se_existe(self):
        resposta = self.client.post(
            reverse("confeitaria:recuperar_usuario"),
            {"email": self.cliente.email},
        )

        self.assertRedirects(resposta, reverse("confeitaria:recuperar_usuario"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.cliente.username, mail.outbox[0].body)

        mail.outbox.clear()
        resposta_inexistente = self.client.post(
            reverse("confeitaria:recuperar_usuario"),
            {"email": "nao-existe@example.com"},
        )
        self.assertRedirects(resposta_inexistente, reverse("confeitaria:recuperar_usuario"))
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_recuperacao_de_senha_envia_link_de_redefinicao(self):
        resposta = self.client.post(
            reverse("confeitaria:recuperar_senha"),
            {"email": self.cliente.email},
        )

        self.assertRedirects(
            resposta,
            reverse("confeitaria:senha_recuperacao_enviada"),
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("senha/redefinir/", mail.outbox[0].body)
