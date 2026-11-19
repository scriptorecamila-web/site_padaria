from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponseRedirect
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

from .estoque import (
    EstoqueInsuficiente,
    estornar_estoque_do_pedido,
    registrar_movimento_manual,
    salvar_novo_pedido,
    salvar_pedido_editado,
)
from .filters import EncomendaFilter, MovimentoEstoqueFilter, PedidoFilter, ProdutoFilter
from .forms import (
    FormularioEmail,
    FormularioEncomenda,
    FormularioMovimentoEstoque,
    FormularioPedido,
    FormularioProduto,
)
from .mixins import FiltroClienteMixin, GrupoNecessarioMixin, ListaComFiltroMixin, MensagemExclusaoMixin
from .models import Encomenda, MovimentoEstoque, Pedido, Produto


# ---------------------------------------------------------------------------
# Produto (catálogo) — não tem FK para User, então não há filtragem por
# cliente aqui (a regra só se aplica quando a classe tem relação com User
# de chave estrangeira, o que não é o caso de Produto).
# ---------------------------------------------------------------------------
class ListaProdutos(LoginRequiredMixin, ListaComFiltroMixin, ListView):
    model = Produto
    filterset_class = ProdutoFilter
    template_name = "confeitaria/produtos/produto_list.html"
    context_object_name = "produtos"
    paginate_by = 20


class DetalheProduto(LoginRequiredMixin, DetailView):
    model = Produto
    template_name = "confeitaria/produtos/produto_detail.html"
    context_object_name = "produto"


class CriarProduto(LoginRequiredMixin, GrupoNecessarioMixin, SuccessMessageMixin, CreateView):
    model = Produto
    form_class = FormularioProduto
    template_name = "confeitaria/produtos/produto_form.html"
    success_url = reverse_lazy("confeitaria:produto_lista")
    success_message = "Produto cadastrado com sucesso."


class EditarProduto(LoginRequiredMixin, GrupoNecessarioMixin, SuccessMessageMixin, UpdateView):
    model = Produto
    form_class = FormularioProduto
    template_name = "confeitaria/produtos/produto_form.html"
    success_url = reverse_lazy("confeitaria:produto_lista")
    success_message = "Produto atualizado com sucesso."


class ExcluirProduto(LoginRequiredMixin, GrupoNecessarioMixin, MensagemExclusaoMixin, DeleteView):
    model = Produto
    template_name = "confeitaria/produtos/produto_excluir_form.html"
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
    template_name = "confeitaria/pedidos/pedido_list.html"
    context_object_name = "pedidos"
    paginate_by = 20


class DetalhePedido(LoginRequiredMixin, FiltroClienteMixin, DetailView):
    model = Pedido
    template_name = "confeitaria/pedidos/pedido_detail.html"
    context_object_name = "pedido"


class CriarPedido(LoginRequiredMixin, GrupoNecessarioMixin, SuccessMessageMixin, CreateView):
    model = Pedido
    form_class = FormularioPedido
    template_name = "confeitaria/pedidos/pedido_form.html"
    success_url = reverse_lazy("confeitaria:pedido_lista")
    success_message = "Pedido cadastrado com sucesso."
    grupos_permitidos = ("Clientes", "Equipe")

    def form_valid(self, form):
        try:
            self.object = salvar_novo_pedido(form, self.request.user)
        except EstoqueInsuficiente as erro:
            form.add_error("quantidade", erro.mensagem)
            return self.form_invalid(form)
        messages.success(self.request, self.get_success_message(form.cleaned_data))
        return HttpResponseRedirect(self.get_success_url())


class EditarPedido(LoginRequiredMixin, FiltroClienteMixin, SuccessMessageMixin, UpdateView):
    model = Pedido
    form_class = FormularioPedido
    template_name = "confeitaria/pedidos/pedido_form.html"
    success_url = reverse_lazy("confeitaria:pedido_lista")
    success_message = "Pedido atualizado com sucesso."

    def form_valid(self, form):
        try:
            self.object = salvar_pedido_editado(form, self.request.user)
        except EstoqueInsuficiente as erro:
            form.add_error("quantidade", erro.mensagem)
            return self.form_invalid(form)
        messages.success(self.request, self.get_success_message(form.cleaned_data))
        return HttpResponseRedirect(self.get_success_url())


