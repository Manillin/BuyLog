document.addEventListener('DOMContentLoaded', function () {
    const commentTextarea = document.getElementById('commento');
    const charCountSpan = document.getElementById('char-count');
    const maxLength = 300;

    if (commentTextarea && charCountSpan) {
        commentTextarea.addEventListener('input', function () {
            const remaining = maxLength - this.value.length;
            charCountSpan.textContent = remaining;

            if (remaining < 0) {
                commentTextarea.classList.add('is-invalid');
                charCountSpan.classList.add('text-danger');
            } else {
                commentTextarea.classList.remove('is-invalid');
                charCountSpan.classList.remove('text-danger');
            }
        });

        // Inizializza il conteggio con il valore esistente (se presente)
        const initialRemaining = maxLength - commentTextarea.value.length;
        charCountSpan.textContent = initialRemaining;
    }
});
