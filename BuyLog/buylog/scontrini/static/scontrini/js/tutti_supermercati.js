$(document).ready(function () {
    $('.filtro-btn').click(function () {
        var filtro = $(this).data('filtro');
        $.ajax({
            url: window.location.href,
            data: {
                'filtro': filtro
            },
            success: function (data) {
                $('#supermercati-list').html(data);
            }
        });
    });

    $('#search-bar').on('input', function () {
        var query = $(this).val();
        $.ajax({
            url: window.location.href,
            data: {
                'search': query
            },
            success: function (data) {
                $('#supermercati-list').html(data);
            }
        });
    });
});