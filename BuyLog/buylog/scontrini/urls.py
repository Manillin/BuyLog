from django.urls import path, re_path
from .views import *


app_name = 'scontrini'

urlpatterns = [
    re_path(r"^$|^statistiche$|^stats$",
            DashboardView.as_view(), name='dashboard'),
    path('carica/', carica_scontrino, name='carica_scontrino'),
    path('successo/', successo, name='successo'),
    path('lista/', lista_scontrini, name='lista_scontrini'),
    path('dettagli/<int:scontrino_id>/',
         dettagli_scontrino, name='dettagli_scontrino'),
    path('elimina_scontrino/<int:scontrino_id>',
         elimina_scontrino, name='elimina_scontrino'),
    path('aggiungi_prodotto/', aggiungi_prodotto, name='aggiungi_prodotto'),
    #  stats:
    # path('statistiche/', DashboardView.as_view(), name='dashboard'),
    path('aggiorna_grafico/', aggiorna_grafico, name='aggiorna_grafico'),

    # global stats & search
    path('tutti_prodotti/', TuttiProdottiView.as_view(), name='tutti_prodotti'),
    path('tutti_supermercati/', TuttiSupermercatiView.as_view(),
         name='tutti_supermercati'),
    path('aggiorna_tabella_supermercati/', aggiorna_tabella_supermercati,
         name='aggiorna_tabella_supermercati'),
    path('aggiorna_tabella_prodotti/', aggiorna_tabella_prodotti,
         name='aggiorna_tabella_prodotti'),


    path('demo/', DemoStatsView.as_view(), name='demo'),
    path('aggiorna_grafico_demo/', aggiorna_grafico_demo,
         name='aggiorna_grafico_demo'),


    # Ricerca e dattaglio prodotto
    path('ricerca_prodotto/', RicercaProdottoView.as_view(),
         name='ricerca_prodotto'),
    path('prodotto/<int:pk>/', DettagliProdottoView.as_view(),
         name='dettagli_prodotto'),


]
