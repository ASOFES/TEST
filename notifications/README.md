# Configuration des Notifications par SMS et WhatsApp

Ce document explique comment configurer les notifications par SMS et WhatsApp pour l'application de gestion de flotte de véhicules.

## Prérequis

Pour activer les notifications par SMS et WhatsApp, vous devez avoir un compte Twilio. Si vous n'en avez pas, vous pouvez en créer un sur [Twilio](https://www.twilio.com/).

## Configuration

### 1. Obtenir les identifiants Twilio

Après avoir créé votre compte Twilio, vous devez récupérer les informations suivantes :
- Account SID
- Auth Token
- Numéro de téléphone Twilio (pour les SMS)
- Numéro de téléphone WhatsApp Twilio (pour WhatsApp)

Ces informations sont disponibles dans votre tableau de bord Twilio.

### 2. Configuration des variables d'environnement

Vous devez configurer les variables d'environnement suivantes :

```bash
# Variables Twilio
export TWILIO_ACCOUNT_SID='votre_account_sid'
export TWILIO_AUTH_TOKEN='votre_auth_token'
export TWILIO_PHONE_NUMBER='votre_numero_twilio'  # Format E.164, ex: +12345678901
export TWILIO_WHATSAPP_NUMBER='votre_numero_whatsapp_twilio'  # Format E.164, ex: +12345678901
```

Pour Windows, utilisez la commande `set` au lieu de `export` :

```cmd
set TWILIO_ACCOUNT_SID=votre_account_sid
set TWILIO_AUTH_TOKEN=votre_auth_token
set TWILIO_PHONE_NUMBER=votre_numero_twilio
set TWILIO_WHATSAPP_NUMBER=votre_numero_whatsapp_twilio
```

### 3. Configuration dans le fichier settings.py

Les variables sont déjà configurées dans le fichier `settings.py` pour récupérer les valeurs des variables d'environnement :

```python
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', '')
```

### 4. Format des numéros de téléphone

Pour que les notifications fonctionnent correctement, assurez-vous que les numéros de téléphone des utilisateurs sont stockés au format E.164 (par exemple, +243995178105).

### 5. Sandbox WhatsApp

Pour les notifications WhatsApp, vous devrez d'abord configurer le sandbox WhatsApp de Twilio. Les utilisateurs devront envoyer un message au numéro WhatsApp de Twilio avec un code spécifique pour s'inscrire au service.

Consultez la documentation de Twilio pour plus d'informations : [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp/api)

## Fonctionnalités implémentées

Les notifications par SMS et WhatsApp sont envoyées dans les cas suivants :

1. **Création d'une demande de course** :
   - Les dispatchers reçoivent une notification

2. **Validation/Refus d'une demande** :
   - Le demandeur reçoit une notification
   - Le chauffeur assigné reçoit une notification (en cas de validation)

3. **Démarrage d'une course** :
   - Le demandeur reçoit une notification

4. **Fin d'une course** :
   - Le demandeur reçoit une notification

## Test des notifications

Pour tester les notifications sans utiliser un compte Twilio réel, vous pouvez utiliser le backend de console en modifiant temporairement les fonctions `send_sms` et `send_whatsapp` dans `notifications/utils.py` pour qu'elles affichent simplement les messages dans la console.

## Dépannage

Si les notifications ne sont pas envoyées :

1. Vérifiez que les variables d'environnement sont correctement configurées
2. Vérifiez que les numéros de téléphone sont au format E.164
3. Vérifiez le solde de votre compte Twilio
4. Consultez les logs de l'application pour les erreurs liées à Twilio 