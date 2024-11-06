document.addEventListener('DOMContentLoaded', function () {
    const prodottiList = [];
    const errorMessage = document.getElementById('error-message');

    // Aggiungi all'inizio del file, dopo la dichiarazione delle costanti
    function toggleSalvaScontrinoButton() {
        const salvaScontrinoButton = document.getElementById('salva_scontrino_button');
        if (prodottiList.length > 0) {
            salvaScontrinoButton.disabled = false;
        } else {
            salvaScontrinoButton.disabled = true;
        }
    }

    // Funzione per formattare il prezzo con due decimali
    function formatPrezzo(prezzo) {
        return Number(Math.round(prezzo + 'e2') + 'e-2').toFixed(2);
    }

    // Funzione per validare l'input
    function validaInput(input) {
        const quantita = parseFloat(input.quantita);
        const prezzo = parseFloat(input.prezzo);
        const nome = input.nome.trim();

        let errori = [];

        // Validazione quantità
        if (!Number.isInteger(quantita)) {
            input.quantita = Math.round(quantita);
            errori.push('La quantità è stata arrotondata all\'intero più vicino');
        }
        if (quantita <= 0) {
            errori.push('La quantità deve essere maggiore di zero');
            return { valido: false, errori, input };
        }

        // Validazione prezzo
        if (prezzo !== parseFloat(formatPrezzo(prezzo))) {
            input.prezzo = formatPrezzo(prezzo);
            errori.push('Il prezzo è stato arrotondato a due decimali');
        }
        if (prezzo <= 0) {
            errori.push('Il prezzo deve essere maggiore di zero');
            return { valido: false, errori, input };
        }

        // Validazione nome
        if (!nome) {
            errori.push('Il nome del prodotto è obbligatorio');
        }

        return {
            valido: errori.length === 0 || (errori.length === 1 && errori[0].includes('arrotonda')),
            errori: errori,
            input: input
        };
    }

    // Funzione per aggiornare la tabella dei prodotti
    function aggiornaTabellaModal() {
        const tbody = document.getElementById('prodotti-modale-list');
        tbody.innerHTML = '';

        prodottiList.forEach((prodotto, index) => {
            const row = `
                <tr>
                    <td class="border-0">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-shopping-cart text-primary mr-3"></i>
                            <span class="font-weight-medium">${prodotto.nome}</span>
                        </div>
                    </td>
                    <td class="border-0 text-center">
                        <div class="btn-group">
                            <button class="btn btn-sm btn-outline-secondary" onclick="modificaQuantita(${index}, -1)">-</button>
                            <span class="btn btn-sm">${prodotto.quantita}</span>
                            <button class="btn btn-sm btn-outline-secondary" onclick="modificaQuantita(${index}, 1)">+</button>
                        </div>
                    </td>
                    <td class="border-0 text-right">${prodotto.prezzo} €</td>
                    <td class="border-0 text-right">
                        <button class="btn btn-sm btn-danger" onclick="rimuoviProdotto(${index})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
            tbody.insertAdjacentHTML('beforeend', row);
        });
    }

    // Funzioni globali per la gestione dei prodotti
    window.modificaQuantita = function (index, delta) {
        const prodotto = prodottiList[index];
        const nuovaQuantita = prodotto.quantita + delta;

        if (nuovaQuantita > 0) {
            prodotto.quantita = nuovaQuantita;
            aggiornaTabellaModal();
            aggiornaTotale();
        }
    };

    window.rimuoviProdotto = function (index) {
        if (confirm('Sei sicuro di voler rimuovere questo prodotto?')) {
            prodottiList.splice(index, 1);
            aggiornaTabellaModal();
            aggiornaTotale();
        }
    };

    window.modificaPrezzo = function (index) {
        const prodotto = prodottiList[index];
        const nuovoPrezzo = prompt('Inserisci il nuovo prezzo:', prodotto.prezzo);

        if (nuovoPrezzo !== null) {
            const prezzo = parseFloat(nuovoPrezzo);
            if (!isNaN(prezzo) && prezzo > 0) {
                prodotto.prezzo = parseFloat(formatPrezzo(prezzo));
                aggiornaTabellaModal();
                aggiornaTotale();
            } else {
                alert('Inserisci un prezzo valido maggiore di 0');
            }
        }
    };

    // Handler per l'aggiunta di un nuovo prodotto
    document.getElementById('aggiungiProdottoForm').addEventListener('submit', function (e) {
        e.preventDefault();

        const input = {
            nome: document.getElementById('nome_prodotto').value,
            quantita: document.getElementById('quantita').value,
            prezzo: document.getElementById('prezzo_unitario').value
        };

        const validazione = validaInput(input);

        if (validazione.errori.length > 0) {
            errorMessage.textContent = validazione.errori.join('. ');
            errorMessage.classList.remove('d-none');

            document.getElementById('quantita').value = validazione.input.quantita;
            document.getElementById('prezzo_unitario').value = validazione.input.prezzo;

            setTimeout(() => {
                errorMessage.classList.add('d-none');
            }, 3000);
            return;
        }

        prodottiList.push({
            nome: validazione.input.nome,
            quantita: parseInt(validazione.input.quantita),
            prezzo: parseFloat(validazione.input.prezzo)
        });

        this.reset();
        aggiornaTabellaModal();
        aggiornaTotale();
        document.getElementById('prodotti_count').value = prodottiList.length;
    });

    // Handler per il salvataggio finale
    document.getElementById('salvaProdottiButton').addEventListener('click', function () {
        const prodottiInput = document.createElement('input');
        prodottiInput.type = 'hidden';
        prodottiInput.name = 'prodotti_json';
        prodottiInput.value = JSON.stringify(prodottiList);
        document.getElementById('scontrino-form').appendChild(prodottiInput);

        document.getElementById('prodotti_count').value = prodottiList.length;
        toggleSalvaScontrinoButton();

        $('#gestioneProdottiModal').modal('hide');
    });

    // Funzione per aggiornare il totale
    function aggiornaTotale() {
        const totale = prodottiList.reduce((acc, prodotto) =>
            acc + (prodotto.quantita * prodotto.prezzo), 0);
        document.getElementById('totale_scontrino').textContent =
            `Totale: ${totale.toFixed(2)} €`;
    }

    // Validazione form principale
    function validaFormPrincipale() {
        const data = document.getElementById('id_data').value;
        const negozio = document.getElementById('id_negozio_nome').value.trim();
        const oggi = new Date().toISOString().split('T')[0];

        let errori = [];

        if (!data) {
            errori.push('La data è obbligatoria');
        } else if (data > oggi) {
            errori.push('La data non può essere futura');
        }

        if (!negozio) {
            errori.push('Il nome del negozio è obbligatorio');
        }

        return {
            valido: errori.length === 0,
            errori: errori
        };
    }

    // Aggiorniamo l'handler del submit del form
    document.getElementById('scontrino-form').addEventListener('submit', function (e) {
        e.preventDefault();

        const validazioneForm = validaFormPrincipale();
        if (!validazioneForm.valido) {
            errorMessage.textContent = validazioneForm.errori.join('. ');
            errorMessage.classList.remove('d-none');
            setTimeout(() => {
                errorMessage.classList.add('d-none');
            }, 3000);
            return;
        }

        if (prodottiList.length === 0) {
            errorMessage.textContent = 'Aggiungi almeno un prodotto allo scontrino';
            errorMessage.classList.remove('d-none');
            setTimeout(() => {
                errorMessage.classList.add('d-none');
            }, 3000);
            return;
        }

        // Aggiungiamo il loading state
        const submitButton = document.getElementById('salva_scontrino_button');
        const originalText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Salvataggio in corso...';

        // Aggiungiamo i dati dei prodotti al form
        const prodottiInput = document.createElement('input');
        prodottiInput.type = 'hidden';
        prodottiInput.name = 'prodotti_json';
        prodottiInput.value = JSON.stringify(prodottiList);
        this.appendChild(prodottiInput);

        // Aggiungiamo il totale
        const totaleInput = document.createElement('input');
        totaleInput.type = 'hidden';
        totaleInput.name = 'totale';
        totaleInput.value = prodottiList.reduce((acc, p) => acc + (p.quantita * p.prezzo), 0).toFixed(2);
        this.appendChild(totaleInput);

        // Gestiamo gli errori del backend
        this.addEventListener('submit', function () {
            setTimeout(() => {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            }, 5000); // timeout di sicurezza
        });

        this.submit();
    });

    document.getElementById('quantita').addEventListener('input', function (e) {
        if (this.value < 1) {
            this.setCustomValidity('La quantità deve essere maggiore di zero');
        } else {
            this.setCustomValidity('');
        }
    });

    document.getElementById('prezzo_unitario').addEventListener('input', function (e) {
        if (this.value <= 0) {
            this.setCustomValidity('Il prezzo deve essere maggiore di zero');
        } else {
            this.setCustomValidity('');
        }
    });
});