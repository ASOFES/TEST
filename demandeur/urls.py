from django.urls import path
from . import views

app_name = 'demandeur'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('nouvelle-demande/', views.nouvelle_demande, name='nouvelle_demande'),
    path('demande/<int:demande_id>/', views.detail_demande, name='detail_demande'),
    path('demande/<int:demande_id>/modifier/', views.modifier_demande, name='modifier_demande'),
    path('demande/<int:demande_id>/annuler/', views.annuler_demande, name='annuler_demande'),
]
