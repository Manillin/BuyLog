from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from scontrini.models import Scontrino, Negozio, ListaProdotti, Prodotto
from django.utils import timezone


class ScontriniViewsTest(TestCase):
    # Questo metodo viene eseguito prima di ogni test
    def setUp(self):
        # crea utente test
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
        self.negozio = Negozio.objects.create(
            nome='Supermercato Test'
        )
        # Aggiungi un prodotto di test
        self.prodotto = Prodotto.objects.create(
            nome='Prodotto Test'
        )
        # Creiamo alcuni scontrini di test
        self.scontrino1 = Scontrino.objects.create(
            utente=self.user,
            negozio=self.negozio,
            data=timezone.now(),
            totale=100.00
        )
        self.scontrino2 = Scontrino.objects.create(
            utente=self.user,
            negozio=self.negozio,
            data=timezone.now(),
            totale=150.00
        )

    def test_lista_scontrini_view_non_autenticato(self):
        # Test accesso alla vista senza autenticazione
        response = self.client.get(reverse('scontrini:lista_scontrini'))
        self.assertEqual(response.status_code, 302)  # Redirect al login

    def test_lista_scontrini_view_autenticato(self):
        # Login dell'utente
        self.client.login(username='testuser', password='12345')
        # Test accesso alla vista con autenticazione
        response = self.client.get(reverse('scontrini:lista_scontrini'))
        self.assertEqual(response.status_code, 200)  # OK
        self.assertTemplateUsed(response, 'scontrini/lista_scontrini.html')
        self.assertEqual(len(response.context['scontrini']), 2)

    def test_dettagli_scontrino_view(self):
        # Accesso alla view con login dell'utente
        self.client.login(username='testuser', password='12345')
        # Test accesso ai dettagli dello scontrino
        response = self.client.get(
            reverse('scontrini:dettagli_scontrino',
                    kwargs={'scontrino_id': self.scontrino1.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scontrini/dettagli_scontrino.html')

    # controllo paginazione nella lista di tutt i gli scontrini

    def test_lista_scontrini_pagination(self):
        self.client.login(username='testuser', password='12345')
        # Creiamo 15 scontrini per testare la paginazione
        for i in range(15):
            Scontrino.objects.create(
                utente=self.user,
                negozio=self.negozio,
                data=timezone.now(),
                totale=100.00
            )

        # Test prima pagina
        response = self.client.get(reverse('scontrini:lista_scontrini'))
        self.assertEqual(response.status_code, 200)
        # 10 per pagina
        self.assertEqual(len(response.context['scontrini']), 10)

        # Test seconda pagina - response contiene le variabili passate al template dalla view
        response = self.client.get(
            reverse('scontrini:lista_scontrini') + '?page=2')
        self.assertEqual(response.status_code, 200)
        # accede al paginator e controlla di essere nella seconda pagina - deve esserci una pagina prima
        self.assertTrue(response.context['scontrini'].has_previous())

    # controllo paginazione nella vista dettaglio scontrino
    def test_dettagli_scontrino_pagination(self):
        self.client.login(username='testuser', password='12345')
        # Creiamo 15 prodotti per lo scontrino
        for i in range(15):
            ListaProdotti.objects.create(
                scontrino=self.scontrino1,
                prodotto=self.prodotto,  # Usa il prodotto di test
                quantita=1,
                prezzo_unitario=10.00
            )

        response = self.client.get(
            reverse('scontrini:dettagli_scontrino',
                    kwargs={'scontrino_id': self.scontrino1.id})
        )
        self.assertEqual(response.status_code, 200)
        # 10 per pagina
        self.assertEqual(len(response.context['prodotti']), 10)
