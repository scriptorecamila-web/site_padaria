from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin


class FiltroClienteMixin:
    """Restringe o queryset aos registros do usuário logado.

    Aplica a regra da 1ª Entrega para classes com FK para User:
      - listar   -> só lista os objetos que o cliente cadastrou
      - detalhar -> só exibe o objeto que o cliente cadastrou
      - editar   -> só permite editar registros do próprio cliente
      - excluir  -> só permite excluir registros do próprio cliente
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(cliente=self.request.user)


class ListaComFiltroMixin:
    filterset_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context


class GrupoNecessarioMixin(UserPassesTestMixin):
    """Libera a view apenas para usuários de um dos grupos informados.

    O controle é pelo grupo do Django (auth.Group), sem exceção por is_staff.
    """

    grupos_permitidos = ("Equipe",)

    def test_func(self):
        return self.request.user.groups.filter(name__in=self.grupos_permitidos).exists()


class MensagemExclusaoMixin:
    success_message = "Registro excluído com sucesso."

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
