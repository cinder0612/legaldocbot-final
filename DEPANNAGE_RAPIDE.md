# 🚨 DÉPANNAGE RAPIDE - LegalDocBot

## ❌ Problème : "Rien ne se passe quand je clique sur Analyser"

### 🔍 Diagnostic rapide

1. **Vérifiez les logs** dans votre terminal :
   - Cherchez les erreurs `401`, `404`, ou `API key not valid`
   - Regardez si les clés API sont configurées

2. **Testez l'interface simple** :
   ```bash
   streamlit run test_simple.py
   ```

### ✅ Solutions par ordre de priorité

#### 1. **Clé API Grok-4 manquante (CRITIQUE)**
- Allez sur [console.x.ai](https://console.x.ai)
- Créez un compte et obtenez une clé API
- Remplacez dans `.streamlit/secrets.toml` :
  ```toml
  XAI_API_KEY = "votre_vraie_clé_grok_ici"
  ```

#### 2. **Clés Google invalides (OPTIONNEL)**
- Allez sur [Google Cloud Console](https://console.cloud.google.com)
- Activez l'API Custom Search
- Créez des identifiants API
- Remplacez dans `.streamlit/secrets.toml` :
  ```toml
  GOOGLE_API_KEY = "votre_vraie_clé_google_ici"
  ONIAM_CSE_ID = "votre_vrai_cse_id_ici"
  ```

#### 3. **Token Hugging Face manquant (OPTIONNEL)**
- Allez sur [huggingface.co](https://huggingface.co/settings/tokens)
- Créez un token d'accès
- Remplacez dans `.streamlit/secrets.toml` :
  ```toml
  HUGGINGFACE_TOKEN = "votre_vrai_token_ici"
  ```

### 🧪 Test de fonctionnement

1. **Test simple** (sans API) :
   ```bash
   streamlit run test_simple.py
   ```

2. **Test complet** (avec API) :
   ```bash
   streamlit run medical_legal_bot_grok.py
   ```

### 🔧 Redémarrage après configuration

1. **Arrêtez** l'application (Ctrl+C)
2. **Modifiez** `.streamlit/secrets.toml` avec vos vraies clés
3. **Relancez** :
   ```bash
   streamlit run medical_legal_bot_grok.py
   ```

### 📊 Messages de succès attendus

Quand tout fonctionne, vous devriez voir :
- ✅ Clé API Grok-4 configurée
- ✅ Clé API Google configurée  
- ✅ CSE ID ONIAM configuré
- ✅ Token Hugging Face configuré

### 🚨 Messages d'erreur courants

- `401 - No or an invalid authentication header` → Clé Grok-4 invalide
- `API key not valid` → Clé Google invalide
- `Repository Not Found` → Token Hugging Face manquant
- `Collection does not exists` → Base ChromaDB manquante (normal)

### 💡 Mode dégradé

Si vous n'avez pas de clés API, l'application peut fonctionner en mode limité :
- Analyse basique sans enrichissement
- Pas de recherche Google
- Pas de base de connaissances ChromaDB

### 📞 Support

Si le problème persiste :
1. Vérifiez que toutes les clés API sont valides
2. Redémarrez complètement l'application
3. Consultez les logs détaillés dans le terminal 