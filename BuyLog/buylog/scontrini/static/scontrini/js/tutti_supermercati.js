$(document).ready(function () {
    $('.filtro-btn').click(function () {
        var filtro = $(this).data('filtro');
        var ordine = $('.sort-link.active').data('ordine') || '-numero_visite';
        $.ajax({
            type: 'GET',
            url: '/scontrini/aggiorna_tabella_supermercati/',
            data: {
                'filtro': filtro,
                'ordine': ordine
            },
            success: function (data) {
                $('#supermercati-list').html(data.html);
            }
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
            }
        });
    });
});