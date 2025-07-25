#!/usr/bin/env python3
"""
Module de recherche Google optimisé pour le bot médico-légal
Utilise uniquement Google Search avec rotation des clés API
"""

import os
import time
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration API
API_CONFIG = {
    "google": {
        "max_results": 10,
        "timeout": 10,
        "retry_attempts": 3
    }
}

class GoogleSearchAPI:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        # CSE IDs - Deux CSE séparés
        self.jurisprudence_cse_id = "votre_cse_jurisprudence_ici"  # CSE Jurisprudence
        self.oniam_cse_id = os.getenv('ONIAM_CSE_ID', "b044b42dfe03243fe")  # CSE ONIAM dédié
        
        self.max_results = API_CONFIG["google"]["max_results"]
        
        # Gestion des quotas
        self.daily_quota = 10000
        self.requests_made = 0
        self.last_request_time = 0
        self.rate_limit_delay = 0.1
        
        # Système de rotation des clés API
        self.api_keys = self._load_multiple_api_keys()
        self.current_key_index = 0
        
        # Cache simple
        self.cache = {}
        self.cache_duration = 3600  # 1 heure
        
        print(f"🔍 Google Search configuré - API Key: {self.api_key[:10]}...")
        print(f"📊 Quota quotidien: {self.daily_quota} requêtes")
        print(f"⚖️ CSE Jurisprudence: {self.jurisprudence_cse_id}")
        print(f"🏥 CSE ONIAM: {self.oniam_cse_id}")
        print(f"🔑 Clés API disponibles: {len(self.api_keys)}")
    
    def _load_multiple_api_keys(self) -> List[str]:
        """Charge toutes les clés API disponibles"""
        keys = []
        
        # Clé principale
        if self.api_key:
            keys.append(self.api_key)
        
        # Clés supplémentaires
        for i in range(2, 6):
            key = os.getenv(f'GOOGLE_API_KEY_{i}')
            if key and key != f"votre_{i}e_clé_api_google":
                keys.append(key)
        
        return keys if keys else [self.api_key] if self.api_key else []
    
    def _get_next_api_key(self) -> str:
        """Rotation des clés API"""
        if not self.api_keys:
            raise ValueError("Aucune clé API disponible")
        
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key
    
    def _get_cache_key(self, query: str, search_type: str) -> str:
        """Génère une clé de cache"""
        return f"{search_type}:{query.lower().strip()}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Vérifie si le cache est valide"""
        if cache_key not in self.cache:
            return False
        
        timestamp, _ = self.cache[cache_key]
        return (time.time() - timestamp) < self.cache_duration
    
    def search(self, query: str, search_type: str = "general", max_results: int = 10) -> List[Dict]:
        """
        Recherche Google optimisée
        
        Args:
            query: Requête de recherche
            search_type: Type de recherche (jurisprudence, oniam, general)
            max_results: Nombre maximum de résultats
            
        Returns:
            Liste des résultats
        """
        # Vérifier le cache
        cache_key = self._get_cache_key(query, search_type)
        if self._is_cache_valid(cache_key):
            print(f"🗄️ Résultats depuis le cache: {search_type}")
            return self.cache[cache_key][1]
        
        # Choisir le CSE selon le type
        if search_type == "oniam":
            cse_id = self.oniam_cse_id
        elif search_type == "jurisprudence":
            cse_id = self.jurisprudence_cse_id
        else:
            cse_id = self.jurisprudence_cse_id  # CSE par défaut
        
        # Effectuer la recherche
        try:
            results = self._perform_search(query, cse_id, max_results, search_type)
            
            # Mettre en cache
            self.cache[cache_key] = (time.time(), results)
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur recherche {search_type}: {e}")
            return []
    
    def _perform_search(self, query: str, cse_id: str, max_results: int, search_type: str) -> List[Dict]:
        """Effectue une recherche Google"""
        # Respecter le rate limit
        self._respect_rate_limit()
        
        # Obtenir la clé API suivante
        api_key = self._get_next_api_key()
        
        # Nettoyer la requête
        clean_query = self._clean_query(query)
        
        # Paramètres de recherche
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': clean_query,
            'num': min(10, max_results),
            'dateRestrict': 'y2',
            'lr': 'lang_fr',
            'gl': 'fr',
            'fields': 'items(title,link,snippet)'
        }
        
        # Effectuer la requête
        response = requests.get(self.base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
        
            # Formater les résultats
            formatted_results = []
            for i, item in enumerate(items):
                formatted_result = {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': self._extract_source(item.get('link', '')),
                    'date': '2024-01-01',
                    'relevance_score': 0.9 - (i * 0.1),
                    'search_type': search_type,
                    'position': i + 1
                }
                formatted_results.append(formatted_result)
            
            print(f"🔍 Recherche {search_type}: {len(formatted_results)} résultats")
            return formatted_results
            
        elif response.status_code == 429:
            print(f"⚠️ Quota dépassé pour cette clé API - Rotation automatique")
            # Essayer avec la clé suivante
            return self._perform_search(query, cse_id, max_results, search_type)
            
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return []
    
    def search_jurisprudence(self, query: str, max_results: int = 10) -> List[Dict]:
        """Recherche jurisprudence avec CSE dédié"""
        print(f"⚖️ Recherche jurisprudence avec CSE: {self.jurisprudence_cse_id}")
        return self.search(query, "jurisprudence", max_results)
    
    def search_oniam(self, query: str, max_results: int = 10) -> List[Dict]:
        """Recherche ONIAM avec CSE dédié"""
        print(f"🏥 Recherche ONIAM avec CSE: {self.oniam_cse_id}")
        return self.search(query, "oniam", max_results)
    
    def search_medical_legal(self, query: str, max_results: int = 10) -> List[Dict]:
        """Recherche médico-légale combinée"""
        results = []
        
        # Recherche jurisprudence
        jur_results = self.search_jurisprudence(f"jurisprudence {query}", max_results//2)
        results.extend(jur_results)
        
        # Recherche ONIAM
        oniam_results = self.search_oniam(query, max_results//2)
        results.extend(oniam_results)
        
        return results[:max_results]
    
    def _respect_rate_limit(self):
        """Respecte le rate limit"""
        current_time = time.time()
        if current_time - self.last_request_time < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay)
        self.last_request_time = current_time
    
    def _clean_query(self, query: str) -> str:
        """Nettoie et tronque la requête"""
        # Supprimer les caractères spéciaux
        clean = query.strip()
        
        # Tronquer si trop long
        if len(clean) > 100:
            clean = clean[:100]
        
        return clean
    
    def _extract_source(self, url: str) -> str:
        """Extrait la source depuis l'URL"""
        if not url:
            return "Inconnu"
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if 'oniam.fr' in domain:
                return 'ONIAM'
            elif 'legifrance.gouv.fr' in domain:
                return 'Legifrance'
            elif 'courdecassation.fr' in domain:
                return 'Cour de Cassation'
            elif 'dalloz.fr' in domain:
                return 'Dalloz'
            else:
                return domain
        except:
            return "Inconnu"
    
    def get_quota_status(self) -> Dict:
        """Retourne le statut du quota"""
        return {
            'daily_quota': self.daily_quota,
            'requests_made': self.requests_made,
            'requests_remaining': self.daily_quota - self.requests_made,
            'percentage_used': (self.requests_made / self.daily_quota) * 100
        }

def test_google_search():
    """Test du module Google Search"""
    api = GoogleSearchAPI()
        
        # Test recherche jurisprudence
    print("\n🔍 Test recherche jurisprudence:")
    results = api.search_jurisprudence("responsabilité médicale", 3)
    for result in results:
        print(f"  - {result['title']}")
        
        # Test recherche ONIAM
    print("\n🏥 Test recherche ONIAM:")
    results = api.search_oniam("accident médical", 3)
    for result in results:
        print(f"  - {result['title']}")
    
    # Test statut quota
    print("\n📊 Statut quota:")
    status = api.get_quota_status()
    print(f"  Quota quotidien: {status['daily_quota']}")
    print(f"  Requêtes effectuées: {status['requests_made']}")
    print(f"  Requêtes restantes: {status['requests_remaining']}")
    print(f"  Pourcentage utilisé: {status['percentage_used']:.1f}%")

if __name__ == "__main__":
    test_google_search() 