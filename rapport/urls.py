from django.urls import path
from . import views

app_name = 'rapport'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('vehicules/', views.rapport_vehicules, name='rapport_vehicules'),
    path('missions/', views.rapport_missions, name='rapport_missions'),
    path('entretiens/', views.rapport_entretiens, name='rapport_entretiens'),
    path('carburant/', views.rapport_carburant, name='rapport_carburant'),
    path('generer/<str:type_rapport>/', views.generer_rapport, name='generer_rapport'),
]
