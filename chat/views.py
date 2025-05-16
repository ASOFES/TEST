from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Max, Count
from django.utils import timezone
from django.contrib import messages

from core.models import Utilisateur
from .models import Message, Conversation
from .forms import MessageForm, ContactForm

@login_required
def conversations_list(request):
    """Vue pour afficher la liste des conversations de l'utilisateur"""
    # Récupérer toutes les conversations de l'utilisateur
    conversations = Conversation.objects.filter(participants=request.user)
    
    # Pour chaque conversation, récupérer le dernier message et l'autre participant
    conversations_data = []
    for conversation in conversations:
        # Récupérer l'autre participant
        other_user = conversation.participants.exclude(id=request.user.id).first()
        
        # Récupérer le dernier message
        messages = conversation.get_messages()
        last_message = messages.last() if messages.exists() else None
        
        # Récupérer le nombre de messages non lus
        unread_count = conversation.get_unread_count(request.user)
        
        # Ajouter les données à la liste
        conversations_data.append({
            'conversation': conversation,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    # Formulaire pour démarrer une nouvelle conversation
    form = ContactForm(user=request.user)
    
    if request.method == 'POST':
        form = ContactForm(request.POST, user=request.user)
        if form.is_valid():
            contact = form.cleaned_data['contact']
            # Récupérer ou créer la conversation
            conversation = Conversation.get_or_create_conversation(request.user, contact)
            return redirect('chat:conversation_detail', conversation_id=conversation.id)
    
    context = {
        'conversations': conversations_data,
        'form': form,
    }
    
    return render(request, 'chat/conversations_list.html', context)

@login_required
def conversation_detail(request, conversation_id):
    """Vue pour afficher les détails d'une conversation et envoyer des messages"""
    # Récupérer la conversation
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Vérifier que l'utilisateur fait partie de la conversation
    if request.user not in conversation.participants.all():
        messages.error(request, "Vous n'avez pas accès à cette conversation.")
        return redirect('chat:conversations_list')
    
    # Récupérer l'autre participant
    other_user = conversation.participants.exclude(id=request.user.id).first()
    
    # Récupérer tous les messages de la conversation
    messages_list = conversation.get_messages()
    
    # Marquer les messages non lus comme lus
    for msg in messages_list:
        if msg.destinataire == request.user and not msg.lu:
            msg.marquer_comme_lu()
    
    # Formulaire pour envoyer un message
    form = MessageForm()
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.expediteur = request.user
            message.destinataire = other_user
            message.save()
            
            # Mettre à jour la date du dernier message
            conversation.dernier_message = timezone.now()
            conversation.save()
            
            return redirect('chat:conversation_detail', conversation_id=conversation.id)
    
    context = {
        'conversation': conversation,
        'other_user': other_user,
        'messages': messages_list,
        'form': form,
    }
    
    return render(request, 'chat/conversation_detail.html', context)

@login_required
def new_conversation(request, user_id):
    """Vue pour démarrer une nouvelle conversation avec un utilisateur spécifique"""
    # Récupérer l'utilisateur avec qui démarrer la conversation
    other_user = get_object_or_404(Utilisateur, id=user_id)
    
    # Récupérer ou créer la conversation
    conversation = Conversation.get_or_create_conversation(request.user, other_user)
    
    return redirect('chat:conversation_detail', conversation_id=conversation.id)

@login_required
def unread_count(request):
    """Vue pour récupérer le nombre de messages non lus (pour l'API)"""
    # Récupérer toutes les conversations de l'utilisateur
    conversations = Conversation.objects.filter(participants=request.user)
    
    # Calculer le nombre total de messages non lus
    total_unread = 0
    for conversation in conversations:
        total_unread += conversation.get_unread_count(request.user)
    
    return JsonResponse({'count': total_unread}) 