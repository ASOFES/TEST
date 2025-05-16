# Configuration de WhatsApp pour les notifications

Ce guide vous explique comment configurer les notifications WhatsApp pour votre application de gestion de flotte via Twilio.

## 1. Prérequis

Avant de commencer, assurez-vous d'avoir:
- Un compte Twilio actif
- Le sandbox WhatsApp de Twilio activé
- Votre numéro de téléphone Twilio WhatsApp (+14155238886)

## 2. Configuration du Sandbox WhatsApp Twilio

WhatsApp nécessite un processus d'approbation officiel pour l'utilisation d'un numéro d'entreprise. Cependant, Twilio offre un "sandbox" pour tester l'intégration WhatsApp:

1. Connectez-vous à votre [compte Twilio](https://www.twilio.com/console)
2. Allez dans la section "Messaging" puis "Try it out" > "Send a WhatsApp message"
3. Suivez les instructions pour activer le sandbox
4. Notez le **mot-code** pour rejoindre votre sandbox (par exemple "join remarkable")

## 3. Inscription des utilisateurs au service WhatsApp

Pour qu'un utilisateur puisse recevoir des messages WhatsApp via votre application:

1. L'utilisateur doit enregistrer le numéro WhatsApp Twilio (+14155238886) dans ses contacts
2. L'utilisateur doit envoyer exactement le message "join [mot-code]" à ce numéro
   - Par exemple: "join remarkable" (remplacez "remarkable" par votre mot-code)
3. Une fois cette opération effectuée, l'utilisateur est inscrit et peut recevoir des messages pendant 72 heures
4. Après 72 heures sans interaction, l'utilisateur devra de nouveau envoyer un message à votre numéro pour réactiver le service

## 4. Test de l'envoi de messages WhatsApp

Pour tester si tout fonctionne correctement:

1. Exécutez le script de test: `python debug_whatsapp.py`
2. Ce script enverra un message de test au numéro spécifié
3. Vérifiez que vous recevez bien le message sur votre téléphone

## 5. Limites du sandbox WhatsApp

Le sandbox WhatsApp de Twilio a quelques limitations:
- Les utilisateurs doivent s'inscrire manuellement
- La session expire après 72 heures d'inactivité
- Vous ne pouvez envoyer des messages qu'aux numéros qui ont rejoint votre sandbox
- Les modèles de messages sont limités

## 6. Passage à une solution WhatsApp Business (pour la production)

Pour une utilisation en production, vous devrez:
1. Demander l'approbation de WhatsApp pour utiliser l'API Business
2. Créer et faire approuver des modèles de messages
3. Configurer un numéro WhatsApp Business via Twilio

## 7. Dépannage

Si les messages ne sont pas reçus:
- Vérifiez que l'utilisateur a bien envoyé le message "join [mot-code]"
- Vérifiez que la session n'a pas expiré (72 heures)
- Vérifiez que le numéro de téléphone est au format E.164 (+243XXXXXXXXX)
- Consultez les journaux de l'application pour voir les erreurs éventuelles 