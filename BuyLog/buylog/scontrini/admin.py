from django.contrib import admin
from .models import Negozio, Prodotto, Scontrino, ListaProdotti

# Register your models here.

admin.site.register(Negozio)
admin.site.register(Prodotto)
admin.site.register(Scontrino)
admin.site.register(ListaProdotti)
