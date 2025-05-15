# Guide des Notifications

Ce guide explique comment configurer et utiliser les services de notification dans l'application de gestion de flotte.

## Fournisseurs de Services

L'application prend en charge deux fournisseurs de services de messagerie :

1. **Twilio** - Service par défaut pour SMS et WhatsApp
2. **CEQUENS** - Alternative pour les services SMS et WhatsApp en Afrique

## Configuration des Fournisseurs

### Configuration de Twilio

Pour configurer Twilio :

1. Créez un compte sur [Twilio](https://www.twilio.com/)
2. Obtenez vos identifiants (Account SID et Auth Token)
3. Achetez un numéro de téléphone pour les SMS
4. Configurez le sandbox WhatsApp pour les tests

Exécutez le script de configuration :

```bash
python twilio_setup.py
```

### Configuration de CEQUENS

Pour configurer CEQUENS :

1. Créez un compte sur [CEQUENS](https://www.cequens.com/)
2. Obtenez vos identifiants API (API Key et API Secret)
3. Configurez un Sender ID pour les SMS
4. Configurez un numéro WhatsApp Business

Exécutez le script de configuration :

```bash
python cequens_setup.py
```

## Changer le Fournisseur Par Défaut

Pour changer le fournisseur par défaut, utilisez le script `settings_update.py` :

```bash
# Pour définir Twilio comme fournisseur par défaut
python settings_update.py --provider twilio

# Pour définir CEQUENS comme fournisseur par défaut
python settings_update.py --provider cequens

# Pour afficher la configuration actuelle
python settings_update.py --show
```

## Tester les Notifications

### Test Simple avec Twilio

```bash
python test_twilio.py [numéro_de_téléphone]
```

### Test Complet avec Options

```bash
python test_notification.py [options]
```

Options disponibles :
- `--provider`, `-p` : Fournisseur à utiliser (twilio, cequens, both)
- `--type`, `-t` : Type de notification (sms, whatsapp, both)
- `--number`, `-n` : Numéro de téléphone pour le test
- `--user`, `-u` : ID ou email de l'utilisateur à notifier

Exemples :
```bash
# Tester SMS et WhatsApp avec Twilio
python test_notification.py --provider twilio

# Tester uniquement SMS avec CEQUENS
python test_notification.py --provider cequens --type sms

# Tester les notifications pour un utilisateur spécifique
python test_notification.py --user admin@example.com
```

## Limites et Considérations

### Twilio
- Version gratuite limitée à un petit nombre de messages par jour
- Nécessite de s'inscrire au sandbox WhatsApp tous les 72 heures
- Fonctionne mondialement

### CEQUENS
- Meilleure couverture en Afrique et au Moyen-Orient
- Tarifs potentiellement plus avantageux pour l'Afrique
- Nécessite un contrat d'entreprise pour volumes importants

## Dépannage

Si vous rencontrez des problèmes avec les notifications :

1. Vérifiez la configuration avec `python settings_update.py --show`
2. Assurez-vous que les identifiants API sont corrects
3. Pour WhatsApp avec Twilio, vérifiez que le destinataire a rejoint le sandbox
4. Vérifiez les limites quotidiennes de messages
5. Consultez les journaux d'erreur pour plus de détails

## Intégration dans l'Application

Les notifications sont envoyées automatiquement pour les événements suivants :

1. Création d'une nouvelle mission
2. Assignation d'un chauffeur à une mission
3. Début d'une course
4. Fin d'une course
5. Rapports périodiques (kilométrage, consommation, etc.)

Pour envoyer une notification manuellement dans le code :

```python
from notifications.utils import notify_user

# Notifier un utilisateur avec tous les canaux disponibles
notify_user(user, "Titre", "Message")

# Notifier un utilisateur par SMS uniquement
notify_user(user, "Titre", "Message", notification_type="sms")

# Notifier un utilisateur par WhatsApp uniquement
notify_user(user, "Titre", "Message", notification_type="whatsapp")
``` 