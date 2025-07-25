 
# 🚀 Déploiement LegalDocBot sur Streamlit Cloud

## 📋 Prérequis

### 1. Compte Streamlit Cloud
- Créez un compte sur [share.streamlit.io](https://share.streamlit.io)
- Connectez votre compte GitHub

### 2. Variables d'Environnement
Configurez ces variables dans Streamlit Cloud :
```bash
GOOGLE_API_KEY=votre_cle_google_api
XAI_API_KEY=votre_cle_xai_api
ONIAM_CSE_ID=votre_cse_oniam
```

## 🔧 Configuration

### 1. Fichier Principal
- **Point d'entrée** : `streamlit_app.py`
- **Configuration** : `.streamlit/config.toml`

### 2. Dépendances
- **Requirements** : `requirements.txt` (déjà configuré)
- **Python** : Version 3.9+ (automatique)

### 3. Ressources Externes
- **ChromaDB** : Téléchargement automatique depuis Google Drive
- **Documents** : Ajout optionnel via interface

## 🚀 Déploiement

### Étape 1 : Connecter GitHub
1. Allez sur [share.streamlit.io](https://share.streamlit.io)
2. Cliquez sur "New app"
3. Sélectionnez votre repository GitHub
4. Branche : `main`

### Étape 2 : Configuration
```
Repository: cinder0612/-legaldocbot
Branch: main
Main file path: streamlit_app.py
```

### Étape 3 : Variables d'Environnement
Dans "Advanced settings" :
```
GOOGLE_API_KEY = votre_cle_google_api
XAI_API_KEY = votre_cle_xai_api
ONIAM_CSE_ID = votre_cse_oniam
```

### Étape 4 : Déployer
- Cliquez sur "Deploy!"
- Attendez 2-3 minutes
- Votre bot sera en ligne !

## 🌐 URL de l'Application
```
https://legaldocbot.streamlit.app
```

## 🔧 Dépannage

### Problème : Erreur de téléchargement
- Vérifiez les URLs dans `download_manager.py`
- Assurez-vous que les fichiers Google Drive sont publics

### Problème : Variables d'environnement
- Vérifiez que toutes les clés API sont configurées
- Redéployez après modification des variables

### Problème : Timeout
- Le premier lancement peut prendre 5-10 minutes
- ChromaDB se télécharge automatiquement

## 📊 Monitoring
- **Logs** : Disponibles dans l'interface Streamlit Cloud
- **Métriques** : Utilisation et performance
- **Mises à jour** : Automatiques depuis GitLab

## 🔄 Mise à Jour
```bash
# Modifiez votre code localement
git add .
git commit -m "Nouvelle fonctionnalité"
git push origin master

# Streamlit Cloud se met à jour automatiquement
```

---

**✅ Votre LegalDocBot sera accessible 24/7 sur le web !** 🌐 