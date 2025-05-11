from django.urls import path
from . import views

app_name = 'chauffeur'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mission/<int:mission_id>/', views.detail_mission, name='detail_mission'),
    path('mission/<int:mission_id>/demarrer/', views.demarrer_mission, name='demarrer_mission'),
    path('mission/<int:mission_id>/terminer/', views.terminer_mission, name='terminer_mission'),
]
