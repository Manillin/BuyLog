from django.views.generic import DetailView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from .models import Scontrino
from django.db.models import Sum, Count, F, FloatField, ExpressionWrapper, Max, Min
from django.views.generic import TemplateView, DetailView
from django.contrib import messages  # Per gestire i messaggi di avviso
from django.contrib import messages  # Per gestire messaggi di avviso
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.db import models
from django.db.models import Sum, Count, F, FloatField, ExpressionWrapper
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Scontrino, Negozio, ListaProdotti
from .forms import *
from django.http import JsonResponse
from django.utils.timezone import now, timedelta
from django.template.loader import render_to_string
from django.utils.text import slugify  # pulire nome negozio rimuovendo spazi
from django.db.models import Q  # ricerche case insensitive
from .cache_monitor import CacheMonitor
from django.core.paginator import Paginator


# Create your views here.


@login_required  # TODO: deve essere visibile anche dalla home questo blocco
def stats(request):
    return render(request, template_name='scontrini/stats.html', context={'message': 'User logged!'})


class ScontriniLandingView(CreateView):
    # form_class = CustomFormTBD
    template_name = 'scontrini/scontrini_landing.html'
    success_url = reverse_lazy('scontrinilanding')


def carica_scontrino(request):
    if 'prodotti' not in request.session:
        request.session['prodotti'] = []

    negozio_nome_sessione = request.session.get('negozio_nome', '')

    if request.method == 'POST' and 'aggiungi_prodotto' in request.POST:
        prodotto_form = ListaProdottiForm(request.POST)
        scontrino_form = ScontrinoForm(request.POST)

        if prodotto_form.is_valid():
            prodotto_dati = prodotto_form.cleaned_data
            prodotto_dati['quantita'] = float(prodotto_dati['quantita'])
            prodotto_dati['prezzo_unitario'] = float(
                prodotto_dati['prezzo_unitario'])
            request.session['prodotti'].append(prodotto_dati)
            request.session.modified = True

        if scontrino_form.is_valid():
            negozio_nome = scontrino_form.cleaned_data['negozio_nome'].strip()
            request.session['negozio_nome'] = negozio_nome

        return redirect('scontrini:carica_scontrino')

    elif request.method == 'POST' and 'salva_scontrino' in request.POST:
        scontrino_form = ScontrinoForm(request.POST)
        if scontrino_form.is_valid() and len(request.session['prodotti']) > 0:
            negozio_nome = scontrino_form.cleaned_data['negozio_nome'].strip()
            negozio_nome_pulito = slugify(
                negozio_nome, allow_unicode=True).replace("-", "").lower()

            negozio = Negozio.objects.filter(
                Q(nome__iexact=negozio_nome_pulito) | Q(nome__icontains=negozio_nome_pulito.replace(" ", ""))).first()

            if not negozio:
                negozio = Negozio.objects.create(nome=negozio_nome)

            # NEW:
            totale_scontrino = sum(
                prodotto['quantita'] * prodotto['prezzo_unitario'] for prodotto in request.session['prodotti']
            )

            scontrino = Scontrino.objects.create(
                utente=request.user,
                negozio=negozio,
                data=scontrino_form.cleaned_data['data'],
                # NEW:
                totale=totale_scontrino
            )

            for prodotto_dati in request.session['prodotti']:
                prodotto_nome = prodotto_dati['prodotto']
                prodotto_nome_pulito = slugify(
                    prodotto_nome, allow_unicode=True).replace("-", "").lower()

                prodotto = Prodotto.objects.filter(
                    nome__iexact=prodotto_nome_pulito).first()
                if not prodotto:
                    prodotto = Prodotto.objects.create(nome=prodotto_nome)

                ListaProdotti.objects.create(
                    scontrino=scontrino,
                    prodotto=prodotto,
                    quantita=prodotto_dati['quantita'],
                    prezzo_unitario=prodotto_dati['prezzo_unitario']
                )

            del request.session['prodotti']
            if 'negozio_nome' in request.session:
                del request.session['negozio_nome']

            return redirect('scontrini:successo')

    else:
        scontrino_form = ScontrinoForm(
            initial={'negozio_nome': negozio_nome_sessione})
        prodotto_form = ListaProdottiForm()

    prodotti_nella_sessione = request.session.get('prodotti', [])

    return render(request, 'scontrini/carica_scontrino.html', {
        'scontrino_form': scontrino_form,
        'prodotto_form': prodotto_form,
        'prodotti': prodotti_nella_sessione
    })

