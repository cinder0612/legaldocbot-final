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
        self.data_dir   = self.base_dir / "data"
        self.models_dir = self.base_dir / "models"
        self.chroma_dir = self.base_dir / "chroma_db"
        self.knowledge_dir = self.base_dir / "knowledge_base"

        # Créer les dossiers s'ils n'existent pas
        self.data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)

        # URLs réelles
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
                "description": "Documents PDF source (OPTIONNEL)",
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

    # ------------------------------------------------------------------
    # Méthodes internes
    # ------------------------------------------------------------------
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
            local_path.mkdir(parents=True, exist_ok=True)

            zip_path = local_path / "temp_download.zip"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            with requests.get(url, headers=headers, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(zip_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(local_path)

            zip_path.unlink()
            logger.info(f"✅ {description} téléchargé et extrait avec succès")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur téléchargement HTTP: {e}")
            if zip_path.exists():
                zip_path.unlink()
            return False

    def download_resource(self, resource_name: str) -> bool:
        """Télécharge une ressource spécifique"""
        if resource_name not in self.resources:
            logger.error(f"❌ Ressource '{resource_name}' inconnue")
            return False

        config = self.resources[resource_name]
        return self.download_from_http(
            config["url"],
            config["local_path"],
            config["description"]
        )

    def download_all_missing(self) -> Dict[str, bool]:
        """Télécharge toutes les ressources manquantes"""
        logger.info("🔍 Vérification des ressources...")
        status = self.check_resources()
        results = {}

        for name, ok in status.items():
            if ok:
                results[name] = True
                continue

            cfg = self.resources[name]
            if cfg.get("optional", False):
                logger.info(f"ℹ️ {name}: optionnel, ignoré")
                results[name] = True
            else:
                logger.info(f"📥 Téléchargement de {name} (obligatoire)...")
                results[name] = self.download_resource(name)
        return results

    def setup_environment(self) -> bool:
        """Configure l’environnement complet"""
        logger.info("🚀 Configuration de l’environnement LegalDocBot...")
        results = self.download_all_missing()

        required = [n for n, c in self.resources.items() if not c.get("optional", False)]
        ok = all(results[n] for n in required)

        if ok:
            logger.info("✅ Environnement prêt")
        else:
            failed = [n for n in required if not results[n]]
            logger.error(f"❌ Échec téléchargement ressources obligatoires: {', '.join(failed)}")
        return ok

# ------------------------------------------------------------------
# Fonctions utilitaires
# ------------------------------------------------------------------
def get_download_manager() -> DownloadManager:
    return DownloadManager()

def check_and_download_resources() -> bool:
    return get_download_manager().setup_environment()

def get_resource_status() -> Dict[str, bool]:
    return get_download_manager().check_resources()

def test_huggingface_download():
    print("🧪 Test téléchargement...")
    dm = DownloadManager()
    ok = dm.download_from_http(
        "https://huggingface.co/datasets/cinder06/legalbot-chromadb/resolve/main/legalbot.zip",
        dm.chroma_dir,
        "ChromaDB test"
    )
    print("✅ OK" if ok else "❌ Échec")

if __name__ == "__main__":
    test_huggingface_download()
