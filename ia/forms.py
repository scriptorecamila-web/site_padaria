from django import forms


class FormularioPergunta(forms.Form):
    pergunta = forms.CharField(
        label="Pergunta",
        max_length=2000,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    conversa = forms.IntegerField(required=False, widget=forms.HiddenInput)
