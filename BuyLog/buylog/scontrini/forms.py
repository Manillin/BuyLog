from django import forms
from django.utils import timezone
from .models import *


class ScontrinoForm(forms.ModelForm):
    # Campo per inserire il nome del negozio manualmente
    negozio_nome = forms.CharField(
        max_length=100, required=True, label='Nome del Negozio')

    class Meta:
        model = Scontrino
        fields = ['data']
        widgets = {
            # Widget per selezionare solo la data
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'negozio_nome': forms.TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(ScontrinoForm, self).__init__(*args, **kwargs)
        # Imposta la data odierna come valore di default
        self.fields['data'].initial = timezone.now().date()
        # Format data
        self.fields['data'].widget.format = '%Y-%m-%d'
        self.fields['data'].input_formats = ['%Y-%m-%d']


class ListaProdottiForm(forms.ModelForm):
    prodotto = forms.CharField(
        max_length=100, required=True, label="Nome del Prodotto")

    class Meta:
        model = ListaProdotti
        fields = ['quantita', 'prezzo_unitario']


class NegozioForm(forms.ModelForm):
    class Meta:
        model = Negozio
        fields = ['nome']


class ProdottoForm(forms.ModelForm):
    class Meta:
        model = Prodotto
        fields = ['nome']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image']


class UserUpdateForm(forms.ModelForm):
    model = User
    fields = ['first_name', 'last_name', 'email']
