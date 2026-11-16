from decimal import Decimal

from django import forms

from .models import Encomenda, Pedido, Produto


class PrecoBrasileiroField(forms.DecimalField):
    def prepare_value(self, value):
        if isinstance(value, Decimal):
            return format(value, ".2f").replace(".", ",")
        return value

    def to_python(self, value):
        if isinstance(value, str) and "," in value:
            value = value.strip().replace(".", "").replace(",", ".")
        return super().to_python(value)


class FormularioProduto(forms.ModelForm):
    preco = PrecoBrasileiroField(
        max_digits=8,
        decimal_places=2,
        localize=False,
        widget=forms.TextInput(
            attrs={
                "inputmode": "decimal",
                "data-mask": "000000,00",
                "data-mask-reverse": "true",
            }
        ),
    )

    class Meta:
        model = Produto
        fields = ["nome", "descricao", "categoria", "preco", "quantidade_estoque"]


class FormularioPedido(forms.ModelForm):
    class Meta:
        model = Pedido
        # "cliente" não entra no form: preenchido automaticamente em
        # form_valid() com o request.user.
        fields = ["produto", "quantidade", "status", "observacoes"]


class FormularioEncomenda(forms.ModelForm):
    class Meta:
        model = Encomenda
        # "cliente" também é preenchido automaticamente em form_valid().
        fields = ["produto", "data_retirada", "observacoes", "status"]
        widgets = {
            "data_retirada": forms.DateInput(attrs={"type": "date"}),
        }


class FormularioEmail(forms.Form):
    email = forms.EmailField(label="E-mail cadastrado")
