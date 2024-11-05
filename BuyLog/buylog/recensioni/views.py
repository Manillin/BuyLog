from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .models import Review
from scontrini.models import Negozio
from django.urls import reverse_lazy
from django.db.models import Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.urls import reverse

# Create your views here.


class RecensioniListView(ListView):
    model = Review
    template_name = 'recensioni/lista_recensioni.html'
    context_object_name = 'recensioni'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['negozi'] = Negozio.objects.annotate(
            media_recensioni=Avg('recensioni__voto_generale')
        ).order_by('-media_recensioni')
        return context


class NegozioRecensioniView(DetailView):
    model = Negozio
    template_name = 'recensioni/recensioni_negozio.html'
    context_object_name = 'negozio'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recensioni_list = Review.objects.filter(
            negozio=self.object).order_by('-data')

        # Calcola la media delle recensioni
        media = recensioni_list.aggregate(
            Avg('voto_generale')
        )['voto_generale__avg'] or 0

        # Paginazione
        paginator = Paginator(recensioni_list, 5)  # 5 recensioni per pagina
        page = self.request.GET.get('page')
        recensioni = paginator.get_page(page)

        context['recensioni'] = recensioni
        context['media_recensioni'] = media
        return context


class AggiungiRecensioneView(LoginRequiredMixin, CreateView):
    model = Review
    template_name = 'recensioni/aggiungi_recensione.html'
    fields = ['qualita_prezzo', 'pulizia', 'servizio', 'varieta',
              'voto_generale', 'commento']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        negozio = get_object_or_404(Negozio, pk=self.kwargs['negozio_id'])
        context['negozio'] = negozio

        # Controlla se esiste già una recensione
        existing_review = Review.objects.filter(
            utente=self.request.user,
            negozio=negozio
        ).first()

        if existing_review:
            context['existing_review'] = existing_review
            # Pre-popoliamo i campi con i valori esistenti
            for field in self.fields:
                context['initial_' + field] = getattr(existing_review, field)

        return context

    def form_valid(self, form):
        negozio = get_object_or_404(Negozio, pk=self.kwargs['negozio_id'])
        existing_review = Review.objects.filter(
            utente=self.request.user,
            negozio=negozio
        ).first()

        if existing_review:
            # Aggiorna la recensione esistente invece di crearne una nuova
            for field in self.fields:
                setattr(existing_review, field, form.cleaned_data[field])
            existing_review.save()
            self.object = existing_review
        else:
            # Crea una nuova recensione
            self.object = form.save(commit=False)
            self.object.utente = self.request.user
            self.object.negozio = negozio
            self.object.save()

        # Invece di chiamare super().form_valid(form), ritorniamo direttamente alla pagina del negozio
        return redirect(reverse('recensioni:recensioni_negozio', kwargs={'pk': negozio.id}))


@login_required
def toggle_like(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user in review.likes.all():
        review.likes.remove(request.user)
        liked = False
    else:
        review.likes.add(request.user)
        liked = True
    return JsonResponse({
        'liked': liked,
        'likes_count': review.likes.count()
    })


def testfunc(request):
    print("TEST!!!")


def recensioni_negozio(request, negozio_id):
    negozio = get_object_or_404(Negozio, pk=negozio_id)
    recensioni_list = Review.objects.filter(negozio=negozio).order_by('-data')

    paginator = Paginator(recensioni_list, 5)  # 5 recensioni per pagina
    page = request.GET.get('page')
    recensioni = paginator.get_page(page)

    return render(request, 'recensioni/recensioni_negozio.html', {
        'negozio': negozio,
        'recensioni': recensioni
    })
