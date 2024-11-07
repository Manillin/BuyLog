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
from django.db.models import Count
from django.utils import timezone

# Create your views here.


class RecensioniListView(ListView):
    model = Review
    template_name = 'recensioni/lista_recensioni.html'
    context_object_name = 'recensioni'
    paginate_by = 9

    def get_queryset(self):
        # Questo metodo sostituisce il queryset predefinito
        return Negozio.objects.annotate(
            num_recensioni=Count('recensioni'),
            media_recensioni=Avg('recensioni__voto_generale')
        ).order_by('-num_recensioni', '-media_recensioni')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Usa page_obj invece di sovrascrivere negozi
        context['negozi'] = context['page_obj']
        return context


class NegozioRecensioniView(DetailView):
    model = Negozio
    template_name = 'recensioni/recensioni_negozio.html'
    context_object_name = 'negozio'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recensioni_list = Review.objects.filter(negozio=self.object)

        # Calcola la media delle recensioni
        media_recensioni = 0
        if recensioni_list.exists():
            media_recensioni = recensioni_list.aggregate(
                Avg('voto_generale'))['voto_generale__avg']
        context['media_recensioni'] = media_recensioni

        # Ordina per data o likes
        order_by = self.request.GET.get('order_by', '-data')
        context['current_order'] = order_by

        if order_by == 'likes':
            recensioni_list = recensioni_list.annotate(
                like_count=Count('likes')).order_by('-like_count', '-data')
        else:
            recensioni_list = recensioni_list.order_by('-data')

        paginator = Paginator(recensioni_list, 5)
        page = self.request.GET.get('page')
        context['recensioni'] = paginator.get_page(page)
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
            existing_review.data = timezone.now()  # Aggiorna la data con l'ultima modifica
            existing_review.likes.clear()  # Rimuove tutti i like
            existing_review.save()
            self.object = existing_review
        else:
            # Crea una nuova recensione
            self.object = form.save(commit=False)
            self.object.utente = self.request.user
            self.object.negozio = negozio
            self.object.save()

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
    recensioni_list = Review.objects.filter(negozio=negozio)

    # Calcola la media di tutte le valutazioni
    media_recensioni = 0
    if recensioni_list.exists():
        media_recensioni = sum(r.calcola_media()
                               for r in recensioni_list) / recensioni_list.count()

    # Ordina per data o likes
    order_by = request.GET.get('order_by', '-data')
    if order_by == 'likes':
        recensioni_list = recensioni_list.annotate(
            like_count=Count('likes')).order_by('-like_count', '-data')
    else:
        recensioni_list = recensioni_list.order_by('-data')

    paginator = Paginator(recensioni_list, 5)
    page = request.GET.get('page')
    recensioni = paginator.get_page(page)

    return render(request, 'recensioni/recensioni_negozio.html', {
        'negozio': negozio,
        'recensioni': recensioni,
        'media_recensioni': media_recensioni,
        'current_order': order_by
    })
