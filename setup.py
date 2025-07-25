#!/usr/bin/env python3
"""
Script de configuration pour LegalDocBot
Configure l'environnement et télécharge les ressources nécessaires
"""

import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Installe les dépendances Python"""
    print("📦 Installation des dépendances...")
    
    requirements = [
        "streamlit",
        "requests",
        "python-dotenv",
        "chromadb",
        "sentence-transformers",
        "gdown",
        "huggingface_hub"
    ]
    
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installé")
        except subprocess.CalledProcessError:
            print(f"❌ Erreur installation {package}")

def create_env_template():
    """Crée un template de fichier .env"""
    env_template = """# Configuration LegalDocBot
# Copiez ce fichier en .env et remplissez vos clés API

# Google Search API
GOOGLE_API_KEY=votre_cle_google_api_ici
ONIAM_CSE_ID=votre_cse_oniam_ici

# X.AI API (Grok-4)
XAI_API_KEY=votre_cle_xai_api_ici

# Kimi API (optionnel)
KIMI_API_KEY=votre_cle_kimi_api_ici

# Configuration des ressources
CHROMA_DB_URL=https://drive.google.com/uc?id=VOTRE_ID_CHROMA
KNOWLEDGE_BASE_URL=https://drive.google.com/uc?id=VOTRE_ID_KNOWLEDGE
MODELS_REPO_ID=VOTRE_USER/legalbot-models
"""
    
    env_path = Path(".env.template")
    if not env_path.exists():
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_template)
        print("✅ Template .env créé")
    else:
        print("ℹ️ Template .env existe déjà")

def setup_directories():
    """Crée les dossiers nécessaires"""
    directories = ["data", "models", "logs", "cache"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Dossier {directory} créé")

def main():
    """Configuration principale"""
    print("🚀 CONFIGURATION LEGALDOCBOT")
    print("=" * 50)
    
    # 1. Installer les dépendances
    install_requirements()
    
    # 2. Créer les dossiers
    setup_directories()
    
    # 3. Créer le template .env
    create_env_template()
    
    # 4. Vérifier les ressources
    try:
        from download_manager import get_resource_status
        status = get_resource_status()
        
        print(f"\n📊 Statut des ressources:")
        for resource, available in status.items():
            print(f"  {resource}: {'✅' if available else '❌'}")
        
        if not all(status.values()):
            print(f"\n⚠️ Certaines ressources ne sont pas disponibles")
            print("📝 Configurez les URLs dans download_manager.py")
            print("📝 Puis lancez: python download_manager.py")
        
    except ImportError:
        print("⚠️ Module de téléchargement non disponible")
    
    print(f"\n✅ Configuration terminée")
    print(f"📝 Prochaines étapes:")
    print(f"  1. Copiez .env.template en .env")
    print(f"  2. Remplissez vos clés API")
    print(f"  3. Configurez les URLs des ressources")
    print(f"  4. Lancez: streamlit run medical_legal_bot_grok.py")

if __name__ == "__main__":
    main() 