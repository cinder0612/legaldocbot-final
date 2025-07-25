# 🚀 Guide de Déploiement LegalDocBot sur GitLab

## 📋 Vue d'ensemble

Ce guide vous explique comment déployer LegalDocBot sur GitLab en séparant le code (quelques Mo) des gros fichiers (42 GB) stockés sur Google Drive/Hugging Face.

## 📦 Étape 1 : Préparation du projet

### 1.1 Structure du projet
```
legaldocbot/
├── 📁 Code (quelques Mo) → GitLab
│   ├── *.py
│   ├── requirements.txt
│   ├── .gitignore
│   └── README.md
├── 📁 Ressources obligatoires → Google Drive
│   └── chroma_db/ (base de connaissances avec embeddings)
├── 📁 Ressources optionnelles → Google Drive/Hugging Face
│   ├── knowledge base/ (PDFs source - pour ajout de nouveaux documents)
│   └── models/ (modèles ML - si nécessaire)
└── 📁 Dossiers vides (créés automatiquement)
    ├── data/
    └── models/
```

### 1.2 Fichiers exclus du GitLab (.gitignore)
```bash
# Gros fichiers et modèles
models/
data/
chroma_db/
cache/
knowledge base/

# Fichiers de données
*.pkl
*.bin
*.onnx
*.h5
*.hdf5
*.joblib
*.pickle

# Fichiers temporaires
*.tmp
*.temp
*.log
*.cache

# Environnement Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Fichiers sensibles
.env
.env.local
.env.production
secrets.json

# Fichiers volumineux
*.pdf
*.zip
*.tar.gz
*.rar
*.7z
```

## 📥 Étape 2 : Stockage des gros fichiers

### 2.1 Option A : Google Drive (15 GB gratuit)

1. **Créer un dossier Google Drive**
   - Allez sur [drive.google.com](https://drive.google.com)
   - Créez un dossier "LegalDocBot-Resources"

2. **Uploader les ressources obligatoires**
   ```bash
   # Compresser ChromaDB (OBLIGATOIRE)
   zip -r chroma_db.zip chroma_db/
   ```

3. **Uploader les ressources optionnelles (si nécessaire)**
   ```bash
   # Pour ajouter de nouveaux documents plus tard
   zip -r knowledge_base.zip "knowledge base/"
   
   # Pour des modèles ML spécifiques
   zip -r models.zip models/
   ```

3. **Partager les fichiers**
   - Clic droit sur chaque fichier
   - "Obtenir le lien"
   - "Autoriser tous les utilisateurs avec le lien"
   - Copier l'URL (ex: `https://drive.google.com/file/d/ABC123/view?usp=sharing`)

4. **Convertir l'URL pour gdown**
   - Remplacer `https://drive.google.com/file/d/ABC123/view?usp=sharing`
   - Par `https://drive.google.com/uc?id=ABC123`

### 2.2 Option B : Hugging Face (illimité)

1. **Créer un compte**
   - Allez sur [huggingface.co](https://huggingface.co)
   - Créez un compte gratuit

2. **Créer un dataset**
   - Cliquez sur "New Dataset"
   - Nom: `legalbot-models`
   - Type: Public

3. **Uploader les fichiers**
   - Glissez-déposez vos fichiers
   - Ou utilisez l'API:
   ```bash
   pip install huggingface_hub
   huggingface-cli upload VOTRE_USER/legalbot-models models/
   ```

## ⚙️ Étape 3 : Configuration

### 3.1 Configurer download_manager.py
```python
self.resources = {
    "chroma_db": {
        "url": "https://drive.google.com/uc?id=VOTRE_ID_CHROMA",
        "type": "gdrive",
        "local_path": self.chroma_dir,
        "description": "Base de données ChromaDB avec embeddings"
    },
    "knowledge_base": {
        "url": "https://drive.google.com/uc?id=VOTRE_ID_KNOWLEDGE",
        "type": "gdrive", 
        "local_path": self.knowledge_dir,
        "description": "Base de connaissances juridique"
    },
    "models": {
        "url": "https://huggingface.co/datasets/VOTRE_USER/legalbot-models",
        "type": "huggingface",
        "local_path": self.models_dir,
        "description": "Modèles de machine learning"
    }
}
```

### 3.2 Configurer .env
```bash
# Google Search API
GOOGLE_API_KEY=votre_cle_google_api_ici
ONIAM_CSE_ID=votre_cse_oniam_ici

# X.AI API (Grok-4)
XAI_API_KEY=votre_cle_xai_api_ici

# Kimi API (optionnel)
KIMI_API_KEY=votre_cle_kimi_api_ici
```

## 🚀 Étape 4 : Déploiement sur GitLab

### 4.1 Initialiser Git
```bash
# Initialiser le repository
git init

# Ajouter les fichiers (gros fichiers exclus par .gitignore)
git add .

# Premier commit
git commit -m "Initial commit - Code LegalDocBot"

# Ajouter le remote GitLab
git remote add origin https://gitlab.com/VOTRE_USER/legalbot.git

# Pousser sur GitLab
git push -u origin main
```

### 4.2 Vérifier la taille
```bash
# Vérifier la taille du repository
du -sh .git
# Doit être < 100 Mo

# Lister les fichiers inclus
git ls-files | wc -l
# Doit être < 100 fichiers
```

## 🔄 Étape 5 : Installation automatique

### 5.1 Script de configuration
```bash
# Lancer la configuration
python setup.py
```

### 5.2 Téléchargement automatique
```bash
# Vérifier les ressources
python download_manager.py

# Ou lancer l'app (télécharge automatiquement)
streamlit run medical_legal_bot_grok.py
```

## 📊 Étape 6 : Vérification

### 6.1 Test local
```bash
# Vérifier que tout fonctionne
python test_pleadings_sobre.py
python download_manager.py
```

### 6.2 Test sur GitLab CI/CD (optionnel)
```yaml
# .gitlab-ci.yml
stages:
  - test
  - deploy

test:
  stage: test
  script:
    - python setup.py
    - python test_pleadings_sobre.py
  only:
    - main

deploy:
  stage: deploy
  script:
    - echo "Déploiement sur serveur"
  only:
    - main
```

## ✅ Résultat final

- **📁 Code sur GitLab** : Quelques Mo, versionnable, collaboratif
- **📁 ChromaDB sur Google Drive** : Base de connaissances avec embeddings (obligatoire)
- **📁 PDFs optionnels** : Pour ajout de nouveaux documents (si nécessaire)
- **🔄 Téléchargement automatique** : ChromaDB au premier lancement
- **🚀 Déploiement simplifié** : Une seule commande
- **⚡ Optimisation** : Seulement les ressources nécessaires

## 🔧 Dépannage

### Problème : Erreur de téléchargement
```bash
# Vérifier les URLs
python download_manager.py

# Vérifier les permissions Google Drive
# Le fichier doit être "Autoriser tous les utilisateurs avec le lien"
```

### Problème : Fichiers manquants
```bash
# Forcer le téléchargement
python -c "from download_manager import check_and_download_resources; check_and_download_resources()"
```

### Problème : Taille du repository
```bash
# Vérifier ce qui est inclus
git ls-files | head -20

# Nettoyer si nécessaire
git rm --cached gros_fichier.zip
git commit -m "Remove large file"
```

## 📞 Support

- **Documentation** : Ce fichier
- **Issues** : GitLab Issues
- **Configuration** : `setup.py` et `download_manager.py`

---

**🎯 Objectif atteint : Code léger sur GitLab + Gros fichiers externes + Téléchargement automatique !** 