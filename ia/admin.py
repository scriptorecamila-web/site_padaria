from django.contrib import admin

from .models import Conversa, Mensagem


class MensagemInline(admin.TabularInline):
    model = Mensagem
    extra = 0
    readonly_fields = ("papel", "conteudo", "criada_em")


@admin.register(Conversa)
class ConversaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "criada_em")
    inlines = [MensagemInline]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(usuario=request.user)

    def save_model(self, request, obj, form, change):
        obj.usuario = request.user
        super().save_model(request, obj, form, change)