# Handler della richiesta AJAX mandata da js per aggiungere un prodotto alla sessione


def aggiungi_prodotto(request):
    if request.method == 'POST':
        # recupero dati forniti dal modale
        quantita = request.POST.get('quantita')
        prezzo_unitario = request.POST.get('prezzo_unitario')
        nome_prodotto = request.POST.get('nome_prodotto')

        # controllo integrità e aggiungo il dizionario alla sessione se valido
        if quantita and prezzo_unitario and nome_prodotto:
            prodotto_dati = {
                'quantita': float(quantita),
                'prezzo_unitario': float(prezzo_unitario),
                'prodotto': nome_prodotto
            }
            # nel caso sia il primo prodotto caricato, creo la lista di dizionari prodotto
            if 'prodotti' not in request.session:
                request.session['prodotti'] = []
            request.session['prodotti'].append(prodotto_dati)
            request.session.modified = True
            return JsonResponse({'success': True, 'prodotti_count': len(request.session['prodotti'])})

    return JsonResponse({'success': False})


def successo(request):
    return render(request, 'scontrini/successo.html')


@login_required
def lista_scontrini(request):
    page = request.GET.get('page', 1)
    scontrini = Scontrino.objects.filter(utente=request.user).order_by('-data')

    # Crea il paginatore
    paginator = Paginator(scontrini, 10)  # 15 scontrini per pagina
    try:
        scontrini_paginati = paginator.page(page)
    except:
        scontrini_paginati = paginator.page(1)

    return render(request, 'scontrini/lista_scontrini.html', {
        'scontrini': scontrini_paginati
    })


@login_required
def dettagli_scontrino(request, scontrino_id):
    scontrino = get_object_or_404(
        Scontrino, id=scontrino_id, utente=request.user)
    prodotti = scontrino.prodotti.all()
    return render(request, 'scontrini/dettagli_scontrino.html', {'scontrino': scontrino, 'prodotti': prodotti})


@login_required
def elimina_scontrino(request, scontrino_id):
    scontrino = get_object_or_404(
        Scontrino, id=scontrino_id, utente=request.user)
    scontrino.delete()
    return redirect('scontrini:lista_scontrini')

# funzione per la visualizzazione delle statistiche in stile dashbaord


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'scontrini/stats.html'

    # ottiene il contesto -> statistiche dell'utente che sta visualizzando le statistiche
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user

        # Filtra in base al parametro di filtro (ad es. 'all time', '1 mese', '6 mesi', ecc.)
        filtro = self.request.GET.get(
            'filtro', '6mesi')  # cambio filtro default
        context['filtro_attuale'] = filtro
        # fetch scontrini fitrati
        scontrini = self.get_scontrini_filtrati(filtro, user)

        # Statistiche principali
        context['numero_scontrini'] = scontrini.count()
        context['totale_speso'] = round(
            scontrini.aggregate(Sum('totale'))['totale__sum'] or 0, 2)
        context['numero_articoli'] = ListaProdotti.objects.filter(
            scontrino__in=scontrini).aggregate(Sum('quantita'))['quantita__sum'] or 0

        # Grafico: spese per giorno
        spese_giorno = self.get_spese_per_giorno(scontrini)
        # Converti il QuerySet in una lista di dizionari
        context['spese_giorno'] = list(spese_giorno)

        # Top prodotti e supermercati
        context['top_prodotti'] = self.get_top_prodotti(scontrini)
        context['top_supermercati'] = self.get_top_supermercati(scontrini)

        return context

    # fetch degli scontrini applicando un filtro per uno specifico user (utente loggato)
    def get_scontrini_filtrati(self, filtro, user):
        # Implementa i filtri per 1 mese, 6 mesi, 1 anno, etc.
        if filtro == '1mese':
            return Scontrino.objects.filter(data__gte=now()-timedelta(days=30), utente=user)
        elif filtro == '6mesi':
            return Scontrino.objects.filter(data__gte=now()-timedelta(days=180), utente=user)
        elif filtro == '1anno':
            return Scontrino.objects.filter(data__gte=now()-timedelta(days=365), utente=user)
        else:
            # filtro default: all_time
            return Scontrino.objects.filter(utente=user)

    def get_spese_per_giorno(self, scontrini):
        # Aggrega le spese per giorno
        spese = scontrini.extra(select={'giorno': 'date(data)'}).values(
            'giorno').annotate(spesa_giornaliera=Sum('totale')).order_by('giorno')
        return spese

    def get_top_prodotti(self, scontrini):
        # Aggrega i prodotti ordinati per frequenza
        return ListaProdotti.objects.filter(scontrino__in=scontrini).values('prodotto__nome').annotate(
            total_ordinato=Sum('quantita')
        ).order_by('-total_ordinato')[:5]

    def get_top_supermercati(self, scontrini):
        # Aggrega i supermercati per frequenza
        return scontrini.values('negozio__nome').annotate(
            frequenza=Count('negozio')
        ).order_by('-frequenza')[:3]


