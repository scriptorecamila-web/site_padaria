from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)

from .filters import EncomendaFilter, PedidoFilter, ProdutoFilter
from .forms import FormularioEmail, FormularioEncomenda, FormularioPedido, FormularioProduto
from .mixins import FiltroClienteMixin, ListaComFiltroMixin, MensagemExclusaoMixin
from .models import Encomenda, Pedido, Produto


# ---------------------------------------------------------------------------
# Produto (catálogo) — não tem FK para User, então não há filtragem por
# cliente aqui (a regra só se aplica quando a classe tem relação com User
# de chave estrangeira, o que não é o caso de Produto).
# ---------------------------------------------------------------------------
class ListaProdutos(LoginRequiredMixin, ListaComFiltroMixin, ListView):
    model = Produto
    filterset_class = ProdutoFilter
    template_name = "confeitaria/produtos/lista.html"
    context_object_name = "produtos"
    paginate_by = 20


class DetalheProduto(LoginRequiredMixin, DetailView):
    model = Produto
    template_name = "confeitaria/produtos/detalhe.html"
    context_object_name = "produto"


class CriarProduto(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Produto
    form_class = FormularioProduto
    template_name = "confeitaria/produtos/formulario.html"
    success_url = reverse_lazy("confeitaria:produto_lista")
    success_message = "Produto cadastrado com sucesso."


class EditarProduto(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Produto
    form_class = FormularioProduto
    template_name = "confeitaria/produtos/formulario.html"
    success_url = reverse_lazy("confeitaria:produto_lista")
    success_message = "Produto atualizado com sucesso."


class ExcluirProduto(LoginRequiredMixin, MensagemExclusaoMixin, DeleteView):
    model = Produto
    template_name = "confeitaria/produtos/excluir.html"
    success_url = reverse_lazy("confeitaria:produto_lista")
    success_message = "Produto excluído com sucesso."


# ---------------------------------------------------------------------------
# Pedido — tem FK para User (cliente). Regras aplicadas:
#   inserir  -> guarda o cliente logado no atributo "cliente" (form_valid)
#   editar   -> só permite editar pedidos do próprio cliente
#   excluir  -> só permite excluir pedidos do próprio cliente
#   listar   -> só lista os pedidos que o cliente fez
#   detalhar -> só exibe o pedido que o cliente fez
#
# O acesso permanece restrito ao cliente proprietário, inclusive para
# usuários com permissões administrativas.
# ---------------------------------------------------------------------------
class ListaPedidos(LoginRequiredMixin, FiltroClienteMixin, ListaComFiltroMixin, ListView):
    model = Pedido
    filterset_class = PedidoFilter
    template_name = "confeitaria/pedidos/lista.html"
    context_object_name = "pedidos"
    paginate_by = 20


class DetalhePedido(LoginRequiredMixin, FiltroClienteMixin, DetailView):
    model = Pedido
    template_name = "confeitaria/pedidos/detalhe.html"
    context_object_name = "pedido"


class CriarPedido(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Pedido
    form_class = FormularioPedido
    template_name = "confeitaria/pedidos/formulario.html"
    success_url = reverse_lazy("confeitaria:pedido_lista")
    success_message = "Pedido cadastrado com sucesso."

    def form_valid(self, form):
        form.instance.cliente = self.request.user
        return super().form_valid(form)


class EditarPedido(LoginRequiredMixin, FiltroClienteMixin, SuccessMessageMixin, UpdateView):
    model = Pedido
    form_class = FormularioPedido
    template_name = "confeitaria/pedidos/formulario.html"
    success_url = reverse_lazy("confeitaria:pedido_lista")
    success_message = "Pedido atualizado com sucesso."


class ExcluirPedido(LoginRequiredMixin, FiltroClienteMixin, MensagemExclusaoMixin, DeleteView):
    model = Pedido
    template_name = "confeitaria/pedidos/excluir.html"
    success_url = reverse_lazy("confeitaria:pedido_lista")
    success_message = "Pedido excluído com sucesso."


# ---------------------------------------------------------------------------
# Encomenda — mesma lógica de Pedido (tem FK para User).
# ---------------------------------------------------------------------------
class ListaEncomendas(LoginRequiredMixin, FiltroClienteMixin, ListaComFiltroMixin, ListView):
    model = Encomenda
    filterset_class = EncomendaFilter
    template_name = "confeitaria/encomendas/lista.html"
    context_object_name = "encomendas"
    paginate_by = 20


class DetalheEncomenda(LoginRequiredMixin, FiltroClienteMixin, DetailView):
    model = Encomenda
    template_name = "confeitaria/encomendas/detalhe.html"
    context_object_name = "encomenda"


class CriarEncomenda(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Encomenda
    form_class = FormularioEncomenda
    template_name = "confeitaria/encomendas/formulario.html"
    success_url = reverse_lazy("confeitaria:encomenda_lista")
    success_message = "Encomenda cadastrada com sucesso."

    def form_valid(self, form):
        form.instance.cliente = self.request.user
        return super().form_valid(form)


class EditarEncomenda(LoginRequiredMixin, FiltroClienteMixin, SuccessMessageMixin, UpdateView):
    model = Encomenda
    form_class = FormularioEncomenda
    template_name = "confeitaria/encomendas/formulario.html"
    success_url = reverse_lazy("confeitaria:encomenda_lista")
    success_message = "Encomenda atualizada com sucesso."


class ExcluirEncomenda(LoginRequiredMixin, FiltroClienteMixin, MensagemExclusaoMixin, DeleteView):
    model = Encomenda
    template_name = "confeitaria/encomendas/excluir.html"
    success_url = reverse_lazy("confeitaria:encomenda_lista")
    success_message = "Encomenda excluída com sucesso."


class RecuperarUsuario(FormView):
    template_name = "conta/recuperar_usuario.html"
    form_class = FormularioEmail
    success_url = reverse_lazy("confeitaria:recuperar_usuario")

    def form_valid(self, form):
        usuarios = get_user_model().objects.filter(
            email__iexact=form.cleaned_data["email"],
            is_active=True,
        ).order_by("pk")
        if usuarios.exists():
            nomes = "\n".join(usuario.get_username() for usuario in usuarios)
            send_mail(
                subject="Recuperação do usuário - Padaria Doce & Ponto",
                message=(
                    "Você solicitou a recuperação do usuário cadastrado neste e-mail.\n\n"
                    f"Usuário(s):\n{nomes}\n\n"
                    f"Acesse {self.request.build_absolute_uri(reverse('confeitaria:entrar'))} "
                    "para entrar ou recuperar sua senha."
                ),
                from_email=None,
                recipient_list=[form.cleaned_data["email"]],
                fail_silently=False,
            )
        messages.success(
            self.request,
            "Se houver uma conta ativa com esse e-mail, enviaremos as instruções.",
        )
        return super().form_valid(form)
