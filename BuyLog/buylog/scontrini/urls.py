from django.urls import path
from .views import *


app_name = 'scontrini'

urlpatterns = [
    path('', scontrini_home, name='scontrinilanding'),
    path('carica/', carica_scontrino, name='carica_scontrino'),
    path('successo/', successo, name='successo'),
]
