from django.urls import path
from . import views

app_name = 'suivi'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('vehicules/', views.suivi_vehicules, name='suivi_vehicules'),
    path('missions/', views.suivi_missions, name='suivi_missions'),
    path('entretiens/', views.suivi_entretiens, name='suivi_entretiens'),
    path('carburant/', views.suivi_carburant, name='suivi_carburant'),
]
