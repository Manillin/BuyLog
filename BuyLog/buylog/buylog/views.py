from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *


# create your views here:

def home(request):
    if request.user.is_authenticated:
        return redirect('scontrini')
    else:
        ctx = {'title': 'HOMEPAGE'}
        return render(request=request, template_name='home.html',
                      context=ctx)


def stats(request):
    print(request.method)
    return HttpResponse('You are not logged in!')


def user(request):
    print(request.method)
    s = 'Welcome back User!'
    return HttpResponse(s)


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
