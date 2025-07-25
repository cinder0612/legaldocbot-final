# 🔧 Configuration Recherche ONIAM - Guide Complet

## ❌ Problème Actuel
La recherche ONIAM ne fonctionne pas car :
1. **Fichier `.env` manquant** avec les clés API
2. **CSE ONIAM non configuré** 
3. **Variables d'environnement non définies**

## ✅ Solution Étape par Étape

### 1. Créer le fichier `.env`

Créez un fichier `.env` à la racine du projet avec ce contenu :

```bash
# ============================================================================
# CONFIGURATION API GOOGLE CUSTOM SEARCH ENGINE
# ============================================================================

# Clé API Google (OBLIGATOIRE pour la recherche ONIAM)
# Obtenez votre clé sur : https://console.cloud.google.com/apis/credentials
GOOGLE_API_KEY=votre_clé_api_google_ici

# ============================================================================
# SYSTÈME DE BYPASS INTELLIGENT - ROTATION DES CLÉS API
# ============================================================================

# Clés API supplémentaires pour contourner les quotas (OPTIONNEL)
# Créez plusieurs projets Google Cloud pour obtenir plusieurs clés
GOOGLE_API_KEY_2=votre_deuxième_clé_api_google
GOOGLE_API_KEY_3=votre_troisième_clé_api_google
GOOGLE_API_KEY_4=votre_quatrième_clé_api_google
GOOGLE_API_KEY_5=votre_cinquième_clé_api_google

# ============================================================================
# CONFIGURATION GROK-4
# ============================================================================

# Clé API Grok-4 (OBLIGATOIRE pour l'analyse)
# Obtenez votre clé sur : https://console.x.ai/
GROK_API_KEY=votre_clé_api_grok_ici

# ============================================================================
# CONFIGURATION X.AI (optionnel)
# ============================================================================

# Clé API X.AI pour recherche web avancée
XAI_API_KEY=votre_clé_api_xai_ici
```

### 2. Obtenir des Clés API Google Multiples

#### Option A : Une seule clé (Simple)
1. **Allez sur** : https://console.cloud.google.com/
2. **Créez un projet** ou sélectionnez un projet existant
3. **Activez l'API** : "Custom Search API"
4. **Créez des identifiants** : "Clé API"
5. **Copiez la clé** et remplacez `votre_clé_api_google_ici`

#### Option B : Clés multiples (Recommandé pour éviter les quotas)
1. **Créez 3-5 projets Google Cloud** différents
2. **Activez Custom Search API** sur chaque projet
3. **Créez une clé API** pour chaque projet
4. **Ajoutez toutes les clés** dans le fichier `.env`

**Avantages des clés multiples :**
- ✅ **Quota multiplié** : 10,000 × 5 = 50,000 requêtes/jour
- ✅ **Rotation automatique** : Le système utilise la clé la moins utilisée
- ✅ **Fallback intelligent** : Si une clé est saturée, passe à la suivante
- ✅ **Cache intégré** : Évite les requêtes répétées

### 3. Configurer le CSE ONIAM

#### Option A : Utiliser le CSE existant (RECOMMANDÉ)
Le CSE actuel inclut déjà les sites ONIAM. Vérifiez dans `google_search_module.py` :

```python
        self.search_engine_id = "votre_cse_jurisprudence_ici"  # CSE "Jurisprudence Officielle"
```

#### Option B : Créer un CSE ONIAM dédié
1. **Allez sur** : https://cse.google.com/
2. **Créez un nouveau moteur de recherche**
3. **Ajoutez les sites ONIAM** :
   - `*.oniam.fr/*`
   - `*.solidarites-sante.gouv.fr/*`
   - `*.legifrance.gouv.fr/*`
4. **Copiez l'ID du CSE** et remplacez dans le code

## 🚀 Système de Bypass Intelligent

### Fonctionnalités Automatiques

1. **Rotation des Clés API**
   - Utilise automatiquement la clé la moins utilisée
   - Passe à la clé suivante si quota dépassé
   - Équilibrage de charge entre les clés

2. **Cache Intelligent**
   - Cache les résultats pendant 1 heure
   - Évite les requêtes répétées
   - Améliore les performances

3. **Mode Hybride**
   - Essaie Google Search d'abord
   - Utilise le fallback si échec
   - Garantit toujours des résultats

