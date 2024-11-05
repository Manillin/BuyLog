from django.urls import path
from .views import RecensioniListView, NegozioRecensioniView, AggiungiRecensioneView, toggle_like

app_name = 'recensioni'

urlpatterns = [
    path('', RecensioniListView.as_view(), name='lista_recensioni'),
    path('negozio/<int:pk>/', NegozioRecensioniView.as_view(),
         name='recensioni_negozio'),
    path('aggiungi/<int:negozio_id>/',
         AggiungiRecensioneView.as_view(), name='aggiungi_recensione'),
    path('like/<int:review_id>/', toggle_like, name='toggle_like'),
]
