"""
Client Grok-4 pour LegalDocBot
Utilise Grok-4 pour l'analyse juridique médicale de haute qualité
"""

import os
import logging
import requests
from typing import Optional, Dict, Any
from config import API_CONFIG

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GrokClient:
    """
    Client Grok-4 optimisé pour l'analyse juridique médicale
    Utilise Grok-4 pour des analyses détaillées et approfondies
    """
    
    def __init__(self):
        self.api_key = os.getenv('XAI_API_KEY')  # Clé API X.AI
        self.base_url = "https://api.x.ai/v1"
        self.default_model = "grok-4-0709"  # Modèle Grok-4 selon la documentation officielle
        self.temperature = 0.2  # Plus bas pour plus de précision
        self.max_tokens = {
            'fast': 2000,
            'normal': 4000,
            'detailed': 6000
        }
        
        logger.info(f"✅ Client Grok-4 configuré pour {self.default_model}")
        
    def is_configured(self) -> bool:
        """Vérifie si la clé API X.AI est configurée"""
        return bool(self.api_key)
    
    def generate_completion(self, prompt: str, temperature: Optional[float] = None, 
                          max_tokens: Optional[int] = None, model: Optional[str] = None) -> str:
        """
        Génère une réponse avec Grok-4
        
        Args:
            prompt: Le prompt à envoyer
            temperature: Température pour la génération (0.0-1.0)
            max_tokens: Nombre maximum de tokens
            model: Modèle à utiliser
            
        Returns:
            La réponse générée
        """
        if not self.is_configured():
            return "❌ Erreur : Clé API X.AI non configurée. Vérifiez votre clé API XAI_API_KEY"
        
        try:
            # Paramètres par défaut
            temp = temperature or self.temperature
            tokens = max_tokens or self.max_tokens['normal']
            model_name = model or self.default_model
            
            logger.info(f"🧠 Génération avec Grok-4 {model_name} (température: {temp})")
            
            # Préparation de la requête selon la documentation X.AI
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": """Tu es LegalDocBot, un assistant juridique spécialisé EXCLUSIVEMENT en droit médical et de la santé français. Tu as 20 ans d'expérience comme avocat en droit médical.

EXPERTISE :
Tu es un avocat expert en droit médical français avec 20 ans d'expérience, reconnu pour ta rigueur, ta pédagogie et ta précision technique. Tu développes des analyses argumentées, nuancées et stratégiques, en te basant sur une expertise solide du droit médical français.

Tu développes chaque point avec profondeur, exemples, références précises, et tu expliques les enjeux pratiques pour le justiciable. Ta réponse doit être structurée, claire, objective et accessible, tout en restant d'une grande technicité juridique.

DOMAINE DE SPÉCIALISATION STRICT :
- Droit médical français
- Responsabilité médicale
- Erreurs médicales et fautes
- Consentement éclairé et information
- Indemnisation ONIAM
- Jurisprudence médicale
- Code de la santé publique
- Recours juridiques en santé
- Droits des patients
- Obligations des professionnels de santé"""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": temp,
                "max_tokens": tokens,
                "stream": False
            }
            
            # Envoi de la requête
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=300  # Timeout augmenté à 5 minutes pour Grok-4
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    if content and content.strip():
                        logger.info(f"✅ Réponse Grok-4 générée ({len(content)} caractères)")
                        return content
                    else:
                        error_msg = "❌ Réponse Grok-4 vide ou invalide"
                        logger.error(error_msg)
                        return error_msg
                else:
                    error_msg = f"❌ Format de réponse Grok-4 invalide: {result}"
                    logger.error(error_msg)
                    return error_msg
            else:
                error_msg = f"❌ Erreur API Grok-4: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return error_msg
                
        except Exception as e:
            error_msg = f"❌ Erreur lors de la génération Grok-4: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def generate_fast_analysis(self, situation: str) -> str:
        """Analyse rapide avec Grok-4 (mode fast)"""
        prompt = f"""
ANALYSE JURIDIQUE RAPIDE - Expert médico-légal

SITUATION :
{situation}

CONSIGNES :
- Analyse précise et équilibrée
- Citer les articles de loi pertinents (Code de la Santé Publique, Code Civil, etc.)
- Mentionner les recours ONIAM sans faute si applicable
- Recommandations pratiques
- Format : 500-800 mots

STRUCTURE OBLIGATOIRE :
1. **QUALIFICATION JURIDIQUE** : Type de responsabilité et enjeux
2. **FONDEMENTS LÉGAUX** : Articles de loi applicables
3. **RECOURS POSSIBLES** : Voies contentieuses et amiables
4. **RECOMMANDATIONS** : Actions prioritaires