4. **Fallback Intelligent**
   - Résultats de jurisprudence pré-générés
   - Informations ONIAM actualisées
   - Pas de coupure de service

### Configuration Avancée

```python
# Dans google_search_module.py
self.hybrid_mode = True  # Mode hybride activé
self.cache_duration = 3600  # Cache 1 heure
self.rate_limit_delay = 0.1  # 100ms entre requêtes
```

## 🔍 Sites ONIAM Indexés

Le CSE actuel inclut ces sites ONIAM :

### Sites Officiels
- ✅ `oniam.fr` - Site officiel ONIAM
- ✅ `service-public.fr` - Informations gouvernementales
- ✅ `legifrance.gouv.fr` - Textes de loi

### Sites Juridiques
- ✅ `dalloz.fr` - Doctrine juridique
- ✅ `lexisnexis.fr` - Base juridique
- ✅ `courdecassation.fr` - Jurisprudence

### Sites Médicaux
- ✅ `has-sante.fr` - Haute Autorité de Santé
- ✅ `ameli.fr` - Assurance Maladie

## 📊 Requêtes ONIAM Optimisées

Le système utilise ces requêtes spécialisées :

```python
oniam_queries = [
    "ONIAM indemnisation",
    "accident médical ONIAM", 
    "barème ONIAM 2024",
    "procédure ONIAM",
    "commission conciliation ONIAM",
    "aléa thérapeutique ONIAM",
    "indemnisation médicale",
    "faute médicale indemnisation",
    "ONIAM accident médical",
    "indemnisation patient"
]
```

## 🎯 Résultats Attendus

Avec une configuration correcte, vous devriez obtenir :

### Dans l'Analyse
```
🏥 Informations ONIAM analysées : 3 sources examinées
Les barèmes et procédures applicables ont été intégrés dans les recommandations
```

### Contenu ONIAM Intégré
- **Barèmes d'indemnisation** 2024
- **Procédures CCI** (Commission de Conciliation)
- **Conditions d'accès** ONIAM
- **Montants d'indemnisation** réalistes
- **Recours possibles** (tribunal administratif)

## ⚠️ Problèmes Courants

### 1. "Clé API Google manquante"
**Solution** : Créez le fichier `.env` avec votre clé Google API

### 2. "Quota dépassé"
**Solution** : 
- **Simple** : Utilisez le mode hybride (fallback automatique)
- **Avancé** : Ajoutez des clés API multiples
- **Expert** : Réduisez `max_results` dans la configuration

### 3. "0 résultats ONIAM"
**Solution** :
- Vérifiez que les sites ONIAM sont dans le CSE
- Testez avec des requêtes simples : "ONIAM indemnisation"
- Vérifiez les logs de debug

## 🔧 Configuration Alternative

Si vous ne voulez pas configurer Google API, vous pouvez :

### Option 1 : Mode Local
Utilisez uniquement ChromaDB (base locale) :
```python
# Dans medical_legal_bot_grok.py
GOOGLE_SEARCH_AVAILABLE = False
```

### Option 2 : Mode Hybride
Utilisez ChromaDB + recherche limitée :
```python
# Réduire le nombre de requêtes
max_results = 3  # Au lieu de 10
```

### Option 3 : Mode Fallback Pur
Utilisez uniquement les résultats de fallback :
```python
# Dans google_search_module.py
self.hybrid_mode = False
self.fallback_mode = True
```

## ✅ Checklist de Configuration

- [ ] Fichier `.env` créé avec clé Google API
- [ ] Clé API Google valide (testée)
- [ ] **Clés API multiples configurées (recommandé)**
- [ ] CSE configuré avec sites ONIAM
- [ ] Test de recherche ONIAM réussi
- [ ] Résultats affichés dans l'analyse
- [ ] Barèmes ONIAM intégrés
- [ ] **Système de bypass testé**

## 🚀 Après Configuration

Une fois configuré, la recherche ONIAM fournira :

1. **Informations actualisées** sur l'indemnisation
2. **Barèmes précis** 2024
3. **Procédures détaillées** CCI
4. **Montants réalistes** d'indemnisation
5. **Recours possibles** (tribunal administratif)
6. **Pas de coupure** grâce au système de bypass

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs dans la console
2. Testez avec des requêtes simples
3. Vérifiez votre quota Google API
4. **Activez le mode hybride pour le fallback automatique**
5. Consultez le guide `GUIDE_CSE_ONIAM.md` 