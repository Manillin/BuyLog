document.addEventListener('DOMContentLoaded', function () {
    const prodottiModal = document.getElementById('prodottiModal');
    const categoriaId = document.querySelector('[data-categoria-id]').dataset.categoriaId;

    function caricaProdotti(page = 1) {
        fetch(`/scontrini/categoria/${categoriaId}/prodotti/?page=${page}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('prodottiTable').innerHTML = data.html;
            });
    }

    // Carica i prodotti quando il modale viene aperto
    prodottiModal.addEventListener('show.bs.modal', function () {
        caricaProdotti(1);
    });

    // Gestione della paginazione
    document.getElementById('prodottiTable').addEventListener('click', function (e) {
        if (e.target.classList.contains('page-link')) {
            e.preventDefault();
            const page = e.target.dataset.page;
            if (page) {
                caricaProdotti(page);
            }
        }
    });
});