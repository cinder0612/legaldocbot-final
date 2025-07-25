"""
ChromaDB Cross-Encoder Reranker
Système de reranking spécialisé pour les résultats ChromaDB avec cross-encoder
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

class ChromaDBReranker:
    """
    Système de reranking avec cross-encoder spécialisé pour les résultats ChromaDB
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialise le cross-encoder pour ChromaDB
        
        Args:
            model_name: Nom du modèle cross-encoder à utiliser
        """
        try:
            # Correction de l'erreur PyTorch
            import torch
            self.model = CrossEncoder(model_name)
            
            # Utiliser to_empty() au lieu de to() pour éviter l'erreur meta tensor
            if torch.cuda.is_available():
                self.model.model = self.model.model.to_empty(device='cuda')
            else:
                self.model.model = self.model.model.to_empty(device='cpu')
                
            logger.info(f"✅ Cross-encoder ChromaDB chargé: {model_name}")
            self.is_available = True
        except Exception as e:
            logger.error(f"❌ Erreur chargement cross-encoder ChromaDB: {e}")
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
            logger.error(f"❌ Erreur calcul score ChromaDB: {e}")
            return 0.5
    
    def rerank_chromadb_results(self, results: List[Dict], query: str) -> List[Dict]:
        """
        Rerank les résultats ChromaDB avec cross-encoder
        
        Args:
            results: Liste des résultats ChromaDB
            query: Requête originale
            
        Returns:
            Liste des résultats rerankés
        """
        if not results:
            return []
        
        logger.info(f"🔍 Reranking {len(results)} résultats ChromaDB avec cross-encoder...")
        
        # Calcul des scores pour chaque résultat
        scored_results = []
        for result in results:
            # Création du texte du document
            document_text = f"{result.get('content', '')}"
            
            # Calcul du score de pertinence cross-encoder
            cross_encoder_score = self.calculate_relevance_score(query, document_text)
            
            # Score ChromaDB original (distance inverse)
            chromadb_score = result.get('relevance_score', 0.5)
            
            # Score bonus selon le type de document
            type_bonus = self._calculate_type_bonus(result.get('collection', ''), result.get('doc_type', ''))
            
            # Score bonus selon l'article
            article_bonus = self._calculate_article_bonus(result.get('article', ''), query)
            
            # Score final pondéré (70% cross-encoder + 20% ChromaDB + 10% bonus)
            final_score = (cross_encoder_score * 0.7) + (chromadb_score * 0.2) + (type_bonus + article_bonus) * 0.1
            
            scored_results.append({
                **result,
                'cross_encoder_score': round(cross_encoder_score, 3),
                'final_score': round(final_score, 3),
                'type_bonus': round(type_bonus, 3),
                'article_bonus': round(article_bonus, 3),
                'reranked': True
            })
        
        # Tri par score final décroissant
        scored_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        logger.info(f"✅ Reranking ChromaDB terminé - {len(scored_results[:5])} meilleurs résultats sélectionnés")
        return scored_results[:5]
    
    def rerank_unified_results(self, results: List[Dict], query: str) -> List[Dict]:
        """
        Rerank UNIFIÉ pour TOUS les résultats de TOUTES les sources juridiques
        Sélectionne les MEILLEURS articles de CSP, déontologie, CSS, civil, pénal
        
        Args:
            results: Liste des résultats de toutes les sources
            query: Requête originale
            
        Returns:
            Liste des MEILLEURS résultats de toutes les sources
        """
        if not results:
            return []
        
        logger.info(f"🔍 Reranking UNIFIÉ {len(results)} résultats de toutes les sources avec cross-encoder...")
        
        # Calcul des scores pour chaque résultat
        scored_results = []
        for result in results:
            # Création du texte du document
            document_text = f"{result.get('content', '')}"
            
            # Calcul du score de pertinence cross-encoder
            cross_encoder_score = self.calculate_relevance_score(query, document_text)
            
            # Score ChromaDB original
            chromadb_score = result.get('relevance_score', 0.5)
            
            # Bonus selon le type de source
            source_bonus = self._calculate_unified_source_bonus(result.get('collection', ''), result.get('article', ''), query)
            
            # Score final pondéré (70% cross-encoder + 20% ChromaDB + 10% bonus source)
            final_score = (cross_encoder_score * 0.7) + (chromadb_score * 0.2) + (source_bonus * 0.1)
            
            scored_results.append({
                **result,
                'cross_encoder_score': round(cross_encoder_score, 3),
                'final_score': round(final_score, 3),
                'source_bonus': round(source_bonus, 3),
                'reranked': True
            })
        
        # Tri par score final décroissant
        scored_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        logger.info(f"✅ Reranking UNIFIÉ terminé - {len(scored_results[:10])} meilleurs résultats de toutes les sources sélectionnés")
        return scored_results[:10]  # Retourner les 10 meilleurs de toutes les sources
    
    def rerank_deontologie_results(self, results: List[Dict], query: str) -> List[Dict]:
        """
        Rerank spécifiquement les résultats de déontologie
        
        Args:
            results: Liste des résultats de déontologie
            query: Requête originale
            
        Returns:
            Liste des résultats rerankés
        """
        if not results:
            return []
        
        logger.info(f"🔍 Reranking {len(results)} résultats déontologie avec cross-encoder...")
        
        # Calcul des scores pour chaque résultat
        scored_results = []
        for result in results:
            # Création du texte du document
            document_text = f"{result.get('content', '')}"
            
            # Calcul du score de pertinence cross-encoder
            cross_encoder_score = self.calculate_relevance_score(query, document_text)
            
            # Score ChromaDB original
            chromadb_score = result.get('relevance_score', 0.5)
            
            # Bonus spécial pour la déontologie
            deontologie_bonus = self._calculate_deontologie_bonus(result.get('article', ''), query)
            
            # Score final pondéré (60% cross-encoder + 20% ChromaDB + 20% bonus déontologie)
            final_score = (cross_encoder_score * 0.6) + (chromadb_score * 0.2) + (deontologie_bonus * 0.2)
            
            scored_results.append({
                **result,
                'cross_encoder_score': round(cross_encoder_score, 3),
                'final_score': round(final_score, 3),
                'deontologie_bonus': round(deontologie_bonus, 3),
                'reranked': True
            })
        
        # Tri par score final décroissant
        scored_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        logger.info(f"✅ Reranking déontologie terminé - {len(scored_results[:3])} meilleurs résultats sélectionnés")
        return scored_results[:3]
    
    def _calculate_type_bonus(self, collection: str, doc_type: str) -> float:
        """
        Calcule un bonus selon le type de document
        
        Args:
            collection: Collection ChromaDB
            doc_type: Type de document
            
        Returns:
            Bonus de score (0-0.3)
        """
        collection_lower = collection.lower()
        doc_type_lower = doc_type.lower()
        
        # Bonus pour la déontologie (priorité haute)
        if 'deontologie' in collection_lower or 'deontologie' in doc_type_lower:
            return 0.3
        
        # Bonus pour le CSP (priorité moyenne)
        elif 'csp' in collection_lower or 'santé' in doc_type_lower:
            return 0.2
        
        # Bonus pour le code civil (priorité moyenne)
        elif 'civil' in collection_lower:
            return 0.15
        
        # Bonus pour le code pénal (priorité moyenne)
        elif 'penal' in collection_lower:
            return 0.15
        
        # Bonus pour le CSS (priorité basse)
        elif 'css' in collection_lower:
            return 0.1
        
        return 0.0
    
    def _calculate_article_bonus(self, article: str, query: str) -> float:
        """
        Calcule un bonus selon la pertinence de l'article
        
        Args:
            article: Numéro d'article
            query: Requête utilisateur
            
        Returns:
            Bonus de score (0-0.2)
        """
        if not article:
            return 0.0
        
        query_lower = query.lower()
        article_lower = article.lower()
        
        # Articles déontologie importants
        deontologie_keywords = ['secret', 'consentement', 'information', 'responsabilité', 'confidentialité']
        if any(keyword in query_lower for keyword in deontologie_keywords):
            if 'r.4127' in article_lower:
                return 0.2
        
        # Articles CSP importants
        csp_keywords = ['responsabilité', 'faute', 'accident', 'erreur', 'maladie']
        if any(keyword in query_lower for keyword in csp_keywords):
            if 'l.1142' in article_lower or 'l.1143' in article_lower:
                return 0.2
        
        return 0.0
    
    def _calculate_deontologie_bonus(self, article: str, query: str) -> float:
        """
        Calcule un bonus spécial pour les articles de déontologie
        
        Args:
            article: Numéro d'article
            query: Requête utilisateur
            
        Returns:
            Bonus de score (0-0.4)
        """
        if not article:
            return 0.0
        
        query_lower = query.lower()
        article_lower = article_lower = article.lower()
        
        # Mapping des articles déontologie par thème
        deontologie_mapping = {
            'secret': ['r.4127-4', 'r.4127-72', 'r.4127-104'],
            'consentement': ['r.4127-36', 'r.4127-37', 'r.4127-38'],
            'information': ['r.4127-35', 'r.4127-47', 'r.4127-48'],
            'responsabilité': ['r.4127-95', 'r.4127-96', 'r.4127-97'],
            'confidentialité': ['r.4127-4', 'r.4127-72', 'r.4127-104'],
            'éthique': ['r.4127-1', 'r.4127-2', 'r.4127-3']
        }
        
        # Vérifier la correspondance
        for theme, articles in deontologie_mapping.items():
            if theme in query_lower:
                if any(art in article_lower for art in articles):
                    return 0.4
        
        # Bonus général pour les articles R.4127
        if 'r.4127' in article_lower:
            return 0.2
        
        return 0.0
    
    def _calculate_unified_source_bonus(self, collection: str, article: str, query: str) -> float:
        """
        Calcule un bonus unifié pour toutes les sources juridiques
        
        Args:
            collection: Collection ChromaDB
            article: Numéro d'article
            query: Requête utilisateur
            
        Returns:
            Bonus de score (0-0.4)
        """
        if not article:
            return 0.0
        
        query_lower = query.lower()
        collection_lower = collection.lower()
        article_lower = article.lower()
        
        # Bonus selon le type de collection
        collection_bonus = 0.0
        
        # Déontologie (priorité haute)
        if 'deontologie' in collection_lower:
            collection_bonus = 0.4
            # Bonus spécifique pour articles déontologie
            deontologie_keywords = ['secret', 'consentement', 'information', 'responsabilité', 'confidentialité', 'éthique']
            if any(keyword in query_lower for keyword in deontologie_keywords):
                if 'r.4127' in article_lower:
                    return 0.4
        
        # CSP (priorité haute)
        elif 'csp' in collection_lower:
            collection_bonus = 0.3
            # Bonus spécifique pour articles CSP
            csp_keywords = ['responsabilité', 'faute', 'accident', 'erreur', 'maladie', 'santé']
            if any(keyword in query_lower for keyword in csp_keywords):
                if 'l.1142' in article_lower or 'l.1143' in article_lower:
                    return 0.4
        
        # Code civil (priorité moyenne)
        elif 'civil' in collection_lower:
            collection_bonus = 0.25
            # Bonus spécifique pour articles civil
            civil_keywords = ['responsabilité', 'dommage', 'faute', 'réparation']
            if any(keyword in query_lower for keyword in civil_keywords):
                if '1382' in article_lower or '1383' in article_lower:
                    return 0.3
        
        # Code pénal (priorité moyenne)
        elif 'penal' in collection_lower:
            collection_bonus = 0.25
            # Bonus spécifique pour articles pénal
            penal_keywords = ['faute', 'délit', 'infraction', 'sanction']
            if any(keyword in query_lower for keyword in penal_keywords):
                if '121-1' in article_lower or '121-2' in article_lower:
                    return 0.3
        
        # CSS (priorité basse)
        elif 'css' in collection_lower:
            collection_bonus = 0.2
            # Bonus spécifique pour articles CSS
            css_keywords = ['sécurité sociale', 'assurance', 'remboursement']
            if any(keyword in query_lower for keyword in css_keywords):
                return 0.25
        
        return collection_bonus

# Instance globale
chromadb_reranker = None

def get_chromadb_reranker() -> ChromaDBReranker:
    """Retourne l'instance du reranker ChromaDB (singleton)"""
    global chromadb_reranker
    if chromadb_reranker is None:
        chromadb_reranker = ChromaDBReranker()
    return chromadb_reranker

