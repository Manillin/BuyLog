# BuyLog


## WIP Features: 

### 1. Generalizzazione prodotti specifici in categorie

Quando si carica un nuovo prodotto da uno scontrino esso potrebbe avere un nome generico difficilmente
associabile a una categoria generica (es: PANE BAUL GRANO DURO - categoria: pane).

**feature:**
- Aggiormaneto dei modelli per estenedere il generico prodotto ad appartenere a una categoria specifica  
- Modello Categoria che rappresenta un generico prodotto (pane, mela, latte, ecc....)  
- Funzione di matching per cercare di riconoscere una categoria da un prodotto mai incontrato  
- Possibilità di inserimento manuale di categoria per un prodotto a cui non è stata associata nessuna categoria
- Creazione di modello ProdottoRiconosciuto per fare in modo che quando si incontra un prodotto a cui è già stata associata una categoria generica questa avvenga automaticamente -> gli utenti nuovi traggoni beneficio dalle associazioni fatte da utenti precedenti -> Apprendimento incrementale e maggiore robustezza nel tempo.  



## 2. Noramlizzazione categorie per plurale e case insensitive
