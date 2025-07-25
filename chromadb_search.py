"""
Système de Recherche ChromaDB pour LegalDocBot
Utilise la base ChromaDB avec 12,024 chunks pour enrichir l'analyse
"""

import chromadb
from typing import List, Dict, Optional
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaDBSearch:
    """
    Système de recherche ChromaDB pour la base de connaissances juridique
    """
    
    def __init__(self):
        """Initialise la connexion à ChromaDB"""
        try:
            self.client = chromadb.PersistentClient(path='chroma_db')
            
            # Vérifier si les collections existent
            available_collections = [c.name for c in self.client.list_collections()]
            logger.info(f"📚 Collections disponibles: {available_collections}")
            
            # Essayer de charger les collections attendues
            self.collections = {}
            expected_collections = {
                'deontologie': 'deontologie',
                'csp': 'csp_legislation',
                'css': 'css_legislation', 
                'penal': 'penal_legislation',
                'civil': 'civil_legislation'
            }
            
            for key, collection_name in expected_collections.items():
                if collection_name in available_collections:
                    try:
                        self.collections[key] = self.client.get_collection(collection_name)
                        logger.info(f"✅ Collection {collection_name} chargée")
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur chargement {collection_name}: {e}")
                else:
                    logger.warning(f"⚠️ Collection {collection_name} manquante")
            
            if self.collections:
                logger.info("✅ ChromaDB connecté avec succès")
                self.is_available = True
            else:
                logger.warning("⚠️ Aucune collection ChromaDB disponible")
                self.is_available = False
                
        except Exception as e:
            logger.error(f"❌ Erreur connexion ChromaDB: {e}")
            self.is_available = False
    
    def search_legal_knowledge(self, query: str, top_k: int = 10, use_reranking: bool = True) -> List[Dict]:
        """
        Recherche dans toute la base de connaissances ChromaDB avec reranking optionnel
        
        Args:
            query: Requête de recherche
            top_k: Nombre maximum de résultats par collection
            use_reranking: Utiliser le cross-encoder pour reranker les résultats
            
        Returns:
            Liste des chunks pertinents avec métadonnées
        """
        if not self.is_available:
            logger.warning("⚠️ ChromaDB non disponible")
            return []
        
        all_results = []
        
        try:
            # Recherche dans toutes les collections
            for collection_name, collection in self.collections.items():
                try:
                    results = collection.query(
                        query_texts=[query],
                        n_results=top_k,
                        include=['metadatas', 'documents', 'distances']
                    )
                    
                    if results['documents'] and results['documents'][0]:
                        for i, (doc, metadata, distance) in enumerate(zip(
                            results['documents'][0],
                            results['metadatas'][0],
                            results['distances'][0]
                        )):
                            # Calculer un score de pertinence (distance inverse)
                            relevance_score = max(0, 1 - distance)
                            
                            result = {
                                'content': doc,
                                'metadata': metadata,
                                'collection': collection_name,
                                'relevance_score': relevance_score,
                                'source': metadata.get('source_file', 'Inconnu'),
                                'article': metadata.get('article', ''),
                                'doc_type': metadata.get('doc_type', '')
                            }
                            all_results.append(result)
                            
                except Exception as e:
                    logger.error(f"❌ Erreur recherche {collection_name}: {e}")
            
            # Reranking avec cross-encoder si demandé
            if use_reranking and all_results:
                try:
                    from chromadb_reranker import get_chromadb_reranker
                    reranker = get_chromadb_reranker()
                    if reranker.is_available:
                        logger.info("🔍 Application du reranking cross-encoder...")
                        all_results = reranker.rerank_chromadb_results(all_results, query)
                    else:
                        # Trier par score de pertinence si pas de reranking
                        all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
                except Exception as e:
                    logger.error(f"❌ Erreur reranking: {e}")
                    # Trier par score de pertinence en cas d'erreur
                    all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            else:
                # Trier par score de pertinence
                all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            logger.info(f"✅ Recherche ChromaDB: {len(all_results)} résultats trouvés")
            return all_results[:top_k * 2]  # Retourner plus de résultats pour diversité
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche ChromaDB: {e}")
            return []
    
    def search_deontologie(self, query: str, top_k: int = 5, use_reranking: bool = True) -> List[Dict]:
        """
        Recherche spécifique dans la collection déontologie avec reranking optionnel
        
        Args:
            query: Requête de recherche
            top_k: Nombre maximum de résultats
            use_reranking: Utiliser le cross-encoder pour reranker les résultats
            
        Returns:
            Liste des chunks de déontologie pertinents
        """
        if not self.is_available or 'deontologie' not in self.collections:
            return []
        
        try:
            results = self.collections['deontologie'].query(
                query_texts=[query],
                n_results=top_k,
                include=['metadatas', 'documents', 'distances']
            )
            
            deont_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    relevance_score = max(0, 1 - distance)
                    
                    result = {
                        'content': doc,
                        'metadata': metadata,
                        'collection': 'deontologie',
                        'relevance_score': relevance_score,
                        'source': metadata.get('source_file', 'codedeont.pdf'),
                        'article': metadata.get('article', ''),
                        'doc_type': 'deontologie'
                    }
                    deont_results.append(result)
            
            # Reranking avec cross-encoder si demandé
            if use_reranking and deont_results:
                try:
                    from chromadb_reranker import get_chromadb_reranker
                    reranker = get_chromadb_reranker()
                    if reranker.is_available:
                        logger.info("🔍 Application du reranking cross-encoder déontologie...")
                        deont_results = reranker.rerank_deontologie_results(deont_results, query)
                    else:
                        # Trier par score de pertinence si pas de reranking
                        deont_results.sort(key=lambda x: x['relevance_score'], reverse=True)
                except Exception as e:
                    logger.error(f"❌ Erreur reranking déontologie: {e}")
                    # Trier par score de pertinence en cas d'erreur
                    deont_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            else:
                # Trier par score de pertinence
                deont_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            logger.info(f"✅ Recherche déontologie: {len(deont_results)} résultats")
            return deont_results
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche déontologie: {e}")
            return []
    
    def search_csp(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Recherche spécifique dans le Code de la santé publique
        
        Args:
            query: Requête de recherche
            top_k: Nombre maximum de résultats
            
        Returns:
            Liste des chunks CSP pertinents
        """
        if not self.is_available or 'csp' not in self.collections:
            return []
        
        try:
            results = self.collections['csp'].query(
                query_texts=[query],
                n_results=top_k,
                include=['metadatas', 'documents', 'distances']
            )
            
            csp_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    relevance_score = max(0, 1 - distance)
                    
                    result = {
                        'content': doc,
                        'metadata': metadata,
                        'collection': 'csp',
                        'relevance_score': relevance_score,
                        'source': metadata.get('source_file', 'Code de la santé publique.pdf'),
                        'article': metadata.get('article', ''),
                        'doc_type': 'csp'
                    }
                    csp_results.append(result)
            
            logger.info(f"✅ Recherche CSP: {len(csp_results)} résultats")
            return csp_results
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche CSP: {e}")
            return []
    
    def search_unified_legal_knowledge(self, query: str, top_k: int = 15, use_reranking: bool = True) -> List[Dict]:
        """
        Recherche UNIFIÉE dans TOUTE la base de connaissances ChromaDB
        Retourne les MEILLEURS articles de TOUTES les sources (CSP, déontologie, CSS, civil, pénal)
        
        Args:
            query: Requête de recherche
            top_k: Nombre maximum de résultats totaux
            use_reranking: Utiliser le cross-encoder pour reranker les résultats
            
        Returns:
            Liste des MEILLEURS chunks de TOUTES les sources juridiques
        """
        if not self.is_available:
            logger.warning("⚠️ ChromaDB non disponible")
            return []
        
        all_results = []
        
        try:
            # Recherche dans TOUTES les collections en parallèle
            for collection_name, collection in self.collections.items():
                try:
                    # Recherche plus large dans chaque collection
                    results = collection.query(
                        query_texts=[query],
                        n_results=top_k,  # Plus de résultats par collection
                        include=['metadatas', 'documents', 'distances']
                    )
                    
                    if results['documents'] and results['documents'][0]:
                        for i, (doc, metadata, distance) in enumerate(zip(
                            results['documents'][0],
                            results['metadatas'][0],
                            results['distances'][0]
                        )):
                            # Calculer un score de pertinence (distance inverse)
                            relevance_score = max(0, 1 - distance)
                            
                            result = {
                                'content': doc,
                                'metadata': metadata,
                                'collection': collection_name,
                                'relevance_score': relevance_score,
                                'source': metadata.get('source_file', 'Inconnu'),
                                'article': metadata.get('article', ''),
                                'doc_type': metadata.get('doc_type', ''),
                                'source_type': self._get_source_type(collection_name)
                            }
                            all_results.append(result)
                            
                except Exception as e:
                    logger.error(f"❌ Erreur recherche {collection_name}: {e}")
            
            logger.info(f"🔍 Recherche unifiée: {len(all_results)} résultats trouvés dans toutes les sources")
            
            # Reranking UNIFIÉ avec cross-encoder pour TOUS les résultats
            if use_reranking and all_results:
                try:
                    from chromadb_reranker import get_chromadb_reranker
                    reranker = get_chromadb_reranker()
                    if reranker.is_available:
                        logger.info("🔍 Application du reranking cross-encoder UNIFIÉ...")
                        all_results = reranker.rerank_unified_results(all_results, query)
                    else:
                        # Trier par score de pertinence si pas de reranking
                        all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
                except Exception as e:
                    logger.error(f"❌ Erreur reranking unifié: {e}")
                    # Trier par score de pertinence en cas d'erreur
                    all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            else:
                # Trier par score de pertinence
                all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            logger.info(f"✅ Recherche unifiée terminée: {len(all_results[:top_k])} meilleurs résultats de toutes les sources")
            return all_results[:top_k]  # Retourner les meilleurs de toutes les sources
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche unifiée ChromaDB: {e}")
            return []
    
    def _get_source_type(self, collection_name: str) -> str:
        """
        Retourne le type de source pour l'affichage
        
        Args:
            collection_name: Nom de la collection
            
        Returns:
            Type de source lisible
        """
        source_types = {
            'deontologie': 'Code de Déontologie Médicale',
            'csp': 'Code de la Santé Publique',
            'css': 'Code de la Sécurité Sociale',
            'penal': 'Code Pénal',
            'civil': 'Code Civil'
        }
        return source_types.get(collection_name, collection_name.upper())
    
    def get_collection_stats(self) -> Dict:
        """
        Retourne les statistiques des collections
        
        Returns:
            Dictionnaire avec les statistiques
        """
        if not self.is_available:
            return {}
        
        stats = {}
        for collection_name, collection in self.collections.items():
            try:
                count = collection.count()
                stats[collection_name] = count
            except Exception as e:
                logger.error(f"❌ Erreur stats {collection_name}: {e}")
                stats[collection_name] = 0
        
        return stats

# Instance globale
chromadb_search = None

def get_chromadb_search() -> ChromaDBSearch:
    """Retourne l'instance du système de recherche ChromaDB (singleton)"""
    global chromadb_search
    if chromadb_search is None:
        chromadb_search = ChromaDBSearch()
    return chromadb_search

def test_chromadb_search():
    """Test du système de recherche ChromaDB"""
    
    print("🧪 TEST CHROMADB SEARCH")
    print("=" * 40)
    
    # Test d'initialisation
    search = get_chromadb_search()
    
    if not search.is_available:
        print("❌ ChromaDB non disponible")
        return
    
    # Statistiques
    stats = search.get_collection_stats()
    print("📊 Statistiques des collections:")
    for collection, count in stats.items():
        print(f"  - {collection}: {count} chunks")
    
    # Test de recherche UNIFIÉE
    test_query = "secret médical et responsabilité médicale"
    print(f"\n🔍 Test RECHERCHE UNIFIÉE: '{test_query}'")
    
    # Recherche unifiée
    unified_results = search.search_unified_legal_knowledge(test_query, top_k=10)
    print(f"✅ Recherche unifiée: {len(unified_results)} résultats de toutes les sources")
    
    # Grouper par source
    sources = {}
    for result in unified_results:
        source_type = result.get('source_type', result['collection'].upper())
        if source_type not in sources:
            sources[source_type] = []
        sources[source_type].append(result)
    
    # Afficher les résultats par source
    for source_type, results in sources.items():
        print(f"\n📚 {source_type}:")
        for i, result in enumerate(results[:3], 1):
            final_score = result.get('final_score', result['relevance_score'])
            print(f"  {i}. Article {result['article']} (Score: {final_score:.2f})")
            if result.get('reranked'):
                cross_score = result.get('cross_encoder_score', 0)
                source_bonus = result.get('source_bonus', 0)
                print(f"     Cross-Encoder: {cross_score:.2f} | Bonus: {source_bonus:.2f}")
    
    # Test de recherche classique
    test_queries = [
        "secret médical",
        "consentement éclairé",
        "responsabilité médicale",
        "obligation d'information"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Recherche classique: '{query}'")
        
        # Recherche générale
        results = search.search_legal_knowledge(query, top_k=3)
        print(f"  Résultats généraux: {len(results)}")
        
        # Recherche déontologie
        deont_results = search.search_deontologie(query, top_k=2)
        print(f"  Résultats déontologie: {len(deont_results)}")
        
        if deont_results:
            for i, result in enumerate(deont_results[:2]):
                print(f"    {i+1}. {result['article']} (score: {result['relevance_score']:.2f})")
                print(f"       {result['content'][:80]}...")

if __name__ == "__main__":
    test_chromadb_search() 