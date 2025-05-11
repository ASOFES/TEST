from django.urls import path
from . import views

app_name = 'securite'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('nouvelle-checklist/', views.nouvelle_checklist, name='nouvelle_checklist'),
    path('checklist/<int:checklist_id>/', views.detail_checklist, name='detail_checklist'),
    path('checklist/<int:checklist_id>/pdf/', views.pdf_checklist, name='pdf_checklist'),
]