class ExcluirPedido(LoginRequiredMixin, FiltroClienteMixin, MensagemExclusaoMixin, DeleteView):
    model = Pedido
    template_name = "confeitaria/pedidos/pedido_excluir_form.html"
    success_url = reverse_lazy("confeitaria:pedido_lista")
    success_message = "Pedido excluído com sucesso."

    def form_valid(self, form):
        with transaction.atomic():
            estornar_estoque_do_pedido(self.object, self.request.user)
            return super().form_valid(form)


# ---------------------------------------------------------------------------
# Encomenda — mesma lógica de Pedido (tem FK para User).
# ---------------------------------------------------------------------------
class ListaEncomendas(LoginRequiredMixin, FiltroClienteMixin, ListaComFiltroMixin, ListView):
    model = Encomenda
    filterset_class = EncomendaFilter
    template_name = "confeitaria/encomendas/encomenda_list.html"
    context_object_name = "encomendas"
    paginate_by = 20


class DetalheEncomenda(LoginRequiredMixin, FiltroClienteMixin, DetailView):
    model = Encomenda
    template_name = "confeitaria/encomendas/encomenda_detail.html"
    context_object_name = "encomenda"


class CriarEncomenda(LoginRequiredMixin, GrupoNecessarioMixin, SuccessMessageMixin, CreateView):
    model = Encomenda
    form_class = FormularioEncomenda
    template_name = "confeitaria/encomendas/encomenda_form.html"
    success_url = reverse_lazy("confeitaria:encomenda_lista")
    success_message = "Encomenda cadastrada com sucesso."
    grupos_permitidos = ("Clientes", "Equipe")

    def form_valid(self, form):
        form.instance.cliente = self.request.user
        return super().form_valid(form)


class EditarEncomenda(LoginRequiredMixin, FiltroClienteMixin, SuccessMessageMixin, UpdateView):
    model = Encomenda
    form_class = FormularioEncomenda
    template_name = "confeitaria/encomendas/encomenda_form.html"
    success_url = reverse_lazy("confeitaria:encomenda_lista")
    success_message = "Encomenda atualizada com sucesso."


class ExcluirEncomenda(LoginRequiredMixin, FiltroClienteMixin, MensagemExclusaoMixin, DeleteView):
    model = Encomenda
    template_name = "confeitaria/encomendas/encomenda_excluir_form.html"
    success_url = reverse_lazy("confeitaria:encomenda_lista")
    success_message = "Encomenda excluída com sucesso."


class ListaMovimentosEstoque(LoginRequiredMixin, GrupoNecessarioMixin, ListaComFiltroMixin, ListView):
    model = MovimentoEstoque
    filterset_class = MovimentoEstoqueFilter
    template_name = "confeitaria/estoque/estoque_list.html"
    context_object_name = "movimentos"
    paginate_by = 20


class CriarMovimentoEstoque(LoginRequiredMixin, GrupoNecessarioMixin, SuccessMessageMixin, CreateView):
    model = MovimentoEstoque
    form_class = FormularioMovimentoEstoque
    template_name = "confeitaria/estoque/estoque_form.html"
    success_url = reverse_lazy("confeitaria:estoque_lista")
    success_message = "Movimento de estoque registrado com sucesso."

    def form_valid(self, form):
        try:
            self.object = registrar_movimento_manual(
                produto=form.cleaned_data["produto"],
                tipo=form.cleaned_data["tipo"],
                quantidade=form.cleaned_data["quantidade"],
                motivo=form.cleaned_data["motivo"],
                usuario=self.request.user,
            )
        except EstoqueInsuficiente as erro:
            form.add_error("quantidade", erro.mensagem)
            return self.form_invalid(form)
        messages.success(self.request, self.get_success_message(form.cleaned_data))
        return HttpResponseRedirect(self.get_success_url())


class RecuperarUsuario(FormView):
    template_name = "conta/recuperar_usuario_form.html"
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
