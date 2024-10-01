from django.contrib import messages  # Per gestire i messaggi di avviso
from django.contrib import messages  # Per gestire messaggi di avviso
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.db import models
from django.db.models import Sum, Count
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Scontrino, Negozio, ListaProdotti
from .forms import *
from django.http import JsonResponse
from django.utils.timezone import now, timedelta

from django.utils.text import slugify  # pulire nome negozio rimuovendo spazi
from django.db.models import Q  # ricerche case insensitive

# Create your views here.


@login_required  # TODO: deve essere visibile anche dalla home questo blocco
def stats(request):
    return render(request, template_name='scontrini/stats.html', context={'message': 'User logged!'})


def scontrini_home(request):
    template = 'scontrini/scontrini_landing.html'
    ctx = {'user': request.user}
    return render(request=request, template_name=template, context=ctx)


class ScontriniLandingView(CreateView):
    # form_class = CustomFormTBD
    template_name = 'scontrini/scontrini_landing.html'
    success_url = reverse_lazy('scontrinilanding')


def carica_scontrino22(request):
    # Inizializziamo la lista dei prodotti se non esiste ancora nella sessione
    if 'prodotti' not in request.session:
        request.session['prodotti'] = []

    # Conserviamo il nome del negozio nella sessione
    negozio_nome_sessione = request.session.get('negozio_nome', '')

    # Gestione aggiunta prodotto - 'aggiungi_prodotto' è il nome del bottone nel tmplt (vuol dire cliccato)
    if request.method == 'POST' and 'aggiungi_prodotto' in request.POST:
        prodotto_form = ListaProdottiForm(request.POST)
        scontrino_form = ScontrinoForm(request.POST)

        # Se il form del PRODOTTO è valido, lo aggiungiamo alla sessione
        if prodotto_form.is_valid():
            prodotto_dati = prodotto_form.cleaned_data
            # Convertiamo i campi in tipi serializzabili (float)
            prodotto_dati['quantita'] = float(prodotto_dati['quantita'])
            prodotto_dati['prezzo_unitario'] = float(
                prodotto_dati['prezzo_unitario'])

            # Aggiungiamo i prodotti serializzati al buffer 'prodotti' della sessione
            request.session['prodotti'].append(prodotto_dati)
            # sessione modificata
            request.session.modified = True

        # Se il form del negozio è valido, salviamo il nome del negozio nella sessione
        if scontrino_form.is_valid():
            negozio_nome = scontrino_form.cleaned_data['negozio_nome'].strip()
            # Memorizziamo il nome del negozio nella sessione
            request.session['negozio_nome'] = negozio_nome

        # TODO: da capire il redirect
        return redirect('scontrini:carica_scontrino')

    # Gestione salvataggio scontrino - 'salva_scontrino' è il nome del bottone nel tmplt
    elif request.method == 'POST' and 'salva_scontrino' in request.POST:
        scontrino_form = ScontrinoForm(request.POST)
        if scontrino_form.is_valid():
            negozio_nome = scontrino_form.cleaned_data['negozio_nome'].strip()
            negozio_nome_pulito = slugify(
                negozio_nome, allow_unicode=True).replace("-", "").lower()

            # Controlliamo se il negozio esiste nel database, se non esiste lo creiamo
            negozio = Negozio.objects.filter(
                Q(nome__iexact=negozio_nome_pulito) | Q(nome__icontains=negozio_nome_pulito.replace(" ", ""))).first()
            if not negozio:
                negozio = Negozio.objects.create(nome=negozio_nome)

            # Creiamo lo scontrino
            scontrino = Scontrino.objects.create(
                utente=request.user,
                negozio=negozio,
                data=scontrino_form.cleaned_data['data']
            )

            # Aggiungiamo i prodotti salvati dalla sessione allo scontrino:
            # Sto iterando nella lista di dizionari, dove ogni dizionario corrisponde a una entry, \
            # ossia  {'prodotto': 'nome_prodotto_generico', 'quantita': n, 'prezzo_unitario': x.xxx}.
            for prodotto_dati in request.session['prodotti']:
                prodotto_nome = prodotto_dati['prodotto']
                prodotto_nome_pulito = slugify(
                    prodotto_nome, allow_unicode=True).replace("-", "").lower()

                # Controllo se prodotto esiste, se non esiste lo creo nel DB
                prodotto = Prodotto.objects.filter(
                    nome__iexact=prodotto_nome_pulito).first()
                if not prodotto:
                    prodotto = Prodotto.objects.create(nome=prodotto_nome)

                # Aggiungiamo il prodotto alla lista
                ListaProdotti.objects.create(
                    scontrino=scontrino,
                    prodotto=prodotto,
                    quantita=prodotto_dati['quantita'],
                    prezzo_unitario=prodotto_dati['prezzo_unitario']
                )

            # Puliamo la sessione dopo il salvataggio
            del request.session['prodotti']
            # Pulisci il nome del negozio dalla sessione
            del request.session['negozio_nome']

            return redirect('scontrini:successo')

    else:
        # Se non stiamo facendo una richiesta POST, carichiamo il form con il negozio salvato dalla sessione
        scontrino_form = ScontrinoForm(
            initial={'negozio_nome': negozio_nome_sessione})
        prodotto_form = ListaProdottiForm()

    # Mostra la lista dei prodotti aggiunti finora
    prodotti_nella_sessione = request.session.get('prodotti', [])

    return render(request, 'scontrini/carica_scontrino.html', {
        'scontrino_form': scontrino_form,
        'prodotto_form': prodotto_form,
        'prodotti': prodotti_nella_sessione
    })


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
    scontrini = Scontrino.objects.filter(utente=request.user)
    return render(request, 'scontrini/lista_scontrini.html', {'scontrini': scontrini})


@login_required
def dettagli_scontrino(request, scontrino_id):
    scontrino = get_object_or_404(
        Scontrino, id=scontrino_id, utente=request.user)
    prodotti = scontrino.prodotti.all()
    return render(request, 'scontrini/dettagli_scontrino.html', {'scontrino': scontrino, 'prodotti': prodotti})


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'scontrini/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user

        # Filtra in base al parametro di filtro (ad es. 'all time', '1 mese', '6 mesi', ecc.)
        filtro = self.request.GET.get('filtro', 'all_time')
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

    labels = [spesa['giorno'] for spesa in spese]
    data = [spesa['spesa_giornaliera'] for spesa in spese]

    return JsonResponse({'labels': labels, 'data': data})
