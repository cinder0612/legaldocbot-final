#!/usr/bin/env python3
"""
Gestionnaire de téléchargement automatique pour LegalDocBot
Télécharge les gros fichiers depuis Hugging Face
"""

import os
import sys
import requests
import zipfile
import shutil
from pathlib import Path
from typing import Optional, Dict, List
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DownloadManager:
    """Gestionnaire de téléchargement des ressources externes"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.models_dir = self.base_dir / "models"
        self.chroma_dir = self.base_dir / "chroma_db"
        self.knowledge_dir = self.base_dir / "knowledge base"
        
        # Créer les dossiers s'ils n'existent pas
        self.data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
        # URLs des ressources (à configurer selon vos fichiers)
        self.resources = {
            "chroma_db": {
                "url": "https://huggingface.co/datasets/cinder06/legalbot-chromadb/resolve/main/legalbot.zip",
                "type": "direct_download",
                "local_path": self.chroma_dir,
                "description": "Base de données ChromaDB avec embeddings (OBLIGATOIRE)"
            },
            "knowledge_base": {
                "url": "https://huggingface.co/datasets/cinder06/legalbot-knowledge/resolve/main/knowledge.zip",
                "type": "direct_download", 
                "local_path": self.knowledge_dir,
                "description": "Documents PDF source (OPTIONNEL - pour ajout de nouveaux documents)",
                "optional": True
            },
            "models": {
                "url": "https://huggingface.co/datasets/cinder06/legalbot-models/resolve/main/models.zip",
                "type": "direct_download",
                "local_path": self.models_dir,
                "description": "Modèles de machine learning (OPTIONNEL)",
                "optional": True
            }
        }
    
    def check_resources(self) -> Dict[str, bool]:
        """Vérifie quelles ressources sont disponibles localement"""
        status = {}
        
        for resource_name, config in self.resources.items():
            local_path = config["local_path"]
            is_optional = config.get("optional", False)
            
            if local_path.exists() and any(local_path.iterdir()):
                status[resource_name] = True
                logger.info(f"✅ {resource_name}: Disponible localement")
            else:
                status[resource_name] = False
                if is_optional:
                    logger.info(f"ℹ️ {resource_name}: Non disponible (optionnel)")
                else:
                    logger.warning(f"❌ {resource_name}: Non disponible (obligatoire)")
        
        return status
    
    def download_from_http(self, url: str, local_path: Path, description: str) -> bool:
        """Télécharge depuis une URL HTTP directe"""
        try:
            logger.info(f"📥 Téléchargement {description} depuis HTTP...")
            
            # Créer le dossier de destination
            local_path.mkdir(parents=True, exist_ok=True)
            
            # Télécharger le fichier ZIP
            zip_path = local_path / "temp_download.zip"
            
            # Headers pour simuler un navigateur
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Télécharger avec requests
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            
            # Sauvegarder le fichier ZIP
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extraire le ZIP
            logger.info(f"📦 Extraction du fichier ZIP...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(local_path)
            
            # Supprimer le fichier ZIP temporaire
            zip_path.unlink()
            
            logger.info(f"✅ {description} téléchargé et extrait avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur téléchargement HTTP: {e}")
            # Nettoyer en cas d'erreur
            if zip_path.exists():
                zip_path.unlink()
            return False
    
    def download_resource(self, resource_name: str) -> bool:
        """Télécharge une ressource spécifique"""
        if resource_name not in self.resources:
            logger.error(f"❌ Ressource '{resource_name}' non trouvée")
            return False
        
        config = self.resources[resource_name]
        local_path = config["local_path"]
        
        # Créer le dossier de destination
        local_path.mkdir(parents=True, exist_ok=True)
        
        if config["type"] == "direct_download":
            return self.download_from_http(
                config["url"],
                local_path,
                config["description"]
            )
        else:
            logger.error(f"❌ Type de ressource non supporté: {config['type']}")
            return False
    
    def download_all_missing(self) -> Dict[str, bool]:
        """Télécharge toutes les ressources manquantes"""
        logger.info("🔍 Vérification des ressources...")
        status = self.check_resources()
        
        results = {}
        for resource_name, is_available in status.items():
            if not is_available:
                config = self.resources[resource_name]
                is_optional = config.get("optional", False)
                
                if is_optional:
                    logger.info(f"ℹ️ {resource_name}: Ressource optionnelle non téléchargée")
                    results[resource_name] = True  # Pas d'erreur pour les ressources optionnelles
                else:
                    logger.info(f"📥 Téléchargement de {resource_name} (obligatoire)...")
                    results[resource_name] = self.download_resource(resource_name)
            else:
                results[resource_name] = True
        
        return results
    
    def setup_environment(self) -> bool:
        """Configure l'environnement complet"""
        logger.info("🚀 Configuration de l'environnement LegalDocBot...")
        
        # Vérifier les ressources
        missing_resources = self.download_all_missing()
        
        # Vérifier le succès (seulement les ressources obligatoires)
        required_resources = [name for name, config in self.resources.items() 
                            if not config.get("optional", False)]
        required_success = all(missing_resources.get(name, True) for name in required_resources)
        
        if required_success:
            logger.info("✅ Environnement configuré avec succès")
            
            # Afficher le statut des ressources optionnelles
            optional_resources = [name for name, config in self.resources.items() 
                                if config.get("optional", False)]
            if optional_resources:
                logger.info("📋 Ressources optionnelles:")
                for resource in optional_resources:
                    status = "✅ Disponible" if missing_resources.get(resource, False) else "ℹ️ Non disponible"
                    logger.info(f"  - {resource}: {status}")
        else:
            failed = [name for name in required_resources if not missing_resources.get(name, True)]
            logger.error(f"❌ Échec du téléchargement des ressources obligatoires: {', '.join(failed)}")
        
        return required_success

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_download_manager() -> DownloadManager:
    """Retourne une instance du gestionnaire de téléchargement"""
    return DownloadManager()

def check_and_download_resources() -> bool:
    """Vérifie et télécharge les ressources si nécessaire"""
    manager = get_download_manager()
    return manager.setup_environment()

def get_resource_status() -> Dict[str, bool]:
    """Retourne le statut des ressources"""
    manager = get_download_manager()
    return manager.check_resources()

def test_huggingface_download():
    """Test du téléchargement depuis Hugging Face"""
    print("🧪 Test du téléchargement Hugging Face...")
    
    manager = DownloadManager()
    
    # Test spécifique pour le dataset ChromaDB
    url = "https://huggingface.co/datasets/cinder06/legalbot-chromadb/resolve/main/legalbot.zip"
    print(f"📥 Test téléchargement: {url}")
    
    success = manager.download_from_http(
        url,
        manager.chroma_dir,
        "Base de données ChromaDB de test"
    )
    
    if success:
        print("✅ Téléchargement réussi !")
        
        # Vérifier le contenu
        if manager.chroma_dir.exists():
            files = list(manager.chroma_dir.iterdir())
            print(f"📁 Fichiers téléchargés: {len(files)}")
            for file in files[:5]:  # Afficher les 5 premiers
                print(f"  - {file.name}")
    else:
        print("❌ Échec du téléchargement")

if __name__ == "__main__":
    test_huggingface_download() 
