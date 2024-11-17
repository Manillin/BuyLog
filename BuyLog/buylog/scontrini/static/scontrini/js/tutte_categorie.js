$(document).ready(function () {
    // Gestione click sui filtri temporali
    $('.filtro-btn').click(function () {
        $('.filtro-btn').removeClass('active');
        $(this).addClass('active');
        var filtro = $(this).data('filtro');
        var ordine = $('.ordine-link.active').data('ordine') || '-quantita_totale';
        aggiornaTabellaCategorie(filtro, ordine, 1);
    });

    // Gestione click sull'ordinamento
    $(document).on('click', '.ordine-link', function (e) {
        e.preventDefault();
        $('.ordine-link').removeClass('active');
        $(this).addClass('active');
        var ordine = $(this).data('ordine');
        var filtro = $('.filtro-btn.active').data('filtro') || 'all_time';
        aggiornaTabellaCategorie(filtro, ordine, 1);
    });

    // Gestione click sulla paginazione
    $(document).on('click', '.page-link', function (e) {
        e.preventDefault();
        var href = $(this).attr('href');
        if (href) {
            var params = new URLSearchParams(href.split('?')[1]);
            var page = params.get('page');
            var filtro = params.get('filtro') || 'all_time';
            var ordine = params.get('ordine') || '-quantita_totale';
            aggiornaTabellaCategorie(filtro, ordine, page);
        }
    });

    // Funzione per aggiornare la tabella
    function aggiornaTabellaCategorie(filtro, ordine, page) {
        $.ajax({
            url: '/scontrini/aggiorna_tabella_categorie/',
            data: {
                'filtro': filtro,
                'ordine': ordine,
                'page': page
            },
            success: function (data) {
                // Aggiorna la tabella
                $('.table-responsive').html(data.html);
                $('.pagination-container').html(data.pagination);

                // Aggiorna l'URL
                var newUrl = `?page=${page}&filtro=${filtro}&ordine=${ordine}`;
                history.pushState({}, '', newUrl);
            },
            error: function (error) {
                console.error("Errore durante l'aggiornamento della tabella:", error);
            }
        });
    }
});