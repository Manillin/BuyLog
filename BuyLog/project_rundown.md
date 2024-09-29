# Spiegazione Feature Progetto


## Modelli e DB:

Modello Lista Prodotti
```python
class ListaProdotti(models.Model):
    scontrino = models.ForeignKey(Scontrino, on_delete=models.CASCADE, related_name='lista_prodotti')
    prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE)
    quantita = models.IntegerField()
    prezzo_unitario = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f'{self.prodotto.nome} - {self.quantita} x {self.prezzo_unitario} $'

    class Meta:
        verbose_name_plural = 'ListaProdotti'
```

Relazione Molti-a-Molti con Attributi Aggiuntivi:

- **scontrino:** Rappresenta lo scontrino a cui è associata la lista dei prodotti.
- **prodotto:** Rappresenta un singolo prodotto nella lista.
- **quantita:** Rappresenta la quantità del singolo prodotto acquistato.
- **prezzo_unitario:** Rappresenta il prezzo unitario del singolo prodotto al momento dell'acquisto.  

Quando aggiungi prodotti a uno scontrino, stai effettivamente creando più righe nella tabella ListaProdotti, ognuna delle quali rappresenta un singolo prodotto con la sua quantità e il suo prezzo unitario.