from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from scontrini.forms import ScontrinoForm, ListaProdottiForm
from scontrini.models import Negozio, Prodotto


class ScontrinoFormTest(TestCase):
    # controllo inserimento date future
    def test_data_futura(self):
        data_futura = timezone.now().date() + timedelta(days=1)
        form_data = {
            'data': data_futura,
            'negozio_nome': 'Test Negozio'
        }
        form = ScontrinoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('data', form.errors)
    # controllo negozio vuoto - errore specifico per campo negozio_nome

    def test_negozio_nome_vuoto(self):
        form_data = {
            'data': timezone.now().date(),
            'negozio_nome': ''
        }
        form = ScontrinoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('negozio_nome', form.errors)


class ListaProdottiFormTest(TestCase):
    # test quantità negativa -1 - errore nel campo quantita
    def test_quantita_negativa(self):
        form_data = {
            'prodotto': 'Test Prodotto',
            'quantita': -1,
            'prezzo_unitario': 10.00
        }
        form = ListaProdottiForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantita', form.errors)

    def test_prezzo_negativo(self):
        # test prezzo negativa -10 - errore nel campo prezzo
        form_data = {
            'prodotto': 'Test Prodotto',
            'quantita': 1,
            'prezzo_unitario': -10.00
        }
        form = ListaProdottiForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('prezzo_unitario', form.errors)