def aggiorna_grafico(request):
    filtro = request.GET.get('filtro', 'all_time')
    user = request.user

    if filtro == '1mese':
        scontrini = Scontrino.objects.filter(
            data__gte=now()-timedelta(days=30), utente=user)
    elif filtro == '6mesi':
        scontrini = Scontrino.objects.filter(
            data__gte=now()-timedelta(days=180), utente=user)
    elif filtro == '1anno':
        scontrini = Scontrino.objects.filter(
            data__gte=now()-timedelta(days=365), utente=user)
    else:
        scontrini = Scontrino.objects.filter(utente=user)

    spese = scontrini.extra(select={'giorno': 'date(data)'}).values(
        'giorno').annotate(spesa_giornaliera=Sum('totale')).order_by('giorno')

    # es query: {'giorno': '2023-08-08', 'spesa_giornaliera': Decimal('25')

    labels = [spesa['giorno'] for spesa in spese]
    data = [spesa['spesa_giornaliera'] for spesa in spese]

    # Statistiche principali
    numero_scontrini = scontrini.count()
    totale_speso = round(scontrini.aggregate(
        Sum('totale'))['totale__sum'] or 0, 2)
    numero_articoli = ListaProdotti.objects.filter(
        scontrino__in=scontrini).aggregate(Sum('quantita'))['quantita__sum'] or 0

    # Top prodotti e supermercati
    top_prodotti = list(ListaProdotti.objects.filter(scontrino__in=scontrini).values('prodotto__nome').annotate(
        total_ordinato=Sum('quantita')).order_by('-total_ordinato')[:5])

    top_supermercati = list(scontrini.values('negozio__nome').annotate(
        frequenza=Count('negozio')).order_by('-frequenza')[:3])

    return JsonResponse({
        'labels': labels,
        'data': data,
        'numero_scontrini': numero_scontrini,
        'totale_speso': totale_speso,
        'numero_articoli': numero_articoli,
        'top_prodotti': top_prodotti,
        'top_supermercati': top_supermercati,
        'filtro_attuale': filtro
    })

    # Visualizzazione GLOBALE:


class TuttiProdottiView(LoginRequiredMixin, TemplateView):
    template_name = 'scontrini/tutti_prodotti.html'
    prodotti_per_pagina = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        filtro = self.request.GET.get('filtro', 'all_time')
        ordine = self.request.GET.get('ordine', '-quantita_ordinata')
        page = self.request.GET.get('page', 1)

        context['filtro_attuale'] = filtro
        context['ordine_attuale'] = ordine

        prodotti = self.get_prodotti_filtrati(filtro, ordine, user)

        # Creiamo il paginatore
        paginator = Paginator(list(prodotti), self.prodotti_per_pagina)
        prodotti_paginati = paginator.get_page(page)

        context['prodotti'] = prodotti_paginati
        return context

    def get_prodotti_filtrati(self, filtro, ordine, user):
        scontrini = self.get_scontrini_filtrati(filtro, user)
        prodotti = ListaProdotti.objects.filter(scontrino__in=scontrini).values(
            'prodotto__nome',
            'prodotto__id'  # Aggiungiamo l'ID del prodotto
        ).annotate(
            quantita_ordinata=Sum('quantita'),
            totale_speso=Sum(ExpressionWrapper(
                F('prezzo_unitario') * F('quantita'), output_field=FloatField())),
            numero_supermercati=Count('scontrino__negozio', distinct=True),
            prezzo_medio=ExpressionWrapper(Sum(
                F('prezzo_unitario') * F('quantita')) / Sum('quantita'),
                output_field=FloatField())
        ).order_by(ordine)
        return prodotti

    def get_scontrini_filtrati(self, filtro, user):
        if filtro == '1mese':
            return Scontrino.objects.filter(data__gte=now()-timedelta(days=30), utente=user)
        elif filtro == '6mesi':
            return Scontrino.objects.filter(data__gte=now()-timedelta(days=180), utente=user)
        elif filtro == '1anno':
            return Scontrino.objects.filter(data__gte=now()-timedelta(days=365), utente=user)
        else:
            return Scontrino.objects.filter(utente=user)


def aggiorna_tabella_prodotti(request):
    filtro = request.GET.get('filtro', 'all_time')
    ordine = request.GET.get('ordine', '-quantita_ordinata')
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '')
    user = request.user

    # Ottieni gli scontrini filtrati
    if filtro == '1mese':
        scontrini = Scontrino.objects.filter(
            data__gte=now()-timedelta(days=30), utente=user)
    elif filtro == '6mesi':
        scontrini = Scontrino.objects.filter(
            data__gte=now()-timedelta(days=180), utente=user)
    elif filtro == '1anno':
        scontrini = Scontrino.objects.filter(
            data__gte=now()-timedelta(days=365), utente=user)
    else:
        scontrini = Scontrino.objects.filter(utente=user)

    # Query base per i prodotti
    prodotti = ListaProdotti.objects.filter(scontrino__in=scontrini)

    # Applica la ricerca se presente
    if search:
        prodotti = prodotti.filter(prodotto__nome__icontains=search)

    # Aggregazione e annotazione
    prodotti = prodotti.values(
        'prodotto__nome',
        'prodotto__id'
    ).annotate(
        quantita_ordinata=Sum('quantita'),
        totale_speso=Sum(ExpressionWrapper(
            F('prezzo_unitario') * F('quantita'), output_field=FloatField())),
        numero_supermercati=Count('scontrino__negozio', distinct=True),
        prezzo_medio=ExpressionWrapper(Sum(
            F('prezzo_unitario') * F('quantita')) / Sum('quantita'),
            output_field=FloatField())
    ).order_by(ordine)

    # Paginazione
    paginator = Paginator(list(prodotti), 15)
    prodotti_paginati = paginator.get_page(page)

    # Renderizza sia la lista che la paginazione
    html = render_to_string(
        'scontrini/partials/prodotti_list.html',
        {'prodotti': prodotti_paginati}
    )

    pagination_html = render_to_string(
        'scontrini/partials/pagination.html',
        {
            'prodotti': prodotti_paginati,
            'filtro_attuale': filtro,
            'ordine_attuale': ordine
        }
    )

    return JsonResponse({
        'html': html,
        'pagination': pagination_html
    })


class TuttiSupermercatiView(LoginRequiredMixin, TemplateView):
    template_name = 'scontrini/tutti_supermercati.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        filtro = self.request.GET.get('filtro', 'all_time')
        ordine = self.request.GET.get('ordine', '-numero_visite')
        context['filtro_attuale'] = filtro
        context['ordine_attuale'] = ordine
        supermercati = self.get_supermercati_filtrati(filtro, ordine, user)
        context['supermercati'] = supermercati
        return context

    def get_supermercati_filtrati(self, filtro, ordine, user):
        scontrini = self.get_scontrini_filtrati(filtro, user)
        supermercati = scontrini.values('negozio__nome').annotate(
            numero_visite=Count('negozio'),
            totale_speso=Sum('totale')
        ).order_by(ordine)
        return supermercati

    def get_scontrini_filtrati(self, filtro, user):
        if filtro == '1mese':
            return Scontrino.objects.filter(data__gte=now()-timedelta(days=30), utente=user)
        elif filtro == '6mesi':
            return Scontrino.objects.filter(data__gte=now()-timedelta(days=180), utente=user)
        elif filtro == '1anno':
            return Scontrino.objects.filter(data__gte=now()-timedelta(days=365), utente=user)
        else:
            return Scontrino.objects.filter(utente=user)