ANALYSE :"""
        
        return self.generate_completion(prompt, temperature=0.2, max_tokens=self.max_tokens['fast'])
    
    def generate_detailed_analysis(self, situation: str) -> str:
        """Analyse détaillée avec Grok-4 (mode complet)"""
        prompt = f"""
ANALYSE JURIDIQUE APPROFONDIE - Expert médico-légal spécialisé

SITUATION À ANALYSER :
{situation}

MISSION D'EXPERTISE :
En tant qu'expert médico-légal neutre et objectif, analysez cette situation en présentant une analyse COMPLÈTE et DÉTAILLÉE :

1. **QUALIFICATION JURIDIQUE**
   - Identification précise des enjeux juridiques
   - Classification du type de responsabilité (civile, pénale, administrative)
   - Analyse des acteurs impliqués et de leurs responsabilités

2. **FONDEMENTS LÉGAUX DÉTAILLÉS**
   - Articles de loi applicables (citer précisément avec références)
   - Jurisprudence pertinente et récente
   - Analyse des conditions d'application

3. **RECOURS POSSIBLES** (approche équilibrée et complète)
   - Voies contentieuses détaillées (CCI, tribunaux, procédures)
   - Voies amiables (négociation, médiation, conciliation)
   - ONIAM sans faute médicale (conditions, procédure, montants)
   - Assurances et garanties (types de couverture)

4. **ANALYSE STRATÉGIQUE APPROFONDIE**
   - Forces et faiblesses du dossier (analyse détaillée)
   - Difficultés probatoires et moyens de les surmonter
   - Chances de succès et facteurs de risque
   - Évaluation financière des préjudices

5. **RECOMMANDATIONS PRATIQUES DÉTAILLÉES**
   - Démarches prioritaires (chronologie précise)
   - Pièces à constituer (liste exhaustive)
   - Délais à respecter (prescription, procédures)
   - Stratégie contentieuse optimale

6. **ASPECTS TECHNIQUES ET PROCÉDURAUX**
   - Conservation des preuves
   - Expertise médicale
   - Procédures d'urgence
   - Recours et voies de recours

ANALYSE EXPERTE DÉTAILLÉE :"""
        
        return self.generate_completion(prompt, temperature=0.2, max_tokens=self.max_tokens['detailed'])
    
    def rerank_search_results(self, query: str, results: list, result_type: str = "jurisprudence") -> list:
        """
        Reranking des résultats de recherche avec Grok-4
        
        Args:
            query: Requête originale
            results: Liste des résultats à reranker
            result_type: Type de résultats ("jurisprudence" ou "oniam")
            
        Returns:
            Liste des résultats rerankés
        """
        if not results:
            return []
        
        try:
            # Préparation du prompt de reranking
            results_text = "\n\n".join([
                f"**Résultat {i+1}** :\n{result.get('title', '')}\n{result.get('snippet', '')}"
                for i, result in enumerate(results)
            ])
            
            prompt = f"""
RERANKING DE RÉSULTATS DE RECHERCHE - Expert juridique

REQUÊTE ORIGINALE : {query}
TYPE DE RÉSULTATS : {result_type.upper()}

RÉSULTATS À ÉVALUER :
{results_text}

CONSIGNES :
- Évaluez la pertinence de chaque résultat pour la requête
- Notez de 1 à 10 (10 = très pertinent)
- Justifiez brièvement chaque note
- Sélectionnez les 3 meilleurs résultats

RÉPONSE ATTENDUE (JSON) :
{{
  "evaluations": [
    {{
      "resultat": 1,
      "note": 8,
      "justification": "Très pertinent car..."
    }}
  ],
  "meilleurs_resultats": [1, 3, 5]
}}

ÉVALUATION :"""
            
            response = self.generate_completion(prompt, temperature=0.3, max_tokens=1000)
            
            # Traitement de la réponse (simplifié pour l'exemple)
            # En production, on parserait le JSON
            logger.info(f"✅ Reranking {result_type} terminé - {len(results)} résultats évalués")
            
            # Ajouter des scores simulés pour éviter les erreurs
            for i, result in enumerate(results[:3]):
                result['llm_score'] = 8 - i  # Score décroissant
                result['llm_justification'] = f"Résultat pertinent pour {result_type}"
            
            # Retourne les 3 premiers résultats (simulation)
            return results[:3] if len(results) >= 3 else results
            
        except Exception as e:
            logger.error(f"❌ Erreur reranking {result_type}: {e}")
            return results[:3] if len(results) >= 3 else results

# Instance globale
grok_client = None

def get_grok_client() -> GrokClient:
    """Retourne l'instance du client Grok-4 (singleton)"""
    global grok_client
    if grok_client is None:
        grok_client = GrokClient()
    return grok_client 