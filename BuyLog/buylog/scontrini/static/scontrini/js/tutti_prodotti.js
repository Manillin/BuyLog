$(document).ready(function () {
    function updateURL(params) {
        const url = new URL(window.location);
        Object.keys(params).forEach(key => {
            url.searchParams.set(key, params[key]);
        });
        window.history.pushState({}, '', url);
    }

    $('.filtro-btn').click(function () {
        var filtro = $(this).data('filtro');
        var ordine = $('.sort-link.active').data('ordine') || '-quantita_ordinata';
        $('.filtro-btn').removeClass('active');
        $(this).addClass('active');

        $.ajax({
            type: 'GET',
            url: '/scontrini/aggiorna_tabella_prodotti/',
            data: {
                'filtro': filtro,
                'ordine': ordine,
                'page': 1 // Resetta alla prima pagina quando si applica un filtro
            },
            success: function (data) {
                $('#prodotti-list').html(data.html);
                $('.pagination-container').html(data.pagination);
                updateURL({ 'filtro': filtro, 'ordine': ordine, 'page': 1 });
            }
        });
    });

    $('#search-bar').on('input', function () {
        var query = $(this).val();
        var filtro = $('.filtro-btn.active').data('filtro') || 'all_time';
        var ordine = $('.sort-link.active').data('ordine') || '-quantita_ordinata';

        $.ajax({
            type: 'GET',
            url: '/scontrini/aggiorna_tabella_prodotti/',
            data: {
                'search': query,
                'filtro': filtro,
                'ordine': ordine,
                'page': 1
            },
            success: function (data) {
                $('#prodotti-list').html(data.html);
                $('.pagination-container').html(data.pagination);
                updateURL({ 'search': query, 'filtro': filtro, 'ordine': ordine, 'page': 1 });
            }
        });
    });

    $('.sort-link').click(function (e) {
        e.preventDefault();
        var ordine = $(this).data('ordine');
        var filtro = $('.filtro-btn.active').data('filtro') || 'all_time';
        $('.sort-link').removeClass('active');
        $(this).addClass('active');

        $.ajax({
            type: 'GET',
            url: '/scontrini/aggiorna_tabella_prodotti/',
            data: {
                'filtro': filtro,
                'ordine': ordine,
                'page': 1
            },
            success: function (data) {
                $('#prodotti-list').html(data.html);
                $('.pagination-container').html(data.pagination);
                updateURL({ 'filtro': filtro, 'ordine': ordine, 'page': 1 });
            }
        });
    });
});