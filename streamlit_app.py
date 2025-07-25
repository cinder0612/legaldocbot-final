#!/usr/bin/env python3
"""
LegalDocBot - Application Streamlit pour déploiement
Base ChromaDB téléchargée automatiquement depuis Hugging Face
"""

import streamlit as st
import os
import time
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de la page
st.set_page_config(
    page_title="⚖️ LegalDocBot - Expert Médico-Légal",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
/* Header Premium */
.premium-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

/* Cards avec effet glassmorphism */
.glass-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* Content cards */
.content-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 2rem;
    margin-bottom: 2rem;
}

/* Analysis result card */
.analysis-result-card {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(15px);
    border-radius: 15px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 2rem;
    margin-top: 2rem;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

/* KPI Cards */
.kpi-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 1.5rem;
    text-align: center;
    margin-bottom: 1rem;
}

.kpi-number {
    font-size: 2rem;
    font-weight: bold;
    color: #ffffff;
    margin: 0;
}

.kpi-label {
    font-size: 0.9rem;
    color: #e0e0e0;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Grand bouton Analyser */
.expert-btn-line {
    display: flex;
    justify-content: center;
    margin-bottom: 1rem;
}

.expert-btn-line button {
    font-size: 1.5rem !important;
    padding: 1.2rem 3rem !important;
    min-width: 280px !important;
    height: auto !important;
    border-radius: 15px !important;
    font-weight: 700 !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2) !important;
    transition: all 0.3s ease !important;
    letter-spacing: 1px !important;
}

.expert-btn-line button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3) !important;
}

