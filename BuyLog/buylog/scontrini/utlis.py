import re
from .models import *


def categorizza_prodotto(nome_prodotto):
    # Prima controlla se il prodotto è già conosciuto
    try:
        prodotto_conosciuto = ProdottoConosciuto.objects.get(
            nome_specifico__iexact=nome_prodotto
        )
        return prodotto_conosciuto.categoria, True
    except ProdottoConosciuto.DoesNotExist:
        # Se non è conosciuto, prova con le regex
        patterns = {
            'pane': r'\b(pane|baguette|filone)\b',
            'latte': r'\b(latte|yogurt)\b',
            # aggiungi altri pattern...
        }

        nome_lower = nome_prodotto.lower()
        for categoria_nome, pattern in patterns.items():
            if re.search(pattern, nome_lower):
                categoria, _ = Categoria.objects.get_or_create(
                    nome=categoria_nome)
                return categoria, False

        # Se non trova match, restituisce la categoria 'altro'
        categoria, _ = Categoria.objects.get_or_create(nome='altro')
        return categoria, False
