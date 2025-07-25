#!/usr/bin/env python3
"""
Module de traitement de nouveaux documents pour LegalDocBot
Permet d'ajouter de nouveaux PDFs à la base de connaissances ChromaDB
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional
import chromadb
from chromadb.config import Settings
import PyPDF2
import fitz  # PyMuPDF

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processeur de documents pour ajouter de nouveaux PDFs à ChromaDB"""
    
    def __init__(self, chroma_db_path: str = "chroma_db"):
        self.chroma_db_path = Path(chroma_db_path)
        self.knowledge_base_path = Path("knowledge base")
        
        # Créer les dossiers si nécessaire
        self.knowledge_base_path.mkdir(exist_ok=True)
        
        # Initialiser ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.chroma_db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Collection pour les documents
        self.collection = self.client.get_or_create_collection(
            name="legal_documents",
            metadata={"description": "Base de connaissances juridique"}
        )
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extrait le texte d'un fichier PDF"""
        try:
            # Essayer PyMuPDF d'abord (plus robuste)
            doc = fitz.open(str(pdf_path))
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
            
        except ImportError:
            # Fallback vers PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    return text.strip()
            except Exception as e:
                logger.error(f"Erreur extraction PDF {pdf_path}: {e}")
                return ""
    
    def process_single_document(self, pdf_path: Path) -> bool:
        """Traite un seul document PDF"""
        try:
            logger.info(f"📄 Traitement de {pdf_path.name}...")
            
            # Extraire le texte
            text = self.extract_text_from_pdf(pdf_path)
            if not text:
                logger.warning(f"⚠️ Aucun texte extrait de {pdf_path.name}")
                return False
            
            # Découper en chunks
            chunks = self._split_text_into_chunks(text, chunk_size=1000, overlap=200)
            
            # Ajouter à ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                doc_id = f"{pdf_path.stem}_{i}"
                documents.append(chunk)
                metadatas.append({
                    "source": pdf_path.name,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "file_path": str(pdf_path)
                })
                ids.append(doc_id)
            
            # Insérer dans ChromaDB
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"✅ {pdf_path.name} traité: {len(chunks)} chunks ajoutés")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement {pdf_path.name}: {e}")
            return False
    
    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Découpe le texte en chunks avec overlap"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Ajuster la fin pour ne pas couper au milieu d'un mot
            if end < len(text):
                # Chercher le dernier espace dans la fenêtre
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Avancer avec overlap
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def process_knowledge_base(self) -> dict:
        """Traite tous les PDFs dans le dossier knowledge base"""
        logger.info("📚 Traitement de la base de connaissances...")
        
        if not self.knowledge_base_path.exists():
            logger.warning("⚠️ Dossier 'knowledge base' non trouvé")
            return {"success": 0, "failed": 0, "total": 0}
        
        # Trouver tous les PDFs
        pdf_files = list(self.knowledge_base_path.glob("*.pdf"))
        
        if not pdf_files:
            logger.info("ℹ️ Aucun fichier PDF trouvé dans 'knowledge base'")
            return {"success": 0, "failed": 0, "total": 0}
        
        logger.info(f"📄 {len(pdf_files)} fichiers PDF trouvés")
        
        success_count = 0
        failed_count = 0
        
        for pdf_file in pdf_files:
            if self.process_single_document(pdf_file):
                success_count += 1
            else:
                failed_count += 1
        
        # Statistiques
        stats = {
            "success": success_count,
            "failed": failed_count,
            "total": len(pdf_files)
        }
        
        logger.info(f"📊 Résultats: {success_count} succès, {failed_count} échecs sur {len(pdf_files)} fichiers")
        
        return stats
    
    def add_new_document(self, pdf_path: str) -> bool:
        """Ajoute un nouveau document PDF"""
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            logger.error(f"❌ Fichier non trouvé: {pdf_path}")
            return False
        
        if pdf_path.suffix.lower() != '.pdf':
            logger.error(f"❌ Fichier non PDF: {pdf_path}")
            return False
        
        # Copier dans knowledge base
        dest_path = self.knowledge_base_path / pdf_path.name
        try:
            import shutil
            shutil.copy2(pdf_path, dest_path)
            logger.info(f"📋 {pdf_path.name} copié dans knowledge base")
        except Exception as e:
            logger.error(f"❌ Erreur copie: {e}")
            return False
        
        # Traiter le document
        return self.process_single_document(dest_path)
    
    def get_collection_stats(self) -> dict:
        """Retourne les statistiques de la collection ChromaDB"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection.name,
                "chroma_db_path": str(self.chroma_db_path)
            }
        except Exception as e:
            logger.error(f"❌ Erreur statistiques: {e}")
            return {}

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_document_processor() -> DocumentProcessor:
    """Retourne une instance du processeur de documents"""
    return DocumentProcessor()

def process_new_documents() -> dict:
    """Traite tous les nouveaux documents dans knowledge base"""
    processor = get_document_processor()
    return processor.process_knowledge_base()

def add_document(pdf_path: str) -> bool:
    """Ajoute un nouveau document PDF"""
    processor = get_document_processor()
    return processor.add_new_document(pdf_path)

def get_database_stats() -> dict:
    """Retourne les statistiques de la base de données"""
    processor = get_document_processor()
    return processor.get_collection_stats()

# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("🧪 TEST PROCESSEUR DE DOCUMENTS")
    print("=" * 50)
    
    processor = DocumentProcessor()
    
    # Statistiques actuelles
    stats = processor.get_collection_stats()
    print(f"\n📊 Statistiques ChromaDB:")
    print(f"  Documents: {stats.get('total_documents', 0)}")
    print(f"  Collection: {stats.get('collection_name', 'N/A')}")
    
    # Traiter les nouveaux documents
    print(f"\n📚 Traitement des nouveaux documents...")
    results = processor.process_knowledge_base()
    
    print(f"\n📈 Résultats:")
    print(f"  Succès: {results['success']}")
    print(f"  Échecs: {results['failed']}")
    print(f"  Total: {results['total']}")
    
    # Nouvelles statistiques
    new_stats = processor.get_collection_stats()
    print(f"\n📊 Nouvelles statistiques:")
    print(f"  Documents: {new_stats.get('total_documents', 0)}")
    
    if results['success'] > 0:
        print(f"✅ {results['success']} documents ajoutés avec succès")
    else:
        print(f"ℹ️ Aucun nouveau document traité") 