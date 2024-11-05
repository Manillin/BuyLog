document.addEventListener('DOMContentLoaded', function () {
    // Gestione dei like
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', function (e) {
            e.stopPropagation(); // Previene l'apertura del modal
            const reviewId = this.dataset.reviewId;

            fetch(`/recensioni/like/${reviewId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            })
                .then(response => response.json())
                .then(data => {
                    const icon = this.querySelector('i');
                    const count = this.querySelector('.like-count');

                    if (data.liked) {
                        icon.classList.add('text-primary');
                    } else {
                        icon.classList.remove('text-primary');
                    }
                    count.textContent = data.likes_count;
                });
        });
    });
});
