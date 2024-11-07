from django import forms
from django.utils import timezone
from datetime import datetime, date, timedelta
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

    def clean_data(self):
        data = self.cleaned_data.get('data')
        if not data:
            raise forms.ValidationError("La data è obbligatoria")

        # Se è una data, convertiamola in datetime
        if isinstance(data, date):
            data = timezone.make_aware(
                datetime.combine(data, datetime.min.time()))

        # Confrontiamo le date
        if data > timezone.now():
            raise forms.ValidationError("La data non può essere nel futuro")

        return data

    def clean(self):
        cleaned_data = super().clean()
        if 'data' not in cleaned_data:
            return cleaned_data
        return cleaned_data


class ListaProdottiForm(forms.ModelForm):
    prodotto = forms.CharField(
        max_length=100, required=True, label="Nome del Prodotto")

    class Meta:
        model = ListaProdotti
        fields = ['quantita', 'prezzo_unitario']

    def clean_quantita(self):
        quantita = self.cleaned_data.get('quantita')
        if quantita <= 0:
            raise forms.ValidationError(
                "La quantità deve essere maggiore di zero")
        return quantita

    def clean_prezzo_unitario(self):
        prezzo = self.cleaned_data.get('prezzo_unitario')
        if prezzo <= 0:
            raise forms.ValidationError(
                "Il prezzo deve essere maggiore di zero")
        return prezzo


class NegozioForm(forms.ModelForm):
    class Meta:
        model = Negozio
        fields = ['nome']


class ProdottoForm(forms.ModelForm):
    class Meta:
        model = Prodotto
        fields = ['nome']
