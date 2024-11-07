$(document).ready(function () {
    function updateURL(params) {
        const url = new URL(window.location);
        Object.keys(params).forEach(key => {
            url.searchParams.set(key, params[key]);
        });
        window.history.pushState({}, '', url);
    }

    function aggiornaTabella(params) {
        $.ajax({
            type: 'GET',
            url: '/scontrini/aggiorna_tabella_supermercati/',
            data: params,
            success: function (data) {
                $('#supermercati-list').html(data.html);
                $('.pagination-container').html(data.pagination);
                updateURL(params);
            }
        });
    }

    $('.filtro-btn').click(function () {
        var filtro = $(this).data('filtro');
        var ordine = $('.sort-link.active').data('ordine') || '-numero_visite';
        $('.filtro-btn').removeClass('active');
        $(this).addClass('active');
        aggiornaTabella({
            'filtro': filtro,
            'ordine': ordine,
            'page': 1
        });
    });

    $(document).on('click', '.pagination .page-link', function (e) {
        e.preventDefault();
        var page = $(this).attr('href').split('page=')[1].split('&')[0];
        var filtro = $('.filtro-btn.active').data('filtro') || 'all_time';
        var ordine = $('.sort-link.active').data('ordine') || '-numero_visite';

        aggiornaTabella({
            'page': page,
            'filtro': filtro,
            'ordine': ordine
        });
    });

    $('#search-bar').on('input', function () {
        var query = $(this).val();
        var filtro = $('.filtro-btn.active').data('filtro') || 'all_time';
        var ordine = $('.sort-link.active').data('ordine') || '-numero_visite';
        $.ajax({
            type: 'GET',
            url: '/scontrini/aggiorna_tabella_supermercati/',
            data: {
                'search': query,
                'filtro': filtro,
                'ordine': ordine
            },
            success: function (data) {
                $('#supermercati-list').html(data.html);
                $('.pagination-container').html(data.pagination);
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
            url: '/scontrini/aggiorna_tabella_supermercati/',
            data: {
                'filtro': filtro,
                'ordine': ordine
            },
            success: function (data) {
                $('#supermercati-list').html(data.html);
                $('.pagination-container').html(data.pagination);
            }
        });
    });
});