# 🤖 LegalDocBot - Assistant Juridique Médical

**Bot spécialisé en droit médical français avec citation automatique des articles de loi**

## 🎯 Fonctionnalités Principales

- **Analyse juridique complète** de situations médicales
- **Citation automatique des articles de loi** (CSP, Code civil, Code pénal)
- **Recherche hybride** : Base locale + Web (jurisprudence, ONIAM)
- **Reranking avancé** avec préservation des articles de loi
- **Analyse structurée** : Faits, cadre juridique, jurisprudence, conseils
- **Génération de plaidoiries** avec Grok-4 (style expert-avocat)
- **Déploiement GitHub optimisé** avec ChromaDB externe

## 📁 Structure du Projet

```
legaldocbot/
├── medical_legal_bot_grok.py     # Interface Streamlit principale
├── pleadings_generator.py        # Générateur de plaidoiries Grok-4
├── download_manager.py           # Gestionnaire de téléchargement automatique
├── document_processor.py         # Traitement de nouveaux documents
├── chromadb_search.py           # Recherche ChromaDB
├── google_search_module.py      # Recherche Google + ONIAM
├── grok_client.py               # Client API Grok-4
├── ui_utils.py                  # Utilitaires interface
├── setup.py                     # Configuration automatique
├── requirements.txt             # Dépendances Python
├── .gitignore                   # Exclusion des gros fichiers
└── README_STREAMLIT.md          # Guide de déploiement Streamlit
```

## 🚀 Installation et Utilisation

### 1. Installation Rapide
```bash
# Cloner le repository
git clone https://github.com/cinder0612/-legaldocbot.git
cd -legaldocbot

# Configuration automatique
python setup.py

# Lancer l'application
streamlit run streamlit_app.py
```

### 2. Configuration des API
```bash
# Copier le template
cp .env.template .env

# Remplir vos clés API dans .env
GOOGLE_API_KEY=votre_cle_google_api
XAI_API_KEY=votre_cle_
```

### 3. Utilisation
- **Interface web** : Ouvrir http://localhost:8501
- **Analyse juridique** : Saisir une situation médicale
- **Génération de plaidoiries** : Utiliser le générateur Grok-4
- **Ajout de documents** : `python document_processor.py`

## 📊 Fonctionnalités Avancées

### Citation Automatique des Articles
Le bot cite automatiquement les articles de loi pertinents :
- **Code de la santé publique** : L1111-2, L1111-4, L1142-1, etc.
- **Code civil** : 1240 (responsabilité civile)
- **Code pénal** : 222-19 (blessures involontaires)
- **Jurisprudence** : Arrêts de la Cour de cassation, Conseil d'État

### Générateur de Plaidoiries
- **Style expert-avocat** : Plaidoiries de niveau professionnel
- **Citations précises** : Articles de loi et jurisprudence
- **Calcul ONIAM** : Indemnisation automatique
- **Format JSON** : Structure normalisée pour l'interface

### Déploiement Optimisé
- **Code léger** : Quelques Mo sur GitHub
- **ChromaDB externe** : Base de connaissances sur Google Drive
- **Téléchargement automatique** : Ressources au premier lancement
- **Configuration simple** : Une seule commande

## 🔧 Configuration

### Variables d'Environnement
```bash
# Google Search API
GOOGLE_API_KEY=votre_cle_google_api
ONIAM_CSE_ID=votre_cse_oniam

# X.AI API (Grok-4)
XAI_API_KEY=votre_cle_xai_api

# Kimi API (optionnel)
KIMI_API_KEY=votre_cle_kimi_api
```

### Ressources Externes
- **ChromaDB** : Téléchargement automatique depuis Google Drive
- **Documents PDF** : Ajout optionnel via `document_processor.py`
- **Modèles ML** : Téléchargement depuis Hugging Face si nécessaire

## 🧪 Tests

### Test du Générateur de Plaidoiries
```bash
python test_pleadings_sobre.py
```

### Test du Processeur de Documents
```bash
python document_processor.py
```

### Test du Gestionnaire de Téléchargement
```bash
python download_manager.py
```

## 📈 Performance

- **Temps d'analyse** : 30-60 secondes (mode hybride)
- **Génération plaidoiries** : 15-30 secondes
- **Téléchargement ChromaDB** : 2-5 minutes (première fois)
- **Précision** : Score de pertinence > 0.8
- **Articles cités** : 5-10 articles de loi par analyse

## 🎯 Cas d'Usage

### Erreurs Médicales
- Erreurs chirurgicales (site, latéralité)
- Infections nosocomiales
- Retards de diagnostic
- Complications post-opératoires

### Responsabilité Médicale
- Faute médicale
- Perte de chance
- Défaut d'information
- Consentement éclairé

### Plaidoiries
- Génération automatique de plaidoiries
- Style professionnel expert-avocat
- Citations juridiques précises
- Calcul d'indemnisation ONIAM

## 🔒 Sécurité et Confidentialité

- **Données locales** : Base de connaissances stockée localement
- **Pas de stockage** : Aucune donnée patient n'est conservée
- **Chiffrement** : Communications API sécurisées
- **Conformité** : Respect du RGPD pour les données médicales
- **Clés API** : Configuration locale, jamais sur GitHub

## 📞 Support

Pour toute question ou problème :
1. Vérifiez la configuration des API
2. Consultez les logs d'erreur
3. Testez avec les scripts de test
4. Consultez `README_STREAMLIT.md`

## 📄 Licence

Ce projet est destiné à un usage professionnel en droit médical français.

---

**LegalDocBot** - Assistant juridique spécialisé en droit médical français avec déploiement GitHub optimisé
#   l e g a l d o c b o t -  
 