document.addEventListener('DOMContentLoaded', function () {
    console.log('Script stars.js caricato');

    const ratingContainers = document.querySelectorAll('.stars');
    console.log('Rating containers trovati:', ratingContainers.length);

    // Funzione per impostare il valore iniziale delle stelle
    function setInitialStars(container, value) {
        const stars = container.querySelectorAll('i');
        const inputField = document.getElementById(container.dataset.rating);

        stars.forEach((star, index) => {
            if (index < value) {
                star.classList.remove('far');
                star.classList.add('fas', 'text-warning');
            } else {
                star.classList.remove('fas', 'text-warning');
                star.classList.add('far');
            }
        });

        if (inputField) {
            inputField.value = value;
        }
    }

    ratingContainers.forEach(container => {
        const stars = container.querySelectorAll('i');
        const inputField = document.getElementById(container.dataset.rating);
        let selectedValue = 0;

        // Controlla se ci sono valori iniziali da pre-popolare
        const initialValue = container.dataset.initialValue;
        if (initialValue) {
            setInitialStars(container, parseInt(initialValue));
            selectedValue = parseInt(initialValue);
        }

        // Il resto del codice esistente per gli eventi click e mouseover
        stars.forEach(star => {
            star.addEventListener('click', function () {
                const value = parseInt(this.dataset.value);
                selectedValue = value;
                inputField.value = value;
                console.log(`Stella cliccata: ${value} per ${container.dataset.rating}`);
                setInitialStars(container, value);
            });

            star.addEventListener('mouseover', function () {
                const value = parseInt(this.dataset.value);
                stars.forEach(s => {
                    const starValue = parseInt(s.dataset.value);
                    if (starValue <= value) {
                        s.classList.remove('far');
                        s.classList.add('fas', 'text-warning');
                    } else {
                        s.classList.remove('fas', 'text-warning');
                        s.classList.add('far');
                    }
                });
            });

            star.addEventListener('mouseout', function () {
                stars.forEach(s => {
                    const starValue = parseInt(s.dataset.value);
                    if (starValue <= selectedValue) {
                        s.classList.remove('far');
                        s.classList.add('fas', 'text-warning');
                    } else {
                        s.classList.remove('fas', 'text-warning');
                        s.classList.add('far');
                    }
                });
            });
        });
    });
});