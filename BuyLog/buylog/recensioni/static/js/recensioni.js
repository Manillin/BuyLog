document.addEventListener('DOMContentLoaded', function () {
    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfTokenElement) {
        console.error('CSRF token non trovato');
        return;
    }
    const csrfToken = csrfTokenElement.value;

    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            const reviewId = this.dataset.reviewId;

            fetch(`/recensioni/like/${reviewId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    const icon = this.querySelector('i');
                    const count = this.querySelector('.like-count');

                    if (data.liked) {
                        icon.classList.add('text-primary');
                    } else {
                        icon.classList.remove('text-primary');
                    }
                    count.textContent = data.likes_count;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    });
});
