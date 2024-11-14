from django.views.generic import DetailView
from django.core.cache import cache
from .models import Scontrino
from django.db.models import Sum, Count, F, FloatField, ExpressionWrapper, Max, Min
from django.views.generic import TemplateView, DetailView
from django.contrib import messages  # Per gestire i messaggi di avviso
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
from .cache_monitor import CacheMonitor
from django.core.paginator import Paginator
import json
from django.core.files.storage import FileSystemStorage
from .utils import *
from django.core import serializers

# Create your views here.


@login_required
def stats(request):
    return render(request, template_name='scontrini/stats.html', context={'message': 'User logged!'})


class ScontriniLandingView(CreateView):
    template_name = 'scontrini/scontrini_landing.html'
    success_url = reverse_lazy('scontrinilanding')


@login_required
def carica_scontrino(request):
    if request.method == 'POST':
        try:
            data = request.POST.get('data')
            negozio_nome = request.POST.get('negozio_nome').strip()
            prodotti_json = request.POST.get('prodotti_json')

            if not all([data, negozio_nome, prodotti_json]):
                messages.error(request, 'Tutti i campi sono obbligatori')
                return redirect('scontrini:carica_scontrino')

            # Valida i prodotti
            prodotti_list = json.loads(prodotti_json)
            for prodotto in prodotti_list:
                if int(prodotto['quantita']) <= 0:
                    messages.error(
                        request, 'La quantità deve essere maggiore di zero')
                    return redirect('scontrini:carica_scontrino')
                if float(prodotto['prezzo']) <= 0:
                    messages.error(
                        request, 'Il prezzo deve essere maggiore di zero')
                    return redirect('scontrini:carica_scontrino')

            # Cerca il negozio case-insensitive o creane uno nuovo
            negozio = Negozio.objects.filter(nome__iexact=negozio_nome).first()
            if not negozio:
                negozio = Negozio.objects.create(nome=negozio_nome)

            # Crea lo scontrino
            scontrino = Scontrino.objects.create(
                utente=request.user,
                negozio=negozio,
                data=data,
                totale=float(request.POST.get('totale', 0))
            )

            # Salva i prodotti
            prodotti_list = json.loads(prodotti_json)
            for prodotto_data in prodotti_list:
                nome_prodotto = prodotto_data['nome']

                # Cerca o crea il prodotto
                prodotto = Prodotto.objects.filter(nome=nome_prodotto).first()
                if not prodotto:
                    prodotto = Prodotto.objects.create(nome=nome_prodotto)
                    # Se il prodotto è nuovo, assegna categoria 'altro'
                    categoria_altro, _ = Categoria.objects.get_or_create(
                        nome='altro')
                    prodotto.categoria = categoria_altro
                    prodotto.save()

                ListaProdotti.objects.create(
                    scontrino=scontrino,
                    prodotto=prodotto,
                    quantita=int(prodotto_data['quantita']),
                    prezzo_unitario=float(prodotto_data['prezzo'])
                )

            messages.success(request, 'Scontrino salvato con successo')
            return redirect('scontrini:successo')

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            messages.error(request, 'Errore nel formato dei dati')
            return redirect('scontrini:carica_scontrino')
    categorie = Categoria.objects.all()
    context = {
        'categorie': categorie,
        'categorie_json': json.dumps(list(categorie.values('id', 'nome')))
    }
    return render(request, 'scontrini/carica_scontrino.html', context)


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
    if not hasattr(scontrino, 'mostra_categoria'):
        scontrino.mostra_categoria = True  # Default: mostra categorie
        scontrino.save()

    lista_prodotti = scontrino.prodotti.all()

    # Prepara i dati dei prodotti con informazioni aggiuntive
    prodotti_elaborati = []
    for lista_item in lista_prodotti:
        prodotto = lista_item.prodotto  # Otteniamo il riferimento al Prodotto

        prodotto_info = {
            'id': lista_item.id,
            'prodotto_id': lista_item.prodotto.id,
            'nome_completo': prodotto.nome,
            'nome_display': prodotto.categoria.nome if (scontrino.mostra_categoria and
                                                        prodotto.categoria and
                                                        prodotto.categoria.nome != 'altro' and
                                                        prodotto.categoria_confermata)
            else prodotto.nome,
            'categoria': prodotto.categoria,
            'categoria_confermata': prodotto.categoria_confermata,
            'quantita': lista_item.quantita,
            'prezzo_unitario': lista_item.prezzo_unitario,
            'totale': lista_item.prezzo_unitario * lista_item.quantita
        }
        prodotti_elaborati.append(prodotto_info)

    # Paginazione
    paginator = Paginator(prodotti_elaborati, 10)
    page = request.GET.get('page', 1)

    try:
        prodotti = paginator.page(page)
    except:
        prodotti = paginator.page(1)

    # Ottieni tutte le categorie per il form di modifica
    categorie = Categoria.objects.all()

    return render(request, 'scontrini/dettagli_scontrino.html', {
        'scontrino': scontrino,
        'prodotti': prodotti,
        'categorie': categorie
    })


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

    context = {
        'prodotti': prodotti_paginati,
        'filtro_attuale': filtro,
        'ordine_attuale': ordine
    }

    # Renderizza sia la lista che la paginazione
    html = render_to_string(
        'scontrini/partials/prodotti_list.html',
        context
    )

    pagination_html = render_to_string(
        'scontrini/partials/pagination.html',
        context
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
        page = self.request.GET.get('page', 1)

        context['filtro_attuale'] = filtro
        context['ordine_attuale'] = ordine

        supermercati = self.get_supermercati_filtrati(filtro, ordine, user)

        # Aggiungi paginazione
        paginator = Paginator(list(supermercati), 10)
        try:
            supermercati_paginati = paginator.page(page)
        except:
            supermercati_paginati = paginator.page(1)

        context['supermercati'] = supermercati_paginati
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
    page = request.GET.get('page', 1)
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

    paginator = Paginator(list(supermercati), 10)
    supermercati_paginati = paginator.get_page(page)

    context = {
        'supermercati': supermercati_paginati,
        'filtro_attuale': filtro,
        'ordine_attuale': ordine
    }

    html = render_to_string(
        'scontrini/partials/supermercati_list.html', context)
    pagination_html = render_to_string(
        'scontrini/partials/pagination.html', context)

    return JsonResponse({
        'html': html,
        'pagination': pagination_html
    })


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
            'spese_giorno': list(spese),  # lista
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
            'spese_giorno': list(spese),  # una lista
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
        filtro = self.request.GET.get('filtro', 'all_time')

        # Ottieni gli scontrini filtrati per data
        if filtro == '1mese':
            scontrini = Scontrino.objects.filter(
                data__gte=now()-timedelta(days=30),
                utente=self.request.user
            )
        elif filtro == '6mesi':
            scontrini = Scontrino.objects.filter(
                data__gte=now()-timedelta(days=180),
                utente=self.request.user
            )
        elif filtro == '1anno':
            scontrini = Scontrino.objects.filter(
                data__gte=now()-timedelta(days=365),
                utente=self.request.user
            )
        else:  # all_time
            scontrini = Scontrino.objects.filter(utente=self.request.user)

        # Filtriamo i prodotti basandoci sugli scontrini filtrati
        lista_prodotti = ListaProdotti.objects.filter(
            prodotto=prodotto,
            scontrino__in=scontrini
        )

        # Il resto dei calcoli rimane invariato ma usa lista_prodotti filtrata
        context['quantita_ordinata'] = lista_prodotti.aggregate(
            Sum('quantita'))['quantita__sum'] or 0

        costo_totale = lista_prodotti.aggregate(
            totale=Sum(F('prezzo_unitario') * F('quantita')))['totale'] or 0
        context['costo_totale'] = costo_totale

        context['costo_medio'] = round(float(
            costo_totale) / context['quantita_ordinata'], 2) if context['quantita_ordinata'] else 0

        context['supermercati_diversi'] = scontrini.filter(
            prodotti__prodotto=prodotto).values('negozio').distinct().count()
        context['prezzo_piu_caro'] = lista_prodotti.aggregate(
            Max('prezzo_unitario'))['prezzo_unitario__max'] or 0
        context['prezzo_piu_economico'] = lista_prodotti.aggregate(
            Min('prezzo_unitario'))['prezzo_unitario__min'] or 0

        if lista_prodotti.exists():
            context['prima_volta_acquistato'] = lista_prodotti.earliest(
                'scontrino__data').scontrino.data
            context['ultima_volta_acquistato'] = lista_prodotti.latest(
                'scontrino__data').scontrino.data
        else:
            context['prima_volta_acquistato'] = None
            context['ultima_volta_acquistato'] = None

        context['filtro_attuale'] = filtro
        return context


@login_required
def analizza_scontrino(request):
    if request.method == 'POST' and request.FILES.get('scontrino_foto'):
        try:
            temp_file = request.FILES['scontrino_foto']
            fs = FileSystemStorage(location='temp_receipts/')
            filename = fs.save(temp_file.name, temp_file)
            file_path = fs.path(filename)

            dati_scontrino = estrai_dati_scontrino(file_path)
            fs.delete(filename)

            # Processa i prodotti prima di inviarli
            prodotti_processati = []
            for idx, nome_prodotto in enumerate(dati_scontrino['prodotti']):
                # Cerca prodotto esistente
                prodotto = Prodotto.objects.filter(
                    nome__iexact=nome_prodotto).first()

                if prodotto:
                    if prodotto.categoria_confermata:
                        print(
                            f"Prodotto esistente '{nome_prodotto}' - usando categoria confermata: {prodotto.categoria.nome}")
                    else:
                        print(
                            f"Prodotto esistente '{nome_prodotto}' - categoria non confermata, provo categorizzazione")
                        categoria, confermata = categorizza_prodotto(
                            nome_prodotto)
                        prodotto.categoria = categoria
                        prodotto.save()
                else:
                    print(
                        f"Nuovo prodotto '{nome_prodotto}' - creo e categorizzo")
                    categoria, confermata = categorizza_prodotto(nome_prodotto)
                    prodotto = Prodotto.objects.create(
                        nome=nome_prodotto,
                        categoria=categoria,
                        categoria_confermata=confermata
                    )

                prodotti_processati.append({
                    'nome': prodotto.nome,
                    'categoria': prodotto.categoria.nome,
                    'prezzo': dati_scontrino['prezzi'][idx] if idx < len(dati_scontrino['prezzi']) else 0
                })

            categorie = list(Categoria.objects.values('id', 'nome'))

            return JsonResponse({
                'success': True,
                'prodotti': prodotti_processati,
                'totale': dati_scontrino['totale'],
                'categorie': categorie
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


@login_required
def salva_scontrino_foto(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            data_scontrino = data.get('data')
            negozio_nome = data.get('negozio')
            prodotti = data.get('prodotti', [])
            totale = sum(float(p['prezzo']) *
                         float(p.get('quantita', 1)) for p in prodotti)

            # Crea o recupera il negozio
            negozio = Negozio.objects.get_or_create(nome=negozio_nome)[0]

            # Crea lo scontrino
            scontrino = Scontrino.objects.create(
                data=data_scontrino,
                negozio=negozio,
                utente=request.user,
                totale=totale
            )

            # Salva i prodotti
            for prod in prodotti:
                categoria = Categoria.objects.get(id=prod['categoria'])
                prodotto = Prodotto.objects.get_or_create(
                    nome=prod['nome'],
                    defaults={'categoria': categoria}
                )[0]

                ListaProdotti.objects.create(
                    scontrino=scontrino,
                    prodotto=prodotto,
                    quantita=prod.get('quantita', 1),
                    prezzo_unitario=prod['prezzo']
                )

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': 'Metodo non permesso'})


@login_required
def crea_categoria(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nome_categoria = data.get('nome', '').lower().strip()

            if not nome_categoria:
                return JsonResponse({
                    'success': False,
                    'error': 'Nome categoria richiesto'
                })

            # Cerca prima la categoria esistente (case-insensitive)
            categoria = Categoria.objects.filter(
                nome__iexact=nome_categoria).first()
            if not categoria:
                categoria = Categoria.objects.create(nome=nome_categoria)

            return JsonResponse({
                'success': True,
                'categoria_id': categoria.id,
                'categoria_nome': categoria.nome
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Dati non validi'
            })

    return JsonResponse({
        'success': False,
        'error': 'Metodo non permesso'
    })


@login_required
def aggiorna_categoria_prodotto(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prodotto_id = data.get('prodotto_id')
            categoria_id = data.get('categoria_id')

            prodotto = get_object_or_404(Prodotto, id=prodotto_id)
            categoria = get_object_or_404(Categoria, id=categoria_id)

            prodotto.categoria = categoria
            prodotto.categoria_confermata = True
            prodotto.save()
            print(
                f"{prodotto.nome} salvato con categoria {prodotto.categoria} ed è: {prodotto.categoria_confermata}")

            print(
                f"Aggiornata categoria per '{prodotto.nome}' a '{categoria.nome}' (confermata > agg_cat_prod)")

            return JsonResponse({
                'success': True,
                'categoria_nome': categoria.nome
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'ayy: ' + str(e)
            })
    return JsonResponse({'success': False, 'error': 'Metodo non permesso'})


@login_required
def toggle_visualizzazione_categoria(request, scontrino_id):
    if request.method == 'POST':
        try:
            scontrino = get_object_or_404(
                Scontrino, id=scontrino_id, utente=request.user)
            scontrino.mostra_categoria = not scontrino.mostra_categoria
            scontrino.save()

            # Forza il refresh della pagina
            return JsonResponse({
                'success': True,
                'mostra_categoria': scontrino.mostra_categoria
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Metodo non permesso'})
