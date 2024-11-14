// Variabili globali
const ITEMS_PER_PAGE = 10;
let currentPage = 1;
let prodottiFoto = [];
let errorMessage;

// Funzione per ottenere il CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function () {
    // Inizializza errorMessage
    errorMessage = document.getElementById('error-message');

    // Toggle tra i form
    const btnManuale = document.getElementById('btn-manuale');
    const btnFoto = document.getElementById('btn-foto');
    const formManuale = document.getElementById('form-manuale');
    const formFoto = document.getElementById('form-foto');

    btnManuale.addEventListener('click', function () {
        formManuale.style.display = 'block';
        formFoto.style.display = 'none';
        btnManuale.classList.add('active');
        btnFoto.classList.remove('active');
    });

    btnFoto.addEventListener('click', function () {
        formManuale.style.display = 'none';
        formFoto.style.display = 'block';
        btnFoto.classList.add('active');
        btnManuale.classList.remove('active');
    });

    // Gestione upload foto
    const fotoForm = document.getElementById('foto-form');
    fotoForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(this);
        const submitButton = this.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;

        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Analisi in corso...';

        fetch('/scontrini/analizza-scontrino/', {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        })
            .then(response => {
                console.log('Response status:', response.status);
                console.log('Response headers:', response.headers);
                return response.json();
            })
            .then(data => {
                console.log('Dati ricevuti:', data);
                if (data.success && data.prodotti && data.prodotti.length > 0) {
                    console.log('Prodotti trovati:', data.prodotti.length);
                    initPagination(data.prodotti, data.categorie);
                    $('#gestioneProdottiFotoModal').modal('show');
                } else {
                    console.error('Errore nei dati:', data);
                    errorMessage.textContent = data.error || 'Errore durante l\'analisi dello scontrino';
                    errorMessage.classList.remove('d-none');
                    setTimeout(() => errorMessage.classList.add('d-none'), 3000);
                }
            })
            .catch(error => {
                console.error('Errore completo:', error);
                errorMessage.textContent = 'Errore di rete durante l\'upload';
                errorMessage.classList.remove('d-none');
            })
            .finally(() => {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            });
    });

    // Gestione salvataggio
    document.getElementById('salvaProdottiFotoButton').addEventListener('click', function () {
        const data = document.getElementById('id_data_foto').value;
        const negozio = document.getElementById('id_negozio_nome_foto').value;
        const scontrinoData = {
            data: data,
            negozio: negozio,
            prodotti: prodottiFoto
        };

        console.log('Dati inviati al server:', scontrinoData);

        fetch('/scontrini/salva-scontrino-foto/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(scontrinoData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/scontrini/successo/';
                } else {
                    errorMessage.textContent = data.error || 'Errore durante il salvataggio';
                    errorMessage.classList.remove('d-none');
                }
            });
    });
});

// Funzioni di gestione tabella e paginazione
function initPagination(products, categories) {
    prodottiFoto = products.map(p => {
        const prezzoStr = p.prezzo.toString().replace(',', '.');
        const prezzoNum = parseFloat(prezzoStr);
        const categoriaObj = categories.find(c => c.nome === p.categoria) ||
            categories.find(c => c.nome === 'altro');
        return {
            nome: p.nome,
            prezzo: prezzoNum,
            quantita: p.quantita || 1,
            categoria: categoriaObj ? categoriaObj.id : null
        };
    });
    data = { categorie: categories || [] };
    currentPage = 1;
    aggiornaTabellaFoto();
    aggiornaTotaleFoto();
}

function aggiornaTabellaFoto() {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;
    const pageProducts = prodottiFoto.slice(start, end);

    const tbody = document.getElementById('prodotti-foto-list');
    tbody.innerHTML = '';

    pageProducts.forEach((prodotto, index) => {
        const globalIndex = start + index;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${prodotto.nome}</td>
            <td class="text-center">
                <div class="btn-group">
                    <button class="btn btn-sm btn-outline-secondary" onclick="modificaQuantitaFoto(${globalIndex}, -1)">-</button>
                    <span class="btn btn-sm">${prodotto.quantita || 1}</span>
                    <button class="btn btn-sm btn-outline-secondary" onclick="modificaQuantitaFoto(${globalIndex}, 1)">+</button>
                </div>
            </td>
            <td class="text-right">${prodotto.prezzo} €</td>
            <td>
                <div class="d-flex align-items-center">
                    <select class="form-control categoria-select" onchange="modificaCategoriaFoto(${globalIndex}, this.value)">
                        ${data.categorie.map(cat => `
                            <option value="${cat.id}" ${prodotto.categoria === cat.id ? 'selected' : ''}>
                                ${cat.nome}
                            </option>
                        `).join('')}
                    </select>
                    ${prodotto.categoria_confermata ?
                '<span class="badge badge-success ml-2"><i class="fas fa-check"></i></span>' : ''}
                </div>
            </td>
            <td class="text-right">
                <button class="btn btn-sm btn-danger" onclick="rimuoviProdottoFoto(${globalIndex})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });

    updatePaginationControls();
    aggiornaTotaleFoto();
}

function updatePaginationControls() {
    const totalPages = Math.ceil(prodottiFoto.length / ITEMS_PER_PAGE);
    const paginationEl = document.getElementById('paginazione-prodotti');
    paginationEl.innerHTML = '';

    for (let i = 1; i <= totalPages; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === currentPage ? 'active' : ''}`;
        li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
        li.querySelector('a').addEventListener('click', (e) => {
            e.preventDefault();
            currentPage = i;
            aggiornaTabellaFoto();
        });
        paginationEl.appendChild(li);
    }
}

// Funzioni di gestione prodotti
function modificaQuantitaFoto(index, delta) {
    const prodotto = prodottiFoto[index];
    console.log(`Modifica quantità per ${prodotto.nome}: ${prodotto.quantita || 1} ${delta > 0 ? '+' : '-'} 1`);
    prodottiFoto[index].quantita = (prodotto.quantita || 1) + delta;
    if (prodottiFoto[index].quantita < 1) prodottiFoto[index].quantita = 1;
    aggiornaTabellaFoto();
    aggiornaTotaleFoto();
}
function modificaCategoriaFoto(index, categoriaId) {
    prodottiFoto[index].categoria = categoriaId;
    prodottiFoto[index].categoria_confermata = true;
    aggiornaTabellaFoto();
}

function rimuoviProdottoFoto(index) {
    if (confirm('Sei sicuro di voler rimuovere questo prodotto?')) {
        prodottiFoto.splice(index, 1);
        aggiornaTabellaFoto();
        aggiornaTotaleFoto();
    }
}

function aggiornaTotaleFoto() {
    console.log('Calcolo totale per prodotti:', prodottiFoto);
    const totale = prodottiFoto.reduce((acc, prodotto) => {
        const prezzo = prodotto.prezzo;
        const quantita = prodotto.quantita || 1;
        const subtotale = quantita * prezzo;
        console.log(`${prodotto.nome}: ${quantita} x ${prezzo}€ = ${subtotale}€`);
        return acc + subtotale;
    }, 0);
    console.log('Totale calcolato:', totale);
    document.getElementById('totale_scontrino_foto').textContent = `${totale.toFixed(2)} €`;
}

