import boto3


def estrai_dati_scontrino(file_path):
    client = boto3.client('textract', region_name='eu-west-3')

    with open(file_path, 'rb') as document:
        imageBytes = bytearray(document.read())

    response = client.analyze_expense(Document={'Bytes': imageBytes})

    dati = {
        'prodotti': [],
        'prezzi': [],
        'data': None,
        'negozio': None,
        'totale': None,
        'via': None,
        'pagamento': None
    }

    # Estrarre informazioni generali
    for expense_doc in response['ExpenseDocuments']:
        for field in expense_doc['SummaryFields']:
            tipo = field['Type']['Text']
            valore = field['ValueDetection']['Text']
            if tipo == 'VENDOR_NAME':
                dati['negozio'] = valore
            elif tipo == 'RECEIPT_DATE':
                dati['data'] = valore
            elif tipo == 'TOTAL':
                dati['totale'] = valore
            elif tipo == 'VENDOR_ADDRESS':
                dati['via'] = valore
            elif tipo == 'PAYMENT_METHOD':
                dati['pagamento'] = 'elettronico' if 'card' in valore.lower(
                ) else 'contanti'

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
dati_scontrino = estrai_dati_scontrino('scontrino1.png')

stampa_dati_scontrino(dati_scontrino)
