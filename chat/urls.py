from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.conversations_list, name='conversations_list'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('nouvelle-conversation/<int:user_id>/', views.new_conversation, name='new_conversation'),
    path('non-lus/', views.unread_count, name='unread_count'),
] 