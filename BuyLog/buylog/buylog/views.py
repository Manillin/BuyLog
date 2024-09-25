from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime


# create your views here:

def home(request):
    ctx = {
        'title': 'Welcome to BuyLog',
        'user': 'User generico '
    }
    template = 'home.html'
    return render(request, template, ctx)


def stats(request):
    print(request.method)
    return HttpResponse('You are not logged in!')


def user(request):
    print(request.method)
    s = 'Welcome back User!'
    return HttpResponse(s)
