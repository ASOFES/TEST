from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Notification, NotificationConfig
from .utils import notify_user

# Create your views here.

@login_required
def notifications_list(request):
    """Vue pour afficher la liste des notifications de l'utilisateur"""
    notifications = Notification.objects.filter(destinataire=request.user).order_by('-date_creation')
    
    # Pagination
    paginator = Paginator(notifications, 10)  # 10 notifications par page
    page_number = request.GET.get('page')
    notifications_page = paginator.get_page(page_number)
    
    # Marquer comme lues les notifications non lues
    Notification.objects.filter(destinataire=request.user, statut='sent').update(statut='delivered')
    
    return render(request, 'notifications/notifications_list.html', {
        'notifications': notifications_page
    })

@login_required
def notification_settings(request):
    """Vue pour gérer les paramètres de notification"""
    config, created = NotificationConfig.objects.get_or_create(utilisateur=request.user)
    
    if request.method == 'POST':
        # Mettre à jour les préférences
        config.sms_enabled = request.POST.get('sms_enabled') == 'on'
        config.whatsapp_enabled = request.POST.get('whatsapp_enabled') == 'on'
        config.email_enabled = request.POST.get('email_enabled') == 'on'
        
        config.notif_demande_course = request.POST.get('notif_demande_course') == 'on'
        config.notif_validation_course = request.POST.get('notif_validation_course') == 'on'
        config.notif_expiration_docs = request.POST.get('notif_expiration_docs') == 'on'
        config.notif_entretien = request.POST.get('notif_entretien') == 'on'
        
        config.save()
        messages.success(request, 'Vos préférences de notification ont été mises à jour.')
        return redirect('notifications:settings')
    
    return render(request, 'notifications/notification_settings.html', {
        'config': config
    })

@login_required
def send_test_notification(request):
    """Vue pour envoyer une notification de test"""
    if request.method == 'POST':
        notification_type = request.POST.get('type', 'all')
        
        result = notify_user(
            request.user,
            "Notification de test",
            "Ceci est une notification de test pour vérifier que le système fonctionne correctement.",
            notification_type=notification_type
        )
        
        if notification_type == 'all':
            if result.get('sms', {}).get('success') or result.get('whatsapp', {}).get('success') or result.get('email', {}).get('success'):
                messages.success(request, 'Notification de test envoyée avec succès.')
            else:
                messages.error(request, 'Échec de l\'envoi de la notification de test.')
        else:
            if result.get(notification_type, {}).get('success'):
                messages.success(request, f'Notification {notification_type} de test envoyée avec succès.')
            else:
                messages.error(request, f'Échec de l\'envoi de la notification {notification_type} de test.')
        
        return redirect('notifications:settings')
    
    return redirect('notifications:settings')

@login_required
def notification_status(request):
    """API pour récupérer le nombre de notifications non lues"""
    count = Notification.objects.filter(destinataire=request.user, statut='sent').count()
    return JsonResponse({'count': count})