/* Analysis content styling */
.analysis-content {
    color: #000000 !important;
    font-size: 1.1em;
    line-height: 1.8;
    background: rgba(255, 255, 255, 0.95) !important;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid rgba(0, 0, 0, 0.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    font-weight: 500;
}

.analysis-content * {
    color: #000000 !important;
}

.analysis-content h1, .analysis-content h2, .analysis-content h3, 
.analysis-content h4, .analysis-content h5, .analysis-content h6 {
    color: #1a1a1a !important;
    font-weight: 700;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}

.analysis-content p {
    color: #000000 !important;
    margin-bottom: 1rem;
}

.analysis-content strong, .analysis-content b {
    color: #000000 !important;
    font-weight: 700;
}

.analysis-content ul, .analysis-content ol {
    color: #000000 !important;
    margin-left: 1.5rem;
}

.analysis-content li {
    color: #000000 !important;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

def load_dotenv():
    """Charge les variables d'environnement depuis .env si disponible"""
    try:
        from dotenv import load_dotenv as load_env
        load_env()
    except ImportError:
        pass

def setup_environment():
    """Configure l'environnement et télécharge les ressources"""
    print("🚀 Configuration de l'environnement LegalDocBot...")
    
    # Configuration des secrets Streamlit
    if hasattr(st, 'secrets'):
        print("🔐 Configuration des secrets Streamlit...")
        
        # Clé API Grok-4
        if 'XAI_API_KEY' in st.secrets:
            os.environ['XAI_API_KEY'] = st.secrets['XAI_API_KEY']
            print("✅ Clé API Grok-4 configurée")
        else:
            print("⚠️ Clé API Grok-4 manquante dans les secrets")
            
        # Clé API Google
        if 'GOOGLE_API_KEY' in st.secrets:
            os.environ['GOOGLE_API_KEY'] = st.secrets['GOOGLE_API_KEY']
            print("✅ Clé API Google configurée")
        else:
            print("⚠️ Clé API Google manquante dans les secrets")
            
        # CSE ID ONIAM
        if 'ONIAM_CSE_ID' in st.secrets:
            os.environ['ONIAM_CSE_ID'] = st.secrets['ONIAM_CSE_ID']
            print("✅ CSE ID ONIAM configuré")
        else:
            print("⚠️ CSE ID ONIAM manquant dans les secrets")
            
        # Token Hugging Face
        if 'HUGGINGFACE_TOKEN' in st.secrets:
            os.environ['HUGGINGFACE_TOKEN'] = st.secrets['HUGGINGFACE_TOKEN']
            print("✅ Token Hugging Face configuré")
        else:
            print("⚠️ Token Hugging Face manquant dans les secrets")
    else:
        print("ℹ️ Mode local - utilisation des variables d'environnement")

    # Vérification et téléchargement des ressources
    try:
        from download_manager import check_and_download_resources, get_resource_status
        print("🔍 Vérification des ressources...")
        resource_status = get_resource_status()
        
        if not all(resource_status.values()):
            print("📥 Téléchargement des ressources manquantes...")
            success = check_and_download_resources()
            if success:
                print("✅ Toutes les ressources téléchargées")
            else:
                print("⚠️ Certaines ressources n'ont pas pu être téléchargées")
        else:
            print("✅ Toutes les ressources sont disponibles")
            
    except ImportError:
        print("⚠️ Module de téléchargement non disponible")
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification des ressources: {e}")

def get_chromadb_search():
    """Récupère l'instance de recherche ChromaDB"""
    try:
        from chromadb_search import get_chromadb_search
        return get_chromadb_search()
    except ImportError:
        print("⚠️ Module ChromaDB non disponible")
        return None

def get_grok_client():
    """Récupère le client Grok-4"""
    try:
        from grok_client import get_grok_client
        return get_grok_client()
    except ImportError:
        print("⚠️ Module Grok-4 non disponible")
        return None

def run_analysis(situation, mode="hybrid", fast_mode=False):
    """Exécute l'analyse avec Grok-4 et ChromaDB"""
    try:
        print("🧠 Démarrage de l'analyse...")
        
        # Récupérer les modules
        chromadb_search = get_chromadb_search()
        grok_client = get_grok_client()
        
        if not grok_client or not grok_client.is_configured():
            return "❌ Erreur : Client Grok-4 non configuré. Vérifiez votre clé API XAI_API_KEY"
        
        # Recherche dans ChromaDB
        chroma_results = []
        if chromadb_search and chromadb_search.is_available:
            print("🔍 Recherche dans la base ChromaDB...")
            chroma_results = chromadb_search.search_unified_legal_knowledge(situation, top_k=10)
            print(f"✅ {len(chroma_results)} résultats ChromaDB trouvés")
        
        # Construction du contexte enrichi
        context = f"""
SITUATION À ANALYSER :
{situation}

CONTEXTE JURIDIQUE (si disponible) :
"""
        
        if chroma_results:
            context += "\n".join([f"- {result.get('content', '')[:200]}..." for result in chroma_results[:5]])
        else:
            context += "Aucune information juridique spécifique disponible."
        
        # Prompt d'analyse
        prompt = f"""
{context}

INSTRUCTIONS POUR L'ANALYSE JURIDIQUE :

Analysez cette situation médicale ou juridique en fournissant :

1. **QUALIFICATION JURIDIQUE** : Identifiez les enjeux juridiques principaux
2. **FONDEMENTS LÉGAUX** : Citez les articles de loi pertinents (CSP, Code civil, etc.)
3. **RECOURS POSSIBLES** : Détaillez les voies de recours disponibles
4. **RECOMMANDATIONS** : Conseils pratiques pour la suite

Format de réponse structuré et professionnel.
"""
        
        # Génération avec Grok-4
        print("🧠 Génération avec Grok-4...")
        if fast_mode:
            result = grok_client.generate_fast_analysis(prompt)
        else:
            result = grok_client.generate_detailed_analysis(prompt)
        
        return result
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        return f"❌ Erreur lors de l'analyse: {str(e)}"

def main():
    """Fonction principale de l'application"""
    
    # Configuration de l'environnement
    load_dotenv()
    setup_environment()
    
    # --- HEADER ---
    st.markdown("""
    <div class="premium-header">
        <h1>⚖️ LegalDocBot</h1>
        <h3>Analyse Médicale & Juridique d'Expert avec Grok-4</h3>
        <p style="font-size: 1rem; color: #A0AEC0; margin-top: 0.5rem;">
            Analyse neutre et objective • Recours ONIAM sans faute • Conseils équilibrés • Powered by Grok-4
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- KPI METRICS ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="kpi-card"><p class="kpi-number">⚡</p><p class="kpi-label">Rapide</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="kpi-card"><p class="kpi-number">🎯</p><p class="kpi-label">Précis</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="kpi-card"><p class="kpi-number">🔒</p><p class="kpi-label">Sécurisé</p></div>', unsafe_allow_html=True)
    
    # --- TABS FOR MAIN CONTENT ---
    tab1, tab2, tab3 = st.tabs(["🔍 Analyse", "📝 Lettres", "💰 Indemnisation"])
    
    with tab1:
        # --- DISPLAY THE INPUT FORM ---
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.subheader("Nouvelle Analyse Juridique avec Grok-4")
        st.info("💡 **Analyse neutre et objective** : Notre système présente tous les points de vue et recours possibles, y compris les voies ONIAM sans faute médicale. Powered by Grok-4.")
        
        # --- SECTION 1: INPUT PRINCIPAL ---
        situation = st.text_area(
            "📝 Décrivez votre situation médicale ou juridique :",
            height=150,
            placeholder="Exemple : Un patient a subi une erreur médicale lors d'une intervention chirurgicale. Quels sont ses droits et les recours possibles ?"
        )
        
        # --- SECTION 2: CONTRÔLES PRINCIPAUX ---
        st.markdown("### ⚙️ Configuration de l'Analyse")
        
        # Bouton Analyser
        st.markdown('<div class="expert-btn-line">', unsafe_allow_html=True)
        analyze_button = st.button(
            "🧠 Analyser",
            type="primary",
            help="Lancer l'analyse juridique avec Grok-4"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Options
        col1, col2 = st.columns(2)
        with col1:
            mode = st.selectbox(
                "🎯 Mode d'Analyse",
                ["hybrid", "grok", "chromadb_rag"],
                format_func=lambda x: {
                    "hybrid": "🤖 Hybride (Grok-4 + ChromaDB)",
                    "grok": "🧠 Grok-4 (Expert)",
                    "chromadb_rag": "⚖️ ChromaDB RAG"
                }[x]
            )
        
        with col2:
            fast_mode = st.checkbox("⚡ Mode Rapide")
        
        # --- VALIDATION ---
        if analyze_button and not situation.strip():
            st.warning("⚠️ Veuillez décrire une situation à analyser.")
        
        # --- LOGIQUE D'ANALYSE ---
        if analyze_button and situation.strip():
            # Spinner pour montrer que l'analyse est en cours
            with st.spinner("🧠 Grok-4 en action... Analyse juridique en cours..."):
                # Mesurer le temps
                start_time = time.time()
                
                # Exécuter l'analyse
                analysis_result = run_analysis(situation, mode, fast_mode)
                
                # Calculer le temps
                analysis_time = time.time() - start_time
                
                # Sauvegarder dans session state
                st.session_state.analysis_result = analysis_result
                st.session_state.analysis_time = analysis_time
                st.session_state.situation = situation
        
        # --- AFFICHAGE DES RÉSULTATS ---
        if hasattr(st.session_state, 'analysis_result') and st.session_state.analysis_result:
            st.markdown("<div class='analysis-result-card'>", unsafe_allow_html=True)
            
            # Métriques
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("⏱️ Temps d'analyse", f"{st.session_state.analysis_time:.1f}s")
            with col2:
                st.metric("🎯 Mode utilisé", mode)
            with col3:
                st.metric("📝 Longueur", f"{len(st.session_state.analysis_result)} caractères")
            
            # Résultat
            st.subheader("📋 Résultat de l'Analyse")
            st.markdown(f"""
            <div class="analysis-content">
            {st.session_state.analysis_result}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.subheader("📝 Générateur de Lettres")
        st.info("Fonctionnalité en cours de développement...")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.subheader("💰 Calculateur d'Indemnisation")
        st.info("Fonctionnalité en cours de développement...")
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 