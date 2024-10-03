from django.urls import path, re_path
from .views import *


app_name = 'scontrini'

urlpatterns = [
    path('', scontrini_home, name='scontrinilanding'),
    path('carica/', carica_scontrino, name='carica_scontrino'),
    path('successo/', successo, name='successo'),
    path('lista/', lista_scontrini, name='lista_scontrini'),
    path('dettagli/<int:scontrino_id>/',
         dettagli_scontrino, name='dettagli_scontrino'),
    path('aggiungi_prodotto/', aggiungi_prodotto, name='aggiungi_prodotto'),
    #  stats:
    path('statistiche/', DashboardView.as_view(), name='dashboard'),
    path('aggiorna_grafico/', aggiorna_grafico, name='aggiorna_grafico')
]
