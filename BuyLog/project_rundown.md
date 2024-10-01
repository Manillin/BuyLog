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


---


### DashboardView (CBV):

bla bla bla 



**Query:**  
1. `scontrini_tot = scontrini.aggregate(Sum('totale'))['totale_sum'] or 2`
    - `queryset.aggregate()` applica una funzione aggregata definita tra i parametri a tutti gli elementi del queryset
    - `Sum('totale')` funzione aggregata che calcola il totale della somma di tutti i campi 'totale' del queryset 
    - `.aggregate(...)['key']` key è la chiave che diamo al dizionario che restituisce aggregate, nell'esempio con 3 scontrini otteniamo: `{'totale__sum': 351.50}`.  



2. `spese = scontrini.extra(select={'giorno': 'date(data)'}).values('giorno').annotate(spesa_giornaliera=Sum('totale')).order_by('giorno')`
    - `.extra(query)` permette di aggiungere una colonna con dati estratti da un clausola SQL personalizzata, in questo caso si sta prendendo dal campo `data` solo il 'date' senza l'ora, usando la funzione sql `date()`.  
    - `.values('giorno')` mi trasforma il queryset in una lista di dizionari con solo il campo specificato tra i parametri, in questo caso: `{'giorno': '2023-01-01'}, ...`

    - `.annotate(spesa_giornaliera = Sum('totale'))` Aggiunge una colonna a ciascun dizionario nel queryset, e in base alla funzione aggregata specificata tra i parametri raggruppa automaticamente le entry con lo stesso valore specificato (nell'esempio con stesso valore in 'giorno') ed esegue la funzione aggregata.  
    **nota:** Per poter usare .annotate e raggruppare query in base a un attributo bisogna prima usare .values per creare la lista di dizionari.
    Inoltre in questa query arrivati a questo punto abbiamo solo il campo 'giorno' ma riusciamo comunque
    ad andare a calcolare il totale in quanto django mantiene il collegamento con il db e sa come fare 
    operazioni che includano attributi della tabella originale ma che magari non sono inculsi in questo
    punto della trasformazione.  


3. `return ListaProdotti.objects.filter(scontrino__in=scontrini).values('prodotto__nome').annotate(total_ordinato=Sum('quantita')).order_by('-total_ordinato')[:5]`
    - `.filter()` prende la lista di scontrini di un utente e va in ListaProdotti per filtrare tutti i prodotti relativi a quei scontrini (scontrino legato come fk in ListaProdotti).  
    - `.values()` trasforma il qs in lista dizionari con unicamente il campo `nome` dalla relazione `prodotto`, notiamo che accediamo a prodotto IN nome (tramite underscore '_').  
    - `.annotate(total_ordinato=Sum('quantita'))` crea una nuova tabella di nome total_ordinato e aggrega le entry con stesso nome prodotto sommando i valori di quantità per ogni prodotto uguale ottenendo un valore che rappresenta il numero di prodotti ordinati in totale.  
    - `.orderby('-total_ordinato')` si ordinano i dizionari del qs in base a questo valore in ordine decrescente (sepcificato dal meno davanti all'attributo di ordinamento).   
    - `[:5]` si fa slicing e si prendono unicamente i primi 5 elementi 


4. Capire bene la differenza tra `aggregate` e `annotate`:
    - **aggregate**: Calcola valori aggregati su un intero queryset e restituisce un dizionario.
    - **annotate**: Calcola valori aggregati per ciascun elemento del queryset e aggiunge i risultati come nuovi campi.

## Richieste AJAX:

Le richieste AJAX (Asynchronous JavaScript and XML) permettono di inviare e ricevere dati dal server in modo asincrono senza dover ricaricare l'intera pagina web. Questo migliora l'esperienza utente rendendo l'interazione con la pagina più fluida e dinamica.

### Funzionamento: 
1. Inizializzazione della Richiesta:
    - Una richiesta AJAX viene inizializzata tramite JavaScript (spesso utilizzando librerie come jQuery per semplificare il processo).
    - La richiesta può essere di tipo GET o POST, a seconda del tipo di operazione che si vuole eseguire.

2. Invio di dati al server: 
    - I dati vengono inviati al server come parte della richiesta.
    - Nel caso di una richiesta POST, i dati vengono generalmente inviati nel corpo della richiesta.

3. Aggiornamento della pagina web:
    - La risposta del server viene utilizzata per aggiornare dinamicamente la pagina web senza ricaricarla completamente.


### Vantaggi:
- **Esperienza Utente Migliorata:** Permettono di aggiornare parti della pagina senza ricaricarla completamente, rendendo l'interazione più fluida.
- **Efficienza:** Riduce il carico sul server e la quantità di dati trasferiti, poiché solo le parti necessarie della pagina vengono aggiornate.
- **Interattività:** Consente di creare applicazioni web più interattive e reattive.