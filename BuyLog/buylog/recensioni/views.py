from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
# Create your views here.


class RecensioniView(CreateView):
    # form_class = CustomFormTBD
    template_name = 'recensioni.html'
    success_url = reverse_lazy('scontrinilanding')
