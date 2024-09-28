from django.shortcuts import render, redirect, HttpResponse
from django.db import models
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from .models import Scontrino, Negozio, ListaProdotti
from .forms import *

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
    if 'prodotti' not in request.session:
        request.session['prodotti'] = []

    if request.method == 'POST' and 'aggiungi_prodotto' in request.POST:
        prodotto_form = ListaProdottiForm(request.POST)
        if prodotto_form.is_valid():
            prodotto_dati = prodotto_form.cleaned_data
            request.session['prodotti'].append(prodotto_dati)
            request.session.modified = True
        return redirect('carica_scontrino')

    elif request.method == 'POST' and 'salva_scontrino' in request.POST:
        scontrino_form = ScontrinoForm(request.POST)
        if scontrino_form.is_valid():
            # otteniamo e puliamo nome negozio
            negozio_nome = scontrino_form.cleaned_data['negozio_nome'].strip()
            negozio_nome_pulito = slugify(
                negozio_nome, allow_unicode=True).replace('-', '').lower()

            # controllo se negozio esiste:
            negozio = Negozio.objects.filter(
                Q(nome__iexact=negozio_nome_pulito) | Q(nome__icontains=negozio_nome_pulito.replace(" ", ""))).first()

            if not negozio:
                negozio = Negozio.objects.create(nome=negozio_nome_pulito)

            # creiamo scontrino
            scontrino = Scontrino.objects.create(
                utente=request.user,
                negozio=negozio,
                data=scontrino_form.cleaned_data['data']
            )

            # Aggiungiamo i prodotti salvati dalla sessione allo scontrino
            for prodotto_dati in request.session['prodotti']:
                prodotto_nome = prodotto_dati['prodotto']
                prodotto_nome_pulito = slugify(
                    prodotto_nome, allow_unicode=True).replace("-", "").lower()

                # Troviamo o creiamo il prodotto
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
            return redirect('scontrinilanding')

    else:
        scontrino_form = ScontrinoForm()
        prodotto_form = ProdottoForm()

    prodotti_nella_sessione = request.session.get('prodotti', [])

    return render(request, 'scontrini/carica_scontrino.html', {
        'scontrino_form': scontrino_form,
        'prodotto_form': prodotto_form,
        'prodotti': prodotti_nella_sessione
    })


def carica_scontrino(request):
    # Inizializziamo la lista dei prodotti se non esiste ancora nella sessione
    if 'prodotti' not in request.session:
        request.session['prodotti'] = []

    # Gestione aggiunta prodotto
    if request.method == 'POST' and 'aggiungi_prodotto' in request.POST:
        prodotto_form = ListaProdottiForm(request.POST)
        if prodotto_form.is_valid():
            prodotto_dati = prodotto_form.cleaned_data

            # Convertiamo quantita e prezzo_unitario in tipi serializzabili
            prodotto_dati['quantita'] = float(prodotto_dati['quantita'])
            prodotto_dati['prezzo_unitario'] = float(
                prodotto_dati['prezzo_unitario'])

            request.session['prodotti'].append(prodotto_dati)
            # Necessario per salvare i cambiamenti nella sessione
            request.session.modified = True

        return redirect('scontrini:carica_scontrino')

    # Gestione salvataggio scontrino
    elif request.method == 'POST' and 'salva_scontrino' in request.POST:
        scontrino_form = ScontrinoForm(request.POST)
        if scontrino_form.is_valid():
            negozio_nome = scontrino_form.cleaned_data['negozio_nome'].strip()
            negozio_nome_pulito = slugify(
                negozio_nome, allow_unicode=True).replace("-", "").lower()

            # Controlliamo se il negozio esiste nel database (case-insensitive e senza spazi)
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

            # Aggiungiamo i prodotti salvati dalla sessione allo scontrino
            for prodotto_dati in request.session['prodotti']:
                prodotto_nome = prodotto_dati['prodotto']
                prodotto_nome_pulito = slugify(
                    prodotto_nome, allow_unicode=True).replace("-", "").lower()

                # Troviamo o creiamo il prodotto
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

            return redirect('scontrini:successo')

    else:
        scontrino_form = ScontrinoForm()
        prodotto_form = ListaProdottiForm()

    prodotti_nella_sessione = request.session.get('prodotti', [])

    return render(request, 'scontrini/carica_scontrino.html', {
        'scontrino_form': scontrino_form,
        'prodotto_form': prodotto_form,
        'prodotti': prodotti_nella_sessione
    })


def successo(request):
    return render(request, 'scontrini/successo.html')
