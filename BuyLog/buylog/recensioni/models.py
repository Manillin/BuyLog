from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from scontrini.models import Negozio
from django.utils import timezone


# Create your models here.

class Review(models.Model):
    utente = models.ForeignKey(User, on_delete=models.CASCADE)
    negozio = models.ForeignKey(
        Negozio, on_delete=models.CASCADE, related_name='recensioni')
    data = models.DateTimeField(default=timezone.now)

    # Valutazioni specifiche
    qualita_prezzo = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1
    )
    pulizia = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1
    )
    servizio = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1
    )
    varieta = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1
    )

    # Valutazione generale e commento
    voto_generale = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1
    )
    commento = models.TextField(max_length=300, null=True, blank=True)

    # Mi piace
    likes = models.ManyToManyField(
        User, related_name='recensioni_liked', blank=True)

    class Meta:
        verbose_name_plural = 'Reviews'
        ordering = ['-data']  # Ordina per data decrescente

    def __str__(self):
        return f"Recensione di {self.utente.username} per {self.negozio.nome}"

    def calcola_media(self):
        return (self.qualita_prezzo + self.pulizia + self.servizio + self.varieta + self.voto_generale) / 5
