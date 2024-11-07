// static/scontrini/js/stats_demo.js

document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM completamente caricato e analizzato");

    // Ottieni i dati JSON direttamente dal tag json_script generato da Django
    var speseData = JSON.parse(document.getElementById('speseData').textContent);

    // Debug: stampa i dati JSON parsati
    console.log("Dati JSON parsati da speseData:", speseData);

    // Verifica che speseData sia un array
    if (!Array.isArray(speseData)) {
        console.error("speseData non è un array:", speseData);
        return;
    }

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
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointRadius: 2,
                pointBackgroundColor: '#2563eb',
                pointBorderWidth: 2,
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day'
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        display: false
                    }
                }
            }
        }
    });

    // Funzione per aggiornare il grafico e le statistiche tramite AJAX
    function aggiornaGrafico(filtro) {
        console.log("Chiamata AJAX per aggiornare il grafico con filtro:", filtro);
        $.ajax({
            url: '/scontrini/aggiorna_grafico_demo/',
            data: {
                'filtro': filtro
            },
            success: function (data) {
                console.log("Dati ricevuti dall'endpoint aggiorna_grafico_demo:", data);

                // Aggiorna il grafico
                speseGrafico.data.labels = data.labels;
                speseGrafico.data.datasets[0].data = data.data;
                speseGrafico.update();

                // Aggiorna le statistiche usando gli ID corretti
                document.getElementById('filtro-attuale').textContent = data.filtro_attuale;
                document.getElementById('numero-scontrini').textContent = data.numero_scontrini;
                document.getElementById('totale-speso').textContent = `${parseFloat(data.totale_speso).toFixed(2)} €`;
                document.getElementById('numero-articoli').textContent = data.numero_articoli;

                // Aggiorna i top prodotti
                var topProdottiTable = document.getElementById('top-prodotti');
                topProdottiTable.innerHTML = '';
                data.top_prodotti.forEach(function (prodotto) {
                    var row = `<tr><td>${prodotto.prodotto__nome}</td><td>${prodotto.total_ordinato}</td></tr>`;
                    topProdottiTable.innerHTML += row;
                });

                // Aggiorna i top supermercati
                var topSupermercatiTable = document.getElementById('top-supermercati');
                topSupermercatiTable.innerHTML = '';
                data.top_supermercati.forEach(function (supermercato) {
                    var row = `<tr><td>${supermercato.negozio__nome}</td><td>${supermercato.frequenza}</td></tr>`;
                    topSupermercatiTable.innerHTML += row;
                });
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
            console.log("Pulsante cliccato, filtro selezionato:", filtro); // Log di debug
            aggiornaGrafico(filtro);
        });
    });

    // Esempio di chiamata AJAX per aggiornare il grafico
    // ? aggiornaGrafico('all_time');
});