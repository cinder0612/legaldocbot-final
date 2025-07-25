#!/usr/bin/env python3
"""
Script de préparation pour le déploiement Streamlit Cloud
Nettoie le repository et vérifie la configuration
"""

import os
import shutil
from pathlib import Path

def prepare_deployment():
    """Prépare le repository pour le déploiement Streamlit Cloud"""
    
    print("🚀 PRÉPARATION DÉPLOIEMENT STREAMLIT CLOUD")
    print("=" * 50)
    
    # Fichiers/dossiers à supprimer pour le déploiement
    items_to_remove = [
        "chroma_db/",
        "__pycache__/",
        ".env",
        "*.pyc",
        "*.pyo",
        "*.pyd"
    ]
    
    print("🧹 Nettoyage du repository...")
    
    for item in items_to_remove:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
                print(f"✅ Dossier supprimé: {item}")
            else:
                os.remove(item)
                print(f"✅ Fichier supprimé: {item}")
        else:
            print(f"ℹ️ Non trouvé: {item}")
    
    # Vérifier les fichiers requis
    required_files = [
        "medical_legal_bot_grok.py",
        "requirements.txt",
        "download_manager.py",
        "chromadb_search.py",
        "grok_client.py",
        "ui_utils.py",
        ".gitignore"
    ]
    
    print("\n📋 Vérification des fichiers requis...")
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ MANQUANT: {file}")
    
    # Vérifier la configuration Hugging Face
    print("\n🔍 Vérification configuration Hugging Face...")
    
    try:
        with open("download_manager.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "cinder06/legalbot-chromadb" in content:
                print("✅ URL Hugging Face configurée")
            else:
                print("❌ URL Hugging Face manquante")
    except Exception as e:
        print(f"❌ Erreur lecture download_manager.py: {e}")
    
    # Vérifier .gitignore
    print("\n🔒 Vérification .gitignore...")
    
    try:
        with open(".gitignore", "r", encoding="utf-8") as f:
            content = f.read()
            if "chroma_db/" in content:
                print("✅ chroma_db/ exclu du git")
            else:
                print("❌ chroma_db/ non exclu du git")
            
            if ".env" in content:
                print("✅ .env exclu du git")
            else:
                print("❌ .env non exclu du git")
    except Exception as e:
        print(f"❌ Erreur lecture .gitignore: {e}")
    
    print("\n🎯 PROCHAINES ÉTAPES:")
    print("1. git add .")
    print("2. git commit -m '🚀 Déploiement Streamlit Cloud'")
    print("3. git push origin main")
    print("4. Configurer les secrets sur Streamlit Cloud")
    print("5. Déployer l'application")
    
    print("\n✅ Préparation terminée !")

if __name__ == "__main__":
    prepare_deployment() 