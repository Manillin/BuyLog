/**
 * Script JS per la pagina di carica_scontrino.html
 */

document.addEventListener('DOMContentLoaded', function () {
    // Selezione dell'elemento nasconto che tiene traccia del numero di prodotti
    const prodottiCountElement = document.getElementById('prodotti_count');
    const salvaScontrinoButton = document.getElementById('salva_scontrino_button');
    const errorMessage = document.getElementById('error-message');

    // Funzione per abilitare/disabilitare il pulsante di salvataggio dello scontrino
    function toggleSalvaScontrinoButton() {
        const prodottiCount = parseInt(prodottiCountElement.value);
        if (prodottiCount > 0) {
            salvaScontrinoButton.disabled = false;
        } else {
            salvaScontrinoButton.disabled = true;
        }
    }

    toggleSalvaScontrinoButton();

    // Aggiunge un event listener al pulsante "Aggiungi" nel modale - responsabile dell'invio AJAX
    document.getElementById('addProductButton').addEventListener('click', function () {
        // Recupero i dati dal form
        const quantitaInput = document.getElementById('quantita');
        const quantita = parseFloat(quantitaInput.value);
        const prezzoUnitario = document.getElementById('prezzo_unitario').value;
        const nomeProdotto = document.getElementById('nome_prodotto').value;

        // Controllo di integrità per la quantità
        if (!Number.isInteger(quantita)) {
            errorMessage.classList.remove('d-none');
            quantitaInput.value = Math.round(quantita);
            setTimeout(() => {
                errorMessage.classList.add('d-none');
            }, 3000);
        } else {
            errorMessage.classList.add('d-none');
            // Se dati consistenti mando AJAX con CSFR token
            if (quantita && prezzoUnitario && nomeProdotto) {
                $.ajax({
                    type: 'POST',
                    url: aggiungi_prodotto_url,
                    data: {
                        'quantita': quantita,
                        'prezzo_unitario': prezzoUnitario,
                        'nome_prodotto': nomeProdotto,
                        'csrfmiddlewaretoken': csrf_token
                    },
                    /**
                     * La richiesta AJAX invoca la funzione aggiungi_prodotto() nel file views.py \
                     * tale view aggiunge un prodotto alla sessione e ritorna i parametri 'success' e 'prodotti_count'
                     */
                    success: function (response) {
                        if (response.success) {
                            prodottiCountElement.value = response.prodotti_count;
                            toggleSalvaScontrinoButton();

                            const prodottiList = document.getElementById('prodotti-list');
                            const noProdotti = document.getElementById('no-prodotti');
                            //rimuove il messaggio 'Nessun prodotto aggiunto' in quanto si sta aggiungendo un prodotto
                            if (noProdotti) {
                                noProdotti.remove();
                            }
                            // Crea un nuovo elemento <li> (dentro la lista) per il prodotto aggiunto
                            const newProduct = document.createElement('li');
                            newProduct.classList.add('list-group-item');
                            newProduct.textContent = `${nomeProdotto} - ${quantita} x ${prezzoUnitario} €`;
                            prodottiList.appendChild(newProduct);

                            // Resetta il form e nasconde il modale
                            document.getElementById('aggiungiProdottoForm').reset();
                            $('#aggiungiProdottoModal').modal('hide');
                        }
                    }
                });
            }
        }
    });
});