from django.urls import path
from .views import RecensioniView


urlpatterns = [
    path('', RecensioniView.as_view(), name='recensioni'),
]