def aggiorna_tabella_supermercati(request):
    filtro = request.GET.get('filtro', 'all_time')
    ordine = request.GET.get('ordine', '-numero_visite')
    user = request.user

    if filtro == '1mese':
        scontrini = Scontrino.objects.filter(
            data__gte=now()-timedelta(days=30), utente=user)
    elif filtro == '6mesi':
        scontrini = Scontrino.objects.filter(
            data__gte=now()-timedelta(days=180), utente=user)
    elif filtro == '1anno':
        scontrini = Scontrino.objects.filter(
            data__gte=now()-timedelta(days=365), utente=user)
    else:
        scontrini = Scontrino.objects.filter(utente=user)

    supermercati = scontrini.values('negozio__nome').annotate(
        numero_visite=Count('negozio'),
        totale_speso=Sum('totale')
    ).order_by(ordine)

    html = render_to_string(
        'scontrini/partials/supermercati_list.html', {'supermercati': supermercati})
    return JsonResponse({'html': html})


# Visualizzazione pagina DEMO:

class DemoStatsView(TemplateView):
    template_name = 'scontrini/demo_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Verifica se i dati sono già in cache
        cached_data = cache.get('demo_stats_data')
        CacheMonitor.log_cache_status('demo_stats_data')
        if cached_data:
            context.update(cached_data)
            return context

        # Fetch dei dati aggregati
        filtro = '1mese'  # Filtro predefinito
        start_date = now() - timedelta(days=30)
        scontrini = Scontrino.objects.filter(data__gte=start_date)
        spese = scontrini.extra(select={'giorno': 'date(data)'}).values(
            'giorno').annotate(spesa_giornaliera=Sum('totale')).order_by('giorno')

        labels = [spesa['giorno'] for spesa in spese]
        data = [spesa['spesa_giornaliera'] for spesa in spese]

        numero_scontrini = scontrini.count()
        totale_speso = round(scontrini.aggregate(
            Sum('totale'))['totale__sum'] or 0, 2)
        numero_articoli = ListaProdotti.objects.filter(
            scontrino__in=scontrini).aggregate(Sum('quantita'))['quantita__sum'] or 0

        top_prodotti = list(ListaProdotti.objects.filter(scontrino__in=scontrini).values('prodotto__nome').annotate(
            total_ordinato=Sum('quantita')).order_by('-total_ordinato')[:5])

        top_supermercati = list(scontrini.values('negozio__nome').annotate(
            frequenza=Count('negozio')).order_by('-frequenza')[:3])

        numero_utenti_registrati = User.objects.count()

        context.update({
            'labels': labels,
            'data': data,
            'numero_scontrini': numero_scontrini,
            'totale_speso': totale_speso,
            'numero_articoli': numero_articoli,
            'top_prodotti': top_prodotti,
            'top_supermercati': top_supermercati,
            'filtro_attuale': filtro,
            'spese_giorno': list(spese),  # Assicurati che sia una lista
            'numero_utenti_registrati': numero_utenti_registrati
        })

        # Crea una copia del contesto con solo i dati SERIALIZZABILI
        cache_data = {
            'labels': labels,
            'data': data,
            'numero_scontrini': numero_scontrini,
            'totale_speso': totale_speso,
            'numero_articoli': numero_articoli,
            'top_prodotti': top_prodotti,
            'top_supermercati': top_supermercati,
            'filtro_attuale': filtro,
            'spese_giorno': list(spese),  # Assicurati che sia una lista
            'numero_utenti_registrati': numero_utenti_registrati,
            'cache_timestamp': now()
        }

        # Memorizza i dati in cache
        cache.set('demo_stats_data', cache_data,
                  60 * 15)  # Cache per 15 minuti

        return context
# Aggiornamento grafico demo


