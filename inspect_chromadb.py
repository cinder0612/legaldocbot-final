#!/usr/bin/env python3
"""
Inspecteur de base ChromaDB pour LegalDocBot
Vérifie le contenu et l'état de la base de données
"""

import chromadb
from pathlib import Path
import os

def inspect_chromadb():
    """Inspecte le contenu de la base ChromaDB"""
    
    print("🔍 INSPECTION DE LA BASE CHROMADB")
    print("=" * 50)
    
    # Vérifier si le dossier existe
    chroma_path = Path("chroma_db")
    if not chroma_path.exists():
        print("❌ Dossier chroma_db n'existe pas")
        return
    
    print(f"✅ Dossier chroma_db trouvé: {chroma_path}")
    
    # Lister les fichiers
    print("\n📁 Contenu du dossier chroma_db:")
    for file in chroma_path.iterdir():
        size = file.stat().st_size / 1024  # Taille en KB
        print(f"  📄 {file.name} ({size:.1f} KB)")
    
    # Tenter la connexion
    try:
        print("\n🔌 Test de connexion ChromaDB...")
        client = chromadb.PersistentClient(path='chroma_db')
        print("✅ Connexion ChromaDB réussie")
        
        # Lister les collections
        print("\n📚 Collections disponibles:")
        collections = client.list_collections()
        
        if not collections:
            print("  ⚠️ Aucune collection trouvée")
        else:
            for collection in collections:
                print(f"  📖 {collection.name}")
                print(f"    - Nombre de documents: {collection.count()}")
                
                # Afficher quelques métadonnées si disponibles
                try:
                    results = collection.peek(limit=1)
                    if results['metadatas'] and results['metadatas'][0]:
                        metadata = results['metadatas'][0]
                        print(f"    - Métadonnées: {list(metadata.keys())}")
                except Exception as e:
                    print(f"    - Erreur lecture métadonnées: {e}")
        
        # Vérifier les collections attendues
        expected_collections = [
            'deontologie',
            'csp_legislation', 
            'css_legislation',
            'penal_legislation',
            'civil_legislation'
        ]
        
        print(f"\n🎯 Collections attendues vs disponibles:")
        available_names = [c.name for c in collections]
        
        for expected in expected_collections:
            if expected in available_names:
                print(f"  ✅ {expected}")
            else:
                print(f"  ❌ {expected} (manquante)")
        
        if not collections:
            print("\n🚨 VOTRE BASE CHROMADB EST VIDE !")
            print("💡 Solutions possibles:")
            print("   1. Télécharger une base pré-embeddée")
            print("   2. Créer une nouvelle base avec vos documents")
            print("   3. Utiliser l'application sans ChromaDB")
        
    except Exception as e:
        print(f"❌ Erreur connexion ChromaDB: {e}")

if __name__ == "__main__":
    inspect_chromadb() 