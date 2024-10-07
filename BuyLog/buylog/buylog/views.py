from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
from scontrini.models import Scontrino
from scontrini.forms import UserUpdateForm, ProfileForm

# create your views here:


def home(request):
    if request.user.is_authenticated:
        return redirect('scontrini')
    else:
        ctx = {'title': 'HOMEPAGE'}
        return render(request=request, template_name='home.html',
                      context=ctx)


class UserCreateView(CreateView):
    form_class = CreaUtenteCliente
    template_name = 'user_create.html'
    success_url = reverse_lazy('login')

# DetailView ha bisogno di sapere l'oggetto da visualizzare (dal DB), per questo
# si passa pk o slug solitamente.
# in questo caso sovrascriviamo il metodo get_object in quanto abbiamo l'utenet autenticato!


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'user_detail.html'

    def get_object(self):
        return self.request.user

    # Aggiungi metodo post per gestire l'invio del form
    def post(self, request, *args, **kwargs):
        user = self.get_object()  # ottieni l'utente
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(
                request, 'Il tuo profilo è stato aggiornato con successo!')
            return redirect('user')

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })


# View per aggiornare le informazioni utente e il profilo

def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(
                request, 'Il tuo profilo è stato aggiornato con successo!')
            return redirect('user')  # Reindirizza alla pagina del profilo
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'user_detail.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

# View per cancellare l'account utente e i suoi dati correlati


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'user_confirm_delete.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        # Cancella scontrini associati
        Scontrino.objects.filter(utente=self.request.user).delete()
        return super().delete(request, *args, **kwargs)