def aggiorna_grafico_demo(request):
    filtro = request.GET.get('filtro', '1mese')

    if filtro == '1mese':
        scontrini = Scontrino.objects.filter(
            data__gte=now()-timedelta(days=30))
    else:
        scontrini = Scontrino.objects.all()

    spese = scontrini.extra(select={'giorno': 'date(data)'}).values(
        'giorno').annotate(spesa_giornaliera=Sum('totale')).order_by('giorno')

    labels = [spesa['giorno'] for spesa in spese]
    data = [spesa['spesa_giornaliera'] for spesa in spese]

    numero_scontrini = scontrini.count()
    totale_speso = round(scontrini.aggregate(
        Sum('totale'))['totale__sum'] or 0, 2)
    numero_articoli = ListaProdotti.objects.filter(
        scontrino__in=scontrini).aggregate(Sum('quantita'))['quantita__sum'] or 0

    top_prodotti = list(ListaProdotti.objects.filter(scontrino__in=scontrini).values('prodotto__nome').annotate(
        total_ordinato=Sum('quantita')).order_by('-total_ordinato')[:5])

    top_supermercati = list(scontrini.values('negozio__nome').annotate(
        frequenza=Count('negozio')).order_by('-frequenza')[:3])

    return JsonResponse({
        'labels': labels,
        'data': data,
        'numero_scontrini': numero_scontrini,
        'totale_speso': totale_speso,
        'numero_articoli': numero_articoli,
        'top_prodotti': top_prodotti,
        'top_supermercati': top_supermercati,
        'filtro_attuale': filtro
    })


class RicercaProdottoView(LoginRequiredMixin, TemplateView):
    template_name = 'scontrini/lista_scontrini.html'

    def get(self, request, *args, **kwargs):
        prodotto_nome = request.GET.get('prodotto', '').strip()
        if prodotto_nome:
            try:
                prodotto = Prodotto.objects.get(nome__iexact=prodotto_nome)
                return redirect('scontrini:dettagli_prodotto', pk=prodotto.pk)
            except Prodotto.DoesNotExist:
                return render(request, self.template_name, {
                    'scontrini': Scontrino.objects.filter(utente=request.user),
                    'error_message': 'Prodotto inesistente, verifica di cercare un prodotto che hai acquistato'
                })
        return render(request, self.template_name, {
            'scontrini': Scontrino.objects.filter(utente=request.user)
        })


class DettagliProdottoView(LoginRequiredMixin, DetailView):
    model = Prodotto
    template_name = 'scontrini/dettagli_prodotto.html'
    context_object_name = 'prodotto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prodotto = self.get_object()
        lista_prodotti = ListaProdotti.objects.filter(prodotto=prodotto)
        scontrini = Scontrino.objects.filter(prodotti__prodotto=prodotto)

        # Calcolo quantità totale ordinata
        context['quantita_ordinata'] = lista_prodotti.aggregate(
            Sum('quantita'))['quantita__sum'] or 0

        # Calcolo costo totale (prezzo_unitario * quantità per ogni riga)
        costo_totale = lista_prodotti.aggregate(
            totale=Sum(F('prezzo_unitario') * F('quantita')))['totale'] or 0
        context['costo_totale'] = costo_totale

        # Calcolo costo medio (costo totale / quantità totale)
        context['costo_medio'] = round(float(
            costo_totale) / context['quantita_ordinata'], 2) if context['quantita_ordinata'] else 0

        # Altri calcoli
        context['supermercati_diversi'] = scontrini.values(
            'negozio').distinct().count()
        context['prezzo_piu_caro'] = lista_prodotti.aggregate(
            Max('prezzo_unitario'))['prezzo_unitario__max'] or 0
        context['prezzo_piu_economico'] = lista_prodotti.aggregate(
            Min('prezzo_unitario'))['prezzo_unitario__min'] or 0
        context['prima_volta_acquistato'] = lista_prodotti.earliest(
            'scontrino__data').scontrino.data if lista_prodotti.exists() else None
        context['ultima_volta_acquistato'] = lista_prodotti.latest(
            'scontrino__data').scontrino.data if lista_prodotti.exists() else None

        return context
