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
    const toggleButton = document.getElementById('toggleVisualizzazione');
    const categoriaInputs = document.querySelectorAll('.categoria-input');

    toggleButton.addEventListener('click', function () {
        const scontrinoId = this.dataset.scontrinoId;
        fetch(`/scontrini/toggle-visualizzazione/${scontrinoId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
    });

    categoriaInputs.forEach(input => {
        let timeoutId;

        input.addEventListener('change', function () {
            const prodottoId = this.dataset.prodottoId;
            const categoriaNome = this.value.trim().toLowerCase();

            if (categoriaNome) {
                // Prima cerca o crea la categoria
                fetch('/scontrini/crea-categoria/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        nome: categoriaNome
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            return fetch('/scontrini/aggiorna-categoria-prodotto/', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': getCookie('csrftoken')
                                },
                                body: JSON.stringify({
                                    prodotto_id: prodottoId,
                                    categoria_id: data.categoria_id
                                })
                            });
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Aggiorna solo l'icona di conferma invece di ricaricare la pagina
                            const inputGroup = input.closest('.input-group');
                            if (!inputGroup.querySelector('.bg-success')) {
                                inputGroup.querySelector('.input-group-append').insertAdjacentHTML(
                                    'beforeend',
                                    '<span class="input-group-text bg-success text-white"><i class="fas fa-check"></i></span>'
                                );
                            }
                        }
                    });
            }
        });
    });
});

function confermaCategoriaClick(button) {
    const input = button.closest('.input-group').querySelector('.categoria-input');
    const rawProdottoId = input.dataset.prodottoId;
    console.log('Raw ID:', rawProdottoId);
    const prodottoId = parseInt(rawProdottoId);
    console.log('Parsed ID:', prodottoId);

    if (isNaN(prodottoId)) {
        console.error('ID prodotto non valido');
        return;
    }

    const categoriaNome = input.value.trim().toLowerCase();

    if (categoriaNome) {
        fetch('/scontrini/crea-categoria/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                nome: categoriaNome
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Categoria creata/trovata:', data);
                    return fetch('/scontrini/aggiorna-categoria-prodotto/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            prodotto_id: prodottoId,
                            categoria_id: data.categoria_id
                        })
                    });
                }
                throw new Error('Errore nella creazione della categoria');
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    console.error('Errore aggiornamento categoria:', data.error);
                }
            })
            .catch(error => {
                console.error('Errore:', error);
            });
    }
}