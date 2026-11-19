from django.contrib.auth import views as views_autenticacao
from django.urls import path
from django.urls import reverse_lazy

from . import views

app_name = "confeitaria"

urlpatterns = [
    # ---- Produto (catálogo) ----
    path("produtos/", views.ListaProdutos.as_view(), name="produto_lista"),
    path("produtos/<int:pk>/", views.DetalheProduto.as_view(), name="produto_detalhe"),
    path("produtos/novo/", views.CriarProduto.as_view(), name="produto_criar"),
    path("produtos/<int:pk>/editar/", views.EditarProduto.as_view(), name="produto_editar"),
    path("produtos/<int:pk>/excluir/", views.ExcluirProduto.as_view(), name="produto_excluir"),

    # ---- Pedido ----
    path("pedidos/", views.ListaPedidos.as_view(), name="pedido_lista"),
    path("pedidos/<int:pk>/", views.DetalhePedido.as_view(), name="pedido_detalhe"),
    path("pedidos/novo/", views.CriarPedido.as_view(), name="pedido_criar"),
    path("pedidos/<int:pk>/editar/", views.EditarPedido.as_view(), name="pedido_editar"),
    path("pedidos/<int:pk>/excluir/", views.ExcluirPedido.as_view(), name="pedido_excluir"),

    # ---- Encomenda ----
    path("encomendas/", views.ListaEncomendas.as_view(), name="encomenda_lista"),
    path("encomendas/<int:pk>/", views.DetalheEncomenda.as_view(), name="encomenda_detalhe"),
    path("encomendas/novo/", views.CriarEncomenda.as_view(), name="encomenda_criar"),
    path("encomendas/<int:pk>/editar/", views.EditarEncomenda.as_view(), name="encomenda_editar"),
    path("encomendas/<int:pk>/excluir/", views.ExcluirEncomenda.as_view(), name="encomenda_excluir"),

    # ---- Autenticação: entrar, sair e alterar senha ----
    path(
        "entrar/",
        views_autenticacao.LoginView.as_view(template_name="conta/entrar_form.html"),
        name="entrar",
    ),
    path("sair/", views_autenticacao.LogoutView.as_view(), name="sair"),
    path(
        "senha/alterar/",
        views_autenticacao.PasswordChangeView.as_view(
            template_name="conta/alterar_senha_form.html",
            success_url="/senha/alterada/",
        ),
        name="alterar_senha",
    ),
    path(
        "senha/alterada/",
        views_autenticacao.PasswordChangeDoneView.as_view(
            template_name="conta/senha_alterada_detail.html"
        ),
        name="senha_alterada",
    ),
    path(
        "senha/recuperar/",
        views_autenticacao.PasswordResetView.as_view(
            template_name="conta/recuperar_senha_form.html",
            email_template_name="conta/email_recuperar_senha.txt",
            subject_template_name="conta/assunto_recuperar_senha.txt",
            success_url=reverse_lazy("confeitaria:senha_recuperacao_enviada"),
        ),
        name="recuperar_senha",
    ),
    path(
        "senha/recuperacao-enviada/",
        views_autenticacao.PasswordResetDoneView.as_view(
            template_name="conta/senha_recuperacao_enviada_detail.html"
        ),
        name="senha_recuperacao_enviada",
    ),
    path(
        "senha/redefinir/<uidb64>/<token>/",
        views_autenticacao.PasswordResetConfirmView.as_view(
            template_name="conta/redefinir_senha_form.html",
            success_url=reverse_lazy("confeitaria:senha_redefinida"),
        ),
        name="redefinir_senha",
    ),
    path(
        "senha/redefinida/",
        views_autenticacao.PasswordResetCompleteView.as_view(
            template_name="conta/senha_redefinida_detail.html"
        ),
        name="senha_redefinida",
    ),
    path(
        "usuario/recuperar/",
        views.RecuperarUsuario.as_view(),
        name="recuperar_usuario",
    ),

    path("estoque/", views.ListaMovimentosEstoque.as_view(), name="estoque_lista"),
    path("estoque/novo/", views.CriarMovimentoEstoque.as_view(), name="estoque_criar"),
]
