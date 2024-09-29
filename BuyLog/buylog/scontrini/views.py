from django.contrib import messages  # Per gestire i messaggi di avviso
from django.contrib import messages  # Per gestire messaggi di avviso
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.db import models
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Scontrino, Negozio, ListaProdotti
from .forms import *
from django.http import JsonResponse

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

            scontrino = Scontrino.objects.create(
                utente=request.user,
                negozio=negozio,
                data=scontrino_form.cleaned_data['data']
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


def aggiungi_prodotto(request):
    if request.method == 'POST':
        quantita = request.POST.get('quantita')
        prezzo_unitario = request.POST.get('prezzo_unitario')
        nome_prodotto = request.POST.get('nome_prodotto')

        if quantita and prezzo_unitario and nome_prodotto:
            prodotto_dati = {
                'quantita': float(quantita),
                'prezzo_unitario': float(prezzo_unitario),
                'prodotto': nome_prodotto
            }
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
