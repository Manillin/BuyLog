from django.contrib import admin
from .models import Negozio, Prodotto, Scontrino, ListaProdotti, Profile

# Register your models here.

admin.site.register(Negozio)
admin.site.register(Prodotto)
admin.site.register(Scontrino)
admin.site.register(ListaProdotti)
admin.site.register(Profile)
