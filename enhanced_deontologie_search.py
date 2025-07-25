"""
Système de Recherche Spécialisé Déontologie Médicale
Améliore la détection des cas de déontologie dans les analyses
"""

import json
import re
from typing import List, Dict, Optional
from pathlib import Path

class DeontologieSearchEngine:
    """
    Moteur de recherche spécialisé pour la déontologie médicale
    """
    
    def __init__(self):
        # Mots-clés déontologie
        self.deontologie_keywords = {
            "secret_medical": [
                "secret médical", "secret professionnel", "confidentialité",
                "discrétion", "révélation", "divulgation", "silence"
            ],
            "consentement": [
                "consentement éclairé", "consentement libre", "information",
                "accord", "refus", "autonomie", "décision"
            ],
            "obligation_information": [
                "obligation d'information", "devoir d'information", "information patient",
                "explication", "compréhension", "risques", "bénéfices"
            ],
            "independance": [
                "indépendance", "liberté", "conflit d'intérêt", "intérêt personnel",
                "corruption", "cadeaux", "avantages"
            ],
            "competence": [
                "compétence", "formation", "qualification", "expertise",
                "limites", "spécialisation", "formation continue"
            ],
            "dignite": [
                "dignité", "respect", "humanité", "éthique",
                "morale", "valeurs", "principe"
            ]
        }
        
        # Articles de déontologie importants
        self.deontologie_articles = [
            "R.4127-1", "R.4127-2", "R.4127-3", "R.4127-4", "R.4127-5",
            "R.4127-6", "R.4127-7", "R.4127-8", "R.4127-9", "R.4127-10",
            "R.4127-11", "R.4127-12", "R.4127-13", "R.4127-14", "R.4127-15",
            "R.4127-16", "R.4127-17", "R.4127-18", "R.4127-19", "R.4127-20"
        ]
    
    def detect_deontologie_issues(self, situation: str) -> Dict:
        """
        Détecte les problèmes de déontologie dans une situation
        
        Args:
            situation: Description de la situation médicale
            
        Returns:
            Dictionnaire avec les problèmes détectés
        """
        situation_lower = situation.lower()
        issues = {}
        
        for category, keywords in self.deontologie_keywords.items():
            detected_keywords = []
            for keyword in keywords:
                if keyword.lower() in situation_lower:
                    detected_keywords.append(keyword)
            
            if detected_keywords:
                issues[category] = {
                    'keywords': detected_keywords,
                    'severity': self._calculate_severity(category, detected_keywords),
                    'articles': self._get_relevant_articles(category)
                }
        
        return issues
    
    def _calculate_severity(self, category: str, keywords: List[str]) -> str:
        """Calcule la sévérité du problème de déontologie"""
        severity_map = {
            "secret_medical": "CRITIQUE",
            "consentement": "ÉLEVÉE", 
            "obligation_information": "ÉLEVÉE",
            "independance": "MOYENNE",
            "competence": "MOYENNE",
            "dignite": "ÉLEVÉE"
        }
        return severity_map.get(category, "FAIBLE")
    
    def _get_relevant_articles(self, category: str) -> List[str]:
        """Retourne les articles de déontologie pertinents"""
        article_map = {
            "secret_medical": ["R.4127-4", "R.4127-5"],
            "consentement": ["R.4127-36", "R.4127-37", "R.4127-38"],
            "obligation_information": ["R.4127-35", "R.4127-36"],
            "independance": ["R.4127-12", "R.4127-13"],
            "competence": ["R.4127-11", "R.4127-14"],
            "dignite": ["R.4127-2", "R.4127-3"]
        }
        return article_map.get(category, [])
    
    def enhance_analysis_with_deontologie(self, analysis: str, situation: str) -> str:
        """
        Améliore l'analyse en ajoutant les aspects déontologiques UNIQUEMENT si pertinent
        
        Args:
            analysis: Analyse existante
            situation: Situation médicale
            
        Returns:
            Analyse enrichie avec déontologie (seulement si pertinent)
        """
        issues = self.detect_deontologie_issues(situation)
        
        # VÉRIFICATION INTELLIGENTE : Ajouter seulement si pertinent
        if not issues:
            print("ℹ️ Aucun problème de déontologie détecté - Section non ajoutée")
            return analysis
        
        # Vérifier la sévérité des problèmes
        has_critical_issues = any(details['severity'] == 'CRITIQUE' for details in issues.values())
        has_high_issues = any(details['severity'] == 'ÉLEVÉE' for details in issues.values())
        
        # Ajouter seulement si problèmes significatifs
        if not (has_critical_issues or has_high_issues):
            print("ℹ️ Problèmes de déontologie mineurs - Section non ajoutée")
            return analysis
        
        print(f"✅ Problèmes de déontologie détectés: {len(issues)} catégories - Section ajoutée")
        
        # Ajouter section déontologie
        deontologie_section = "\n\n## ⚖️ ASPECTS DÉONTOLOGIQUES\n\n"
        deontologie_section += "En tant qu'expert médico-légal, je dois également souligner les enjeux déontologiques de cette situation :\n\n"
        
        for category, details in issues.items():
            category_names = {
                "secret_medical": "Secret Médical",
                "consentement": "Consentement Éclairé", 
                "obligation_information": "Obligation d'Information",
                "independance": "Indépendance Professionnelle",
                "competence": "Compétence et Formation",
                "dignite": "Dignité et Respect"
            }
            
            category_name = category_names.get(category, category.replace('_', ' ').title())
            severity = details['severity']
            keywords = details['keywords']
            articles = details['articles']
            
            deontologie_section += f"### 🔍 {category_name} (Sévérité: {severity})\n\n"
            deontologie_section += f"**Problèmes détectés :** {', '.join(keywords)}\n\n"
            
            if articles:
                deontologie_section += f"**Articles de déontologie applicables :** {', '.join(articles)}\n\n"
            
            # Ajouter explication selon la catégorie
            explanations = {
                "secret_medical": "Le secret médical est un principe fondamental (art. R.4127-4 CSP). Toute violation peut entraîner des sanctions disciplinaires et pénales.",
                "consentement": "Le consentement éclairé est obligatoire pour tout acte médical (art. R.4127-36 CSP). Le patient doit être informé des risques et bénéfices.",
                "obligation_information": "Le médecin a l'obligation d'informer le patient de manière claire et adaptée (art. R.4127-35 CSP).",
                "independance": "Le médecin doit exercer en toute indépendance, sans conflit d'intérêt (art. R.4127-12 CSP).",
                "competence": "Le médecin doit maintenir et perfectionner ses connaissances (art. R.4127-11 CSP).",
                "dignite": "Le médecin doit respecter la dignité de la personne humaine (art. R.4127-2 CSP)."
            }
            
            deontologie_section += f"**Explication :** {explanations.get(category, 'Aspect déontologique à considérer.')}\n\n"
        
        # Recommandations déontologiques
        deontologie_section += "### 📋 Recommandations Déontologiques\n\n"
        deontologie_section += "1. **Vérifier le respect du secret médical** dans tous les échanges\n"
        deontologie_section += "2. **S'assurer du consentement éclairé** pour tous les actes\n"
        deontologie_section += "3. **Documenter l'information** fournie au patient\n"
        deontologie_section += "4. **Respecter l'indépendance** professionnelle\n"
        deontologie_section += "5. **Maintenir la compétence** par la formation continue\n\n"
        
        return analysis + deontologie_section
    
    def search_deontologie_chunks(self, query: str) -> List[Dict]:
        """
        Recherche spécifique dans les chunks de déontologie
        
        Args:
            query: Requête de recherche
            
        Returns:
            Liste des chunks pertinents
        """
        try:
            from local_kb_search import LocalKnowledgeBase
            
            kb = LocalKnowledgeBase()
            
            # Recherche avec mots-clés déontologie
            deontologie_queries = [
                f"déontologie {query}",
                f"code de déontologie {query}",
                f"R.4127 {query}"
            ]
            
            all_results = []
            for dq in deontologie_queries:
                results = kb.search(dq, top_k=5)
                all_results.extend(results)
            
            # Dédupliquer
            seen_links = set()
            unique_results = []
            for result in all_results:
                content_hash = hash(result.get('content', ''))
                if content_hash not in seen_links:
                    seen_links.add(content_hash)
                    unique_results.append(result)
            
            return unique_results[:10]
            
        except Exception as e:
            print(f"❌ Erreur recherche déontologie: {e}")
            return []

def test_deontologie_detection():
    """Test de détection des problèmes de déontologie"""
    
    print("🧪 TEST DÉTECTION DÉONTOLOGIE")
    print("=" * 40)
    
    engine = DeontologieSearchEngine()
    
    # Cas de test
    test_cases = [
        "Un médecin révèle des informations médicales à un tiers sans consentement du patient",
        "Le patient n'a pas été informé des risques de l'intervention",
        "Le médecin a accepté des cadeaux de l'industrie pharmaceutique",
        "Le médecin n'a pas respecté le secret médical en parlant du patient à sa famille"
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 CAS {i}: {case}")
        issues = engine.detect_deontologie_issues(case)
        
        if issues:
            for category, details in issues.items():
                print(f"  🔍 {category}: {details['severity']} - {details['keywords']}")
        else:
            print("  ✅ Aucun problème de déontologie détecté")

if __name__ == "__main__":
    test_deontologie_detection() 