"""
Cross-Encoder Reranker - Système de reranking spécialisé avec cross-encoder
Remplace le reranking avec Grok-4 par un système plus rapide et précis
"""

import json
import re
from typing import List, Dict, Optional, Tuple
import logging
from sentence_transformers import CrossEncoder
import numpy as np

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    """
    Système de reranking avec cross-encoder spécialisé pour le droit médical français
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialise le cross-encoder
        
        Args:
            model_name: Nom du modèle cross-encoder à utiliser
        """
        try:
            self.model = CrossEncoder(model_name)
            logger.info(f"✅ Cross-encoder chargé: {model_name}")
            self.is_available = True
        except Exception as e:
            logger.error(f"❌ Erreur chargement cross-encoder: {e}")
            self.is_available = False
            self.model = None
    
    def calculate_relevance_score(self, query: str, document: str) -> float:
        """
        Calcule le score de pertinence entre une requête et un document
        
        Args:
            query: Requête utilisateur
            document: Document à évaluer
            
        Returns:
            Score de pertinence (0-1)
        """
        if not self.is_available or not self.model:
            return 0.5  # Score par défaut
        
        try:
            # Préparation des paires query-document
            pairs = [[query, document]]
            
            # Calcul des scores
            scores = self.model.predict(pairs)
            
            # Normalisation (les scores peuvent être négatifs)
            score = float(scores[0])
            normalized_score = max(0.0, min(1.0, (score + 1) / 2))  # Normalisation 0-1
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul score: {e}")
            return 0.5
    
    def rerank_jurisprudence_results(self, results: List[Dict], query: str) -> List[Dict]:
        """
        Rerank les résultats de jurisprudence avec cross-encoder
        
        Args:
            results: Liste des résultats Google
            query: Requête originale
            
        Returns:
            Liste des résultats rerankés
        """
        if not results:
            return []
        
        logger.info(f"🔍 Reranking {len(results)} résultats jurisprudence avec cross-encoder...")
        
        # Calcul des scores pour chaque résultat
        scored_results = []
        for result in results:
            # Création du texte du document
            document_text = f"{result.get('title', '')} {result.get('snippet', '')}"
            
            # Calcul du score de pertinence
            relevance_score = self.calculate_relevance_score(query, document_text)
            
            # Score bonus pour les sources importantes
            source_bonus = self._calculate_source_bonus(result.get('source', ''), 'jurisprudence')
            
            # Score final
            final_score = relevance_score + source_bonus
            
            scored_results.append({
                **result,
                'llm_score': round(final_score * 10, 1),  # Score 0-10
                'llm_justification': self._generate_justification(relevance_score, source_bonus, result.get('source', ''))
            })
        
        # Tri par score décroissant
        scored_results.sort(key=lambda x: x['llm_score'], reverse=True)
        
        logger.info(f"✅ Reranking jurisprudence terminé - {len(scored_results[:3])} résultats sélectionnés")
        return scored_results[:3]
    
    def rerank_oniam_results(self, results: List[Dict], query: str) -> List[Dict]:
        """
        Rerank les résultats ONIAM avec cross-encoder
        
        Args:
            results: Liste des résultats Google
            query: Requête originale
            
        Returns:
            Liste des résultats rerankés
        """
        if not results:
            return []
        
        logger.info(f"🔍 Reranking {len(results)} résultats ONIAM avec cross-encoder...")
        
        # Calcul des scores pour chaque résultat
        scored_results = []
        for result in results:
            # Création du texte du document
            document_text = f"{result.get('title', '')} {result.get('snippet', '')}"
            
            # Calcul du score de pertinence
            relevance_score = self.calculate_relevance_score(query, document_text)
            
            # Score bonus pour les sources importantes
            source_bonus = self._calculate_source_bonus(result.get('source', ''), 'oniam')
            
            # Score final
            final_score = relevance_score + source_bonus
            
            scored_results.append({
                **result,
                'llm_score': round(final_score * 10, 1),  # Score 0-10
                'llm_justification': self._generate_justification(relevance_score, source_bonus, result.get('source', ''))
            })
        
        # Tri par score décroissant
        scored_results.sort(key=lambda x: x['llm_score'], reverse=True)
        
        logger.info(f"✅ Reranking ONIAM terminé - {len(scored_results[:3])} résultats sélectionnés")
        return scored_results[:3]
    
    def _calculate_source_bonus(self, source: str, result_type: str) -> float:
        """
        Calcule un bonus de score selon la source
        
        Args:
            source: Nom de la source
            result_type: Type de résultat ('jurisprudence' ou 'oniam')
            
        Returns:
            Bonus de score (0-0.2)
        """
        source_lower = source.lower()
        
        if result_type == 'jurisprudence':
            # Sources juridiques importantes
            if any(keyword in source_lower for keyword in ['cassation', 'cour de cassation']):
                return 0.2
            elif any(keyword in source_lower for keyword in ['conseil d\'état', 'conseil d\'etat']):
                return 0.15
            elif any(keyword in source_lower for keyword in ['cour d\'appel', 'tribunal']):
                return 0.1
            elif any(keyword in source_lower for keyword in ['legifrance', 'service-public']):
                return 0.05
        
        elif result_type == 'oniam':
            # Sources ONIAM importantes
            if any(keyword in source_lower for keyword in ['oniam', 'office national']):
                return 0.2
            elif any(keyword in source_lower for keyword in ['ameli', 'assurance maladie']):
                return 0.15
            elif any(keyword in source_lower for keyword in ['service-public', 'gouvernement']):
                return 0.1
            elif any(keyword in source_lower for keyword in ['legifrance', 'droit']):
                return 0.05
        
        return 0.0
    
    def _generate_justification(self, relevance_score: float, source_bonus: float, source: str) -> str:
        """
        Génère une justification pour le score
        
        Args:
            relevance_score: Score de pertinence
            source_bonus: Bonus de source
            source: Nom de la source
            
        Returns:
            Justification du score
        """
        if relevance_score > 0.8:
            pertinence = "très pertinent"
        elif relevance_score > 0.6:
            pertinence = "pertinent"
        elif relevance_score > 0.4:
            pertinence = "modérément pertinent"
        else:
            pertinence = "peu pertinent"
        
        if source_bonus > 0.1:
            source_qualite = f"Source de qualité ({source})"
        else:
            source_qualite = f"Source standard ({source})"
        
        return f"{pertinence.capitalize()} - {source_qualite}"
    
    def rerank_general_results(self, results: List[Dict], query: str, result_type: str = "general") -> List[Dict]:
        """
        Reranking général pour tout type de résultats
        
        Args:
            results: Liste des résultats
            query: Requête originale
            result_type: Type de résultats
            
        Returns:
            Liste des résultats rerankés
        """
        if result_type == "jurisprudence":
            return self.rerank_jurisprudence_results(results, query)
        elif result_type == "oniam":
            return self.rerank_oniam_results(results, query)
        else:
            # Reranking général
            if not results:
                return []
            
            logger.info(f"🔍 Reranking {len(results)} résultats généraux avec cross-encoder...")
            
            scored_results = []
            for result in results:
                document_text = f"{result.get('title', '')} {result.get('snippet', '')}"
                relevance_score = self.calculate_relevance_score(query, document_text)
                
                scored_results.append({
                    **result,
                    'llm_score': round(relevance_score * 10, 1),
                    'llm_justification': f"Score de pertinence: {relevance_score:.2f}"
                })
            
            scored_results.sort(key=lambda x: x['llm_score'], reverse=True)
            return scored_results[:3]

# Instance globale
cross_encoder_reranker = None

def get_cross_encoder_reranker() -> CrossEncoderReranker:
    """Retourne l'instance du cross-encoder reranker (singleton)"""
    global cross_encoder_reranker
    if cross_encoder_reranker is None:
        cross_encoder_reranker = CrossEncoderReranker()
    return cross_encoder_reranker

def test_cross_encoder():
    """Test du cross-encoder reranker"""
    print("🧪 TEST CROSS-ENCODER RERANKER")
    print("=" * 50)
    
    # Test d'initialisation
    reranker = get_cross_encoder_reranker()
    
    if not reranker.is_available:
        print("❌ Cross-encoder non disponible")
        return
    
    # Test de calcul de score
    query = "responsabilité médicale erreur chirurgicale"
    document = "Cour de Cassation - Responsabilité médicale - Erreur chirurgicale - Indemnisation"
    
    score = reranker.calculate_relevance_score(query, document)
    print(f"📊 Score de pertinence: {score:.3f}")
    
    # Test de reranking
    test_results = [
        {
            "title": "Responsabilité médicale - Cour de Cassation 2024",
            "source": "Cour de Cassation",
            "snippet": "Arrêt important sur la responsabilité médicale en cas d'erreur chirurgicale",
            "link": "https://example.com/cassation"
        },
        {
            "title": "ONIAM - Indemnisation erreur médicale",
            "source": "ONIAM",
            "snippet": "Barème d'indemnisation pour les erreurs médicales sans faute",
            "link": "https://example.com/oniam"
        }
    ]
    
    reranked = reranker.rerank_jurisprudence_results(test_results, query)
    print(f"✅ Reranking test réussi: {len(reranked)} résultats")

if __name__ == "__main__":
    test_cross_encoder() 