from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from scontrini.models import Scontrino, Negozio, Prodotto, ListaProdotti
from recensioni.models import Review


class NegozioModelTest(TestCase):
    def setUp(self):
        self.negozio = Negozio.objects.create(nome='Test Negozio')
        self.user = User.objects.create_user('testuser')

    def test_aggiorna_medie_recensioni(self):
        # Test con nessuna recensione
        self.assertIsNone(self.negozio.recensione_media)

        # Aggiungi recensioni e testa la media
        Review.objects.create(
            negozio=self.negozio,
            utente=self.user,
            voto_generale=4
        )
        Review.objects.create(
            negozio=self.negozio,
            utente=User.objects.create_user('testuser2'),
            voto_generale=2
        )

        self.negozio.aggiorna_medie_recensioni()
        self.assertEqual(self.negozio.recensione_media, 3.0)


class ScontrinoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser')
        self.negozio = Negozio.objects.create(nome='Test Negozio')
        self.prodotto = Prodotto.objects.create(nome='Test Prodotto')

    # calcolo del totale per uno scontrino inserendo quantità 3
    def test_calcolo_totale(self):
        scontrino = Scontrino.objects.create(
            utente=self.user,
            negozio=self.negozio,
            data=timezone.now()
        )

        ListaProdotti.objects.create(
            scontrino=scontrino,
            prodotto=self.prodotto,
            quantita=2,
            prezzo_unitario=10.00
        )

        ListaProdotti.objects.create(
            scontrino=scontrino,
            prodotto=self.prodotto,
            quantita=1,
            prezzo_unitario=5.00
        )

        scontrino.calcola_totale()
        self.assertEqual(float(scontrino.totale), 25.00)

    def test_data_futura(self):
        # tentativo di inserire data futura
        with self.assertRaises(ValidationError):
            scontrino = Scontrino(
                utente=self.user,
                negozio=self.negozio,
                data=timezone.now() + timedelta(days=1)
            )
            scontrino.full_clean()
