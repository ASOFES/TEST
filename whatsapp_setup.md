# Configuration de WhatsApp Business API avec CEQUENS

Ce document explique comment configurer WhatsApp Business API via CEQUENS pour votre application de gestion de flotte.

## Prérequis

1. Un compte CEQUENS actif (https://www.cequens.com/)
2. Un numéro de téléphone WhatsApp Business approuvé par CEQUENS
3. Une clé API CEQUENS valide

## Étapes de configuration

### 1. Créer un compte CEQUENS

- Rendez-vous sur [CEQUENS](https://www.cequens.com/)
- Cliquez sur "Book demo" pour demander une démonstration
- Suivez le processus d'inscription et de création de compte

### 2. Obtenir vos identifiants API

- Connectez-vous à votre tableau de bord CEQUENS
- Accédez à la section API Keys ou Developer
- Notez votre API Key et API Secret

### 3. Configurer votre numéro WhatsApp Business

- Dans votre tableau de bord CEQUENS, accédez à la section WhatsApp Business
- Suivez les étapes pour vérifier et configurer votre numéro WhatsApp Business
- Créez des modèles de messages pour les notifications importantes

### 4. Configuration dans l'application

Exécutez le script de configuration CEQUENS pour mettre à jour les paramètres dans votre application:

```bash
python cequens_setup.py
```

Ou mettez à jour manuellement les variables suivantes dans `gestion_vehicules/settings.py`:

```python
# CEQUENS configuration
CEQUENS_API_KEY = 'votre_api_key'
CEQUENS_API_SECRET = 'votre_api_secret'
CEQUENS_SENDER_ID = 'votre_sender_id'
CEQUENS_WHATSAPP_NUMBER = 'votre_numero_whatsapp'
MESSAGING_PROVIDER = 'CEQUENS'
```

### 5. Tester l'envoi de messages

Pour tester l'envoi de messages WhatsApp:

```bash
python debug_whatsapp.py
```

## Modèles de messages WhatsApp

Pour envoyer des messages WhatsApp via l'API CEQUENS, vous devez d'abord créer et faire approuver des modèles de messages pour chaque type de notification:

1. **Notification de mission**: Pour informer les chauffeurs des nouvelles missions
2. **Rappel de maintenance**: Pour rappeler les entretiens programmés
3. **Alerte de carburant**: Pour signaler les niveaux bas de carburant
4. **Confirmation de réservation**: Pour confirmer les réservations de véhicules

## Support

En cas de problème avec l'intégration CEQUENS:

- Consultez la documentation officielle: [CEQUENS Developer Hub](https://www.cequens.com/knowledgehub)
- Contactez le support CEQUENS: hello@cequens.com
- Vérifiez les journaux d'erreur de l'application 