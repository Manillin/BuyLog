/**
 * Script JS per la pagina di carica_scontrino.html
 */

document.addEventListener('DOMContentLoaded', function () {
    const prodottiCountElement = document.getElementById('prodotti_count');
    const salvaScontrinoButton = document.getElementById('salva_scontrino_button');

    function toggleSalvaScontrinoButton() {
        const prodottiCount = parseInt(prodottiCountElement.value);
        if (prodottiCount > 0) {
            salvaScontrinoButton.disabled = false;
        } else {
            salvaScontrinoButton.disabled = true;
        }
    }

    toggleSalvaScontrinoButton();

    document.getElementById('addProductButton').addEventListener('click', function () {
        const quantita = document.getElementById('quantita').value;
        const prezzoUnitario = document.getElementById('prezzo_unitario').value;
        const nomeProdotto = document.getElementById('nome_prodotto').value;

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
                success: function (response) {
                    if (response.success) {
                        prodottiCountElement.value = response.prodotti_count;
                        toggleSalvaScontrinoButton();

                        const prodottiList = document.getElementById('prodotti-list');
                        const noProdotti = document.getElementById('no-prodotti');
                        if (noProdotti) {
                            noProdotti.remove();
                        }
                        const newProduct = document.createElement('li');
                        newProduct.textContent = `${nomeProdotto} - ${quantita} x ${prezzoUnitario} €`;
                        prodottiList.appendChild(newProduct);

                        document.getElementById('aggiungiProdottoForm').reset();
                        $('#aggiungiProdottoModal').modal('hide');
                    }
                }
            });
        }
    });
});