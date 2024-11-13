document.addEventListener('DOMContentLoaded', function () {
    const btnManuale = document.getElementById('btn-manuale');
    const btnFoto = document.getElementById('btn-foto');
    const formManuale = document.getElementById('form-manuale');
    const formFoto = document.getElementById('form-foto');
    const errorMessage = document.getElementById('error-message');

    // Toggle tra i form
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

        // Disabilita il bottone e mostra loading
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Analisi in corso...';

        fetch('/scontrini/analizza-scontrino/', {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Popola i prodotti nella sessione
                    if (data.prodotti && data.prodotti.length > 0) {
                        // TODO: Popolare la tabella prodotti
                        $('#gestioneProdottiModal').modal('show');
                    }
                } else {
                    errorMessage.textContent = data.error || 'Errore durante l\'analisi dello scontrino';
                    errorMessage.classList.remove('d-none');
                    setTimeout(() => {
                        errorMessage.classList.add('d-none');
                    }, 3000);
                }
            })
            .catch(error => {
                errorMessage.textContent = 'Errore di rete durante l\'upload';
                errorMessage.classList.remove('d-none');
            })
            .finally(() => {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            });
    });
});
