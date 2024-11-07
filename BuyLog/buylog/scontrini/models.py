from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Negozio(models.Model):
    nome = models.CharField(max_length=100)
    recensione_media = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.nome

    def aggiorna_medie_recensioni(self):
        recensioni = self.recensioni.all()
        if recensioni:
            self.recensione_media = recensioni.aggregate(
                Avg('voto_generale'))['voto_generale__avg']
            self.save()
        return self.recensione_media

    class Meta:
        verbose_name_plural = 'Negozi'


class Prodotto(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = 'Prodotti'


class Scontrino(models.Model):
    utente = models.ForeignKey(User, on_delete=models.CASCADE)
    negozio = models.ForeignKey(Negozio, on_delete=models.CASCADE)
    data = models.DateTimeField()
    totale = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)  # Aggiungi questo campo

    def __str__(self):
        return f'Acquisto in: {self.negozio.nome} del {self.data}'

    class Meta:
        verbose_name_plural = 'Scontrini'

    def clean(self):
        cleaned_data = super().clean()
        if hasattr(self, 'data') and self.data:
            if self.data > timezone.now():
                raise ValidationError(
                    {'data': "La data non può essere nel futuro"})
        return cleaned_data

    def calcola_totale(self):
        totale = self.prodotti.aggregate(
            total=models.Sum(models.F('quantita') *
                             models.F('prezzo_unitario'))
        )['total'] or 0
        self.totale = totale
        self.save()
        return totale


class ListaProdotti(models.Model):
    scontrino = models.ForeignKey(
        Scontrino, on_delete=models.CASCADE, related_name='prodotti')
    prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE)
    quantita = models.IntegerField()
    prezzo_unitario = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f'{self.prodotto.nome} - {self.quantita} x {self.prezzo_unitario} $'

    class Meta:
        verbose_name_plural = 'ListaProdotti'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(
        upload_to='profile_images/', default='default_pfp.jpeg')

    def __str__(self):
        return f"{self.user.username} Profile"


@receiver(post_save, sender=ListaProdotti)
def aggiorna_totale_scontrino(sender, instance, **kwargs):
    instance.scontrino.calcola_totale()