def test_chromadb_reranker():
    """Test du système de reranking ChromaDB"""
    
    print("🧪 TEST CHROMADB RERANKER")
    print("=" * 40)
    
    # Test d'initialisation
    reranker = get_chromadb_reranker()
    
    if not reranker.is_available:
        print("❌ Cross-encoder ChromaDB non disponible")
        return
    
    # Test avec des résultats simulés
    test_results = [
        {
            'content': 'Article R.4127-4 - Le secret professionnel, institué dans l\'intérêt des patients, s\'impose à tout médecin dans les conditions établies par la loi.',
            'collection': 'deontologie',
            'article': 'R.4127-4',
            'relevance_score': 0.8,
            'source': 'codedeont.pdf'
        },
        {
            'content': 'Article R.4127-36 - Le consentement de la personne examinée ou soignée doit être recherché dans tous les cas.',
            'collection': 'deontologie',
            'article': 'R.4127-36',
            'relevance_score': 0.7,
            'source': 'codedeont.pdf'
        },
        {
            'content': 'Article L.1142-1 - Les professionnels de santé, les établissements de santé, les centres de santé, les réseaux de santé...',
            'collection': 'csp',
            'article': 'L.1142-1',
            'relevance_score': 0.6,
            'source': 'Code de la santé publique.pdf'
        }
    ]
    
    test_query = "secret médical et consentement éclairé"
    
    print(f"🔍 Test reranking avec: '{test_query}'")
    
    # Reranking général
    reranked_results = reranker.rerank_chromadb_results(test_results, test_query)
    
    print(f"✅ Résultats rerankés: {len(reranked_results)}")
    for i, result in enumerate(reranked_results, 1):
        print(f"  {i}. Article {result['article']}")
        print(f"     Score final: {result['final_score']}")
        print(f"     Cross-encoder: {result['cross_encoder_score']}")
        print(f"     Bonus type: {result['type_bonus']}")
        print(f"     Bonus article: {result['article_bonus']}")
        print()
    
    # Reranking déontologie
    deont_results = [r for r in test_results if r['collection'] == 'deontologie']
    reranked_deont = reranker.rerank_deontologie_results(deont_results, test_query)
    
    print(f"✅ Déontologie rerankée: {len(reranked_deont)}")
    for i, result in enumerate(reranked_deont, 1):
        print(f"  {i}. Article {result['article']} - Score: {result['final_score']}")

if __name__ == "__main__":
    test_chromadb_reranker() 