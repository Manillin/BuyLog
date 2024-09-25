from django.db import models
from django.contrib.auth.models import User
from scontrini.models import Negozio


# Create your models here.

class Review(models.Model):
    utente = models.ForeignKey(Negozio, on_delete=models.CASCADE)
    negozio = models.ForeignKey(
        Negozio, on_delete=models.CASCADE, related_name='recensioni')
    voto = models.IntegerField()
    commento = models.TextField(null=True, blank=False)

    def __str__(self):
        return f"Recensioni di {self.utente.username} per {self.negoizio.home}"
