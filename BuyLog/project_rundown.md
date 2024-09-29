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



## Views:

### crea_scotrino():

Questa view crea uno scontrino, lo scontrino collega un utente a un negozio in una data. Per collegare i prodotti acquistati si usa un Modello intermediario `ListaProdotti`che collega una lista di prodotti a uno specifico scontrino.  

Per salvare una lista di prodotti in uno specifico scontrino si usa il concetto di sessione in django.  
In particolare si salvano i prodotti in : `request.session['prodotti']` che è una lista di dizionari!  

es: aggiunta mela e pera come prodotti durante la sessione, in request.session['prodotti'] avremo:

```python
[
    {'prodotto': 'mela', 'quantita': 3, 'prezzo_unitario': 1.2},
    {'prodotto': 'pera', 'quantita': 2, 'prezzo_unitario': 0.9}
]
```

Nella view per salvare tutti i prodotti a uno scontrino si fa questo:

```python
# Aggiungiamo i prodotti salvati dalla sessione allo scontrino
for prodotto_dati in request.session['prodotti']:
    prodotto_nome = prodotto_dati['prodotto']
    prodotto_nome_pulito = slugify(
        prodotto_nome, allow_unicode=True).replace("-", "").lower()

    # Controllo se prodotto esiste, se non esiste lo creo nel DB
    prodotto = Prodotto.objects.filter(
        nome__iexact=prodotto_nome_pulito).first()
    if not prodotto:
        prodotto = Prodotto.objects.create(nome=prodotto_nome)

    # Aggiungiamo il prodotto alla lista
    ListaProdotti.objects.create(
        scontrino=scontrino,
        prodotto=prodotto,
        quantita=prodotto_dati['quantita'],
        prezzo_unitario=prodotto_dati['prezzo_unitario']
    )
```

quando si fa `prodotto_nome = prodotto_dati['prodotto']` si sta accedendo alla chiave prodotto di ogni dizionario nella lista.  
Poiché si sta iterando su request.session['prodotti'], prodotto_dati rappresenta ogni dizionario nella lista, quindi prodotto_dati['prodotto'] ti dà il nome del prodotto corrente nell'iterazione. (prima mela e poi pera)  

