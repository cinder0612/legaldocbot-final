# 🔐 GUIDE CONFIGURATION DES SECRETS STREAMLIT CLOUD

## 📋 Secrets requis pour LegalDocBot

Vous devez configurer ces secrets dans votre application Streamlit Cloud :

### 1. **Clé API Grok-4 (OBLIGATOIRE)**
```toml
XAI_API_KEY = "votre_clé_api_grok_ici"
```

### 2. **Clés API Google (OPTIONNELLES)**
```toml
GOOGLE_API_KEY = "votre_clé_api_google_ici"
ONIAM_CSE_ID = "votre_cse_id_oniam_ici"
```

### 3. **Token Hugging Face (OPTIONNEL)**
```toml
HUGGINGFACE_TOKEN = "votre_token_huggingface_ici"
```

## 🚀 Comment configurer les secrets

### **Étape 1 : Aller sur Streamlit Cloud**
1. Connectez-vous à [share.streamlit.io](https://share.streamlit.io)
2. Sélectionnez votre application `legaldocbot-clean`

### **Étape 2 : Configurer les secrets**
1. Cliquez sur **"Settings"** (⚙️)
2. Allez dans l'onglet **"Secrets"**
3. Collez cette configuration :

```toml
XAI_API_KEY = "votre_clé_api_grok_ici"
GOOGLE_API_KEY = "votre_clé_api_google_ici"
ONIAM_CSE_ID = "votre_cse_id_oniam_ici"
HUGGINGFACE_TOKEN = "votre_token_huggingface_ici"
```

### **Étape 3 : Remplacer les valeurs**
- Remplacez `votre_clé_api_grok_ici` par votre vraie clé API Grok-4
- Remplacez `votre_clé_api_google_ici` par votre vraie clé API Google
- Remplacez `votre_cse_id_oniam_ici` par votre vrai CSE ID
- Remplacez `votre_token_huggingface_ici` par votre vrai token Hugging Face

### **Étape 4 : Sauvegarder**
1. Cliquez sur **"Save"**
2. Votre application se redéploiera automatiquement

## 🔑 Où obtenir les clés API

### **Clé API Grok-4 (X.AI)**
1. Allez sur [console.x.ai](https://console.x.ai)
2. Créez un compte ou connectez-vous
3. Allez dans "API Keys"
4. Créez une nouvelle clé API
5. Copiez la clé

### **Clé API Google**
1. Allez sur [Google Cloud Console](https://console.cloud.google.com)
2. Créez un projet ou sélectionnez un projet existant
3. Activez l'API Custom Search
4. Créez des identifiants API
5. Copiez la clé API

### **CSE ID ONIAM**
1. Allez sur [Google Programmable Search Engine](https://programmablesearchengine.google.com)
2. Créez un nouveau moteur de recherche
3. Configurez-le pour rechercher sur les sites ONIAM
4. Copiez l'ID du moteur de recherche

### **Token Hugging Face**
1. Allez sur [huggingface.co](https://huggingface.co)
2. Connectez-vous à votre compte
3. Allez dans "Settings" > "Access Tokens"
4. Créez un nouveau token
5. Copiez le token

## ⚠️ Important

- **Ne partagez JAMAIS** vos clés API publiquement
- **La clé Grok-4 est OBLIGATOIRE** pour que l'application fonctionne
- **Les autres clés sont optionnelles** mais améliorent les fonctionnalités
- **Redéployez** votre application après avoir configuré les secrets

## 🎯 Test

Une fois les secrets configurés :
1. Votre application devrait se redéploier automatiquement
2. Le bouton "Analyser" devrait fonctionner
3. Vous devriez voir "✅ Client Grok-4 configuré" dans les logs 