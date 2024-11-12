import boto3


'''
Nota: 
Se si vuole modificare e migliorare l'immagine prima di passarla a textextract
conviene usare librerire come CV2 o PILLOW e successivamente convertire 
l'immagine in bytearray 
'''


def analizza_scontrino_con_expense(file_path):
    # creazione del client (.aws/credentials) e della regione
    client = boto3.client('textract', region_name='eu-west-3')

    # immagine in formato byte per consentire interazione con servizi AWS
    with open(file_path, 'rb') as document:
        imageBytes = bytearray(document.read())

    response = client.analyze_expense(Document={'Bytes': imageBytes})

    print(f' Resp type: {type(response)}')
    print("\n -------- \n")
    for expense_doc in response['ExpenseDocuments']:
        for item in expense_doc['LineItemGroups']:
            for line_item in item['LineItems']:
                for field in line_item['LineItemExpenseFields']:
                    if field['Type']['Text'] == 'ITEM':
                        print(f"Prodotto: {field['ValueDetection']['Text']}")
                    elif field['Type']['Text'] == 'PRICE':
                        print(f"Prezzo: {field['ValueDetection']['Text']}")

    # Estrazione di informazioni aggiuntive
    info_generali = estrai_info_generali(response)
    print(
        f"Negozio: {info_generali.get('negozio')}, Data: {info_generali.get('data')}, Via: {info_generali.get('via')}")
    return response


def estrai_info_generali(response):
    info = {}
    for expense_doc in response['ExpenseDocuments']:
        for field in expense_doc['SummaryFields']:
            if field['Type']['Text'] == 'VENDOR_NAME':
                info['negozio'] = field['ValueDetection']['Text']
            elif field['Type']['Text'] == 'RECEIPT_DATE':
                info['data'] = field['ValueDetection']['Text']
            elif field['Type']['Text'] == 'VENDOR_ADDRESS':
                info['via'] = field['ValueDetection']['Text']
    return info


def estrai_dati_interessanti(response):
    dati_interessanti = {}

    for expense_doc in response['ExpenseDocuments']:
        # Estrarre informazioni generali
        for field in expense_doc['SummaryFields']:
            tipo = field['Type']['Text']
            valore = field['ValueDetection']['Text']
            if tipo in ['VENDOR_NAME', 'RECEIPT_DATE', 'TOTAL']:
                dati_interessanti[tipo] = valore

        # Estrarre articoli e prezzi
        articoli = []
        for item in expense_doc['LineItemGroups']:
            for line_item in item['LineItems']:
                articolo = {}
                for field in line_item['LineItemExpenseFields']:
                    tipo = field['Type']['Text']
                    valore = field['ValueDetection']['Text']
                    if tipo in ['ITEM', 'PRICE']:
                        articolo[tipo] = valore
                if articolo:
                    articoli.append(articolo)
        dati_interessanti['Articoli'] = articoli

    return dati_interessanti


response = analizza_scontrino_con_expense('scontrino1.png')

# Esempio di utilizzo
print("\n\n -------------- \n\n")
print("Response dict: \n")
dati = estrai_dati_interessanti(response)
for chiave, valore in dati.items():
    print(f"{chiave}: {valore}")
