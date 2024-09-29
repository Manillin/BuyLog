# BuyLog

currently WIP

## Main Features:
- Load user pictures of receipts
- Different potential output based on user type 
- Visualize the stats with a default filer, and add possiiblity to change said filter
- User page with details and possibility to export data in different formats.  


# Steps: 

1. Creazione webpage landing 
2. Creazione e suddivisione del progetto in APP e creazione dei modelli 
3. Migrazione + superutente
4. Creazione utenti 



# Currently Working on: 

1. Caricamento scontrino da parte dell'utente [check]
    - definire un ModelForm basato su modello Scontrino 
    - fare una CBV - CreateView 
    - definire un template che includa il django form 
    - verificare funzionamento con test 


2. Visualizzazione degli scontrini / statistiche in stile dashboard
    - pagina dedicata per vedere scontrini 
        - visualizzazione di un grafico [x: giorni, y: soldi]
        - on entry: numero di scontrini messi
        - totale di soldi spesi 
        - numero di articoli ordinati 
        - lista di scontrini da visualizzare (espandere)
        - top selling products / most freq supermarcet 
    - possibilità di usare filtri 