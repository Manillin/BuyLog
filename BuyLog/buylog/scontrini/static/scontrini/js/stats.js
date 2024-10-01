document.addEventListener('DOMContentLoaded', function () {

    console.log("DOM completamente caricato e analizzato"); // Log di debug

    // Ottieni i dati JSON direttamente dal tag json_script generato da Django
    var speseData = JSON.parse(document.getElementById('speseData').textContent);

    // Debug: stampa i dati JSON parsati
    console.log("Dati JSON parsati da speseData:", speseData);

    // Estrai le etichette (giorno) e i dati (spesa_giornaliera)
    var labels = speseData.map(item => item.giorno);
    var data = speseData.map(item => item.spesa_giornaliera);

    // Debug: stampa le etichette e i dati estratti
    console.log("Etichette (labels) per il grafico:", labels);
    console.log("Dati (spese giornaliere) per il grafico:", data);

    var ctx = document.getElementById('speseGrafico').getContext('2d');
    var speseGrafico = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Spese',
                data: data,
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day'
                    }
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Funzione per aggiornare il grafico tramite AJAX
    function aggiornaGrafico(filtro) {
        console.log("Chiamata AJAX per aggiornare il grafico con filtro:", filtro); // Log di debug
        $.ajax({
            url: '/scontrini/aggiorna_grafico/',
            data: {
                'filtro': filtro
            },
            success: function (data) {
                // Debug: stampa i dati ricevuti
                console.log("Dati ricevuti dall'endpoint aggiorna_grafico:", data);

                speseGrafico.data.labels = data.labels;
                speseGrafico.data.datasets[0].data = data.data;
                speseGrafico.update();
            },
            error: function (error) {
                console.error("Errore durante l'aggiornamento del grafico:", error);
            }
        });
    }

    // Gestore di eventi per i pulsanti di filtro
    document.querySelectorAll('.filtro-btn').forEach(button => {
        button.addEventListener('click', function () {
            var filtro = this.getAttribute('data-filtro');
            console.log("pulsante cliccato con filtro:", filtro); // Log di debug
            aggiornaGrafico(filtro);
        });
    });

    // Esempio di chiamata AJAX per aggiornare il grafico
    aggiornaGrafico('all_time');
});