from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
from scontrini.models import Scontrino

# create your views here:


def home(request):
    if request.user.is_authenticated:
        return redirect('scontrini:dashboard')
    else:
        return render(request, 'landing_page.html')


class UserCreateView(CreateView):
    form_class = CreaUtenteCliente
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

# DetailView ha bisogno di sapere l'oggetto da visualizzare (dal DB), per questo
# si passa pk o slug solitamente.
# in questo caso sovrascriviamo il metodo get_object in quanto abbiamo l'utenet autenticato!


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'user_detail.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserUpdateForm(instance=self.request.user)
        context['profile_form'] = ProfileForm(
            instance=self.request.user.profile)
        return context

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
        else:
            for error in user_form.errors.values():
                messages.error(request, error)
            for error in profile_form.errors.values():
                messages.error(request, error)

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })


class DemoHomeView(TemplateView):
    template_name = 'demo_home.html'
