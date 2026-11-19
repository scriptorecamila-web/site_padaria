from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView, ListView

from confeitaria.mixins import ListaComFiltroMixin

from .filters import ConversaFilter
from .forms import FormularioPergunta
from .models import Conversa, Mensagem
from .servico import gerar_resposta


class Assistente(LoginRequiredMixin, FormView):
    template_name = "assistente.html"
    form_class = FormularioPergunta

    def get_initial(self):
        initial = super().get_initial()
        conversa = self.request.GET.get("conversa")
        if conversa:
            initial["conversa"] = conversa
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversas = Conversa.objects.filter(usuario=self.request.user)
        context["conversas"] = conversas
        conversa_id = self.request.POST.get("conversa") or self.request.GET.get("conversa")
        conversa = conversas.filter(pk=conversa_id).first() if conversa_id else None
        context["conversa_atual"] = conversa
        context["mensagens_conversa"] = conversa.mensagens.all() if conversa else []
        return context

    def form_valid(self, form):
        conversa_id = form.cleaned_data.get("conversa")
        if conversa_id:
            conversa = get_object_or_404(Conversa, pk=conversa_id, usuario=self.request.user)
        else:
            conversa = Conversa.objects.create(
                usuario=self.request.user,
                titulo=form.cleaned_data["pergunta"][:80],
            )
        Mensagem.objects.create(
            conversa=conversa,
            papel=Mensagem.USUARIO,
            conteudo=form.cleaned_data["pergunta"],
        )
        Mensagem.objects.create(
            conversa=conversa,
            papel=Mensagem.ASSISTENTE,
            conteudo=gerar_resposta(form.cleaned_data["pergunta"], self.request.user),
        )
        messages.success(self.request, "O assistente respondeu à sua pergunta.")
        return redirect(f"{reverse('ia:assistente')}?conversa={conversa.pk}")


class ListaConversas(LoginRequiredMixin, ListaComFiltroMixin, ListView):
    model = Conversa
    filterset_class = ConversaFilter
    template_name = "conversa_list.html"
    context_object_name = "conversas"
    paginate_by = 10

    def get_queryset(self):
        queryset = Conversa.objects.filter(usuario=self.request.user)
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs
