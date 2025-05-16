from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_list, name='list'),
    path('settings/', views.notification_settings, name='settings'),
    path('test/', views.send_test_notification, name='test'),
    path('status/', views.notification_status, name='status'),
] 