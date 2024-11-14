import re
import boto3
from .models import *


def categorizza_prodotto(nome_prodotto):
    # Prima controlla se il prodotto è già conosciuto
    prodotto_esistente = Prodotto.objects.filter(
        nome__iexact=nome_prodotto).first()
    if prodotto_esistente:
        if prodotto_esistente.categoria_confermata:
            print(
                f"Prodotto '{nome_prodotto}' trovato - categoria confermata: {prodotto_esistente.categoria.nome}")
            return prodotto_esistente.categoria, True
        print(
            f"Prodotto '{nome_prodotto}' trovato - categoria non confermata, provo regex")

    # Se non esiste, prova con le regex
    patterns = {
        'pane': r'\b(pane|baguette|filone)\b',
        'latte': r'\b(latte|yogurt)\b',
        # aggiungi altri pattern...
    }

    nome_lower = nome_prodotto.lower()
    for categoria_nome, pattern in patterns.items():
        if re.search(pattern, nome_lower):
            categoria, _ = Categoria.objects.get_or_create(nome=categoria_nome)
            print(
                f"Categorizzazione con regex riuscita per '{nome_prodotto}': {categoria_nome}")
            return categoria, True  # Se fa match, la categoria è confermata

    # Se non trova match, restituisce la categoria 'altro'
    print(
        f"Categorizzazione con regex fallita per '{nome_prodotto}', assegno 'altro'")
    categoria, _ = Categoria.objects.get_or_create(nome='altro')
    return categoria, False


def estrai_dati_scontrino(file_path):
    client = boto3.client('textract', region_name='eu-west-3')

    with open(file_path, 'rb') as document:
        imageBytes = bytearray(document.read())

    response = client.analyze_expense(Document={'Bytes': imageBytes})

    dati = {
        'prodotti': [],
        'prezzi': [],
        'totale': None,
    }

    # Estrarre informazioni generali
    for expense_doc in response['ExpenseDocuments']:
        for field in expense_doc['SummaryFields']:
            tipo = field['Type']['Text']
            valore = field['ValueDetection']['Text']
            if tipo == 'TOTAL':
                dati['totale'] = valore

        # Estrarre articoli e prezzi
        for item in expense_doc['LineItemGroups']:
            for line_item in item['LineItems']:
                for field in line_item['LineItemExpenseFields']:
                    tipo = field['Type']['Text']
                    valore = field['ValueDetection']['Text']
                    if tipo == 'ITEM':
                        dati['prodotti'].append(valore)
                    elif tipo == 'PRICE':
                        dati['prezzi'].append(valore)

    # Validazione prezzi
    dati['prezzi'] = [float(prezzo.replace(',', '.'))
                      for prezzo in dati['prezzi']]
    if dati['totale']:
        dati['totale'] = float(dati['totale'].replace(',', '.'))

    return dati


def stampa_dati_scontrino(dati_scontrino):
    # Stampa i prodotti e i loro prezzi
    for prodotto, prezzo in zip(dati_scontrino['prodotti'], dati_scontrino['prezzi']):
        print(f"{prodotto} - {prezzo}")

    # Stampa le altre informazioni
    print(f"DATA: {dati_scontrino['data']}")
    print(f"NEGOZIO: {dati_scontrino['negozio']}")
    print(f"TOTALE: {dati_scontrino['totale']}")
    print(f"VIA: {dati_scontrino['via']}")
    print(
        f"PAGAMENTO: {'Elettronico' if dati_scontrino['pagamento'] else 'Contanti'}")


# Esempio di utilizzo
# dati_scontrino = estrai_dati_scontrino('scontrino1.png')

# stampa_dati_scontrino(dati_scontrino)
