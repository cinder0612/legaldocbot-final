"""
LegalDocBot avec Grok-4
Version optimisée pour l'analyse juridique médicale avec Grok-4
"""

import os
import streamlit as st
import time
from dotenv import load_dotenv
import logging
from datetime import datetime

# Import des modules externalisés
from ui_utils import cached_analysis, create_performance_chart, create_mode_usage_chart, stream_analysis_result
from ui_utils import display_analysis_10
from letter_generator_module import display_letter_generator
from compensation_calculator import display_compensation_calculator
from timeline_generator import display_timeline_generator
from scenario_engine import display_scenario_engine
from analytics_module import analytics
from export_utils import export_to_pdf, compare_analyses
from config import API_CONFIG, RAG_CONFIG, UI_CONFIG
from grok_client import get_grok_client

# 🚀 INTÉGRATION GOOGLE SEARCH API
try:
    from google_search_module import GoogleSearchAPI
    GOOGLE_SEARCH_AVAILABLE = True
    print("✅ Module Google Search chargé pour jurisprudence et ONIAM")
except ImportError as e:
    GOOGLE_SEARCH_AVAILABLE = False
    print(f"⚠️ Module Google Search non disponible: {e}")

# 🗄️ INTÉGRATION CHROMADB
try:
    from chromadb_search import get_chromadb_search
    CHROMADB_AVAILABLE = True
    print("✅ Module ChromaDB chargé pour la base de connaissances")
except ImportError as e:
    CHROMADB_AVAILABLE = False
    print(f"⚠️ Module ChromaDB non disponible: {e}")

# Configuration du logging structuré
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s'
)

# Load environment variables from .env file or Streamlit secrets
load_dotenv()

# Configuration des secrets Streamlit Cloud
if hasattr(st, 'secrets'):
    print("🔐 Configuration des secrets Streamlit...")
    # Remplacer les variables d'environnement par les secrets Streamlit
    if 'XAI_API_KEY' in st.secrets:
        os.environ['XAI_API_KEY'] = st.secrets['XAI_API_KEY']
        print("✅ Clé API Grok-4 configurée")
    else:
        print("⚠️ Clé API Grok-4 manquante dans les secrets")
        
    if 'GOOGLE_API_KEY' in st.secrets:
        os.environ['GOOGLE_API_KEY'] = st.secrets['GOOGLE_API_KEY']
        print("✅ Clé API Google configurée")
    else:
        print("⚠️ Clé API Google manquante dans les secrets")
        
    if 'ONIAM_CSE_ID' in st.secrets:
        os.environ['ONIAM_CSE_ID'] = st.secrets['ONIAM_CSE_ID']
        print("✅ CSE ID ONIAM configuré")
    else:
        print("⚠️ CSE ID ONIAM manquant dans les secrets")
        
    if 'HUGGINGFACE_TOKEN' in st.secrets:
        os.environ['HUGGINGFACE_TOKEN'] = st.secrets['HUGGINGFACE_TOKEN']
        print("✅ Token Hugging Face configuré")
    else:
        print("⚠️ Token Hugging Face manquant dans les secrets")
else:
    print("ℹ️ Mode local - utilisation des variables d'environnement")

# 🚀 VÉRIFICATION ET TÉLÉCHARGEMENT DES RESSOURCES
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

def enrich_analysis_with_chromadb(query: str, analysis_type: str = "medical_legal") -> str:
    """
    Enrichit l'analyse avec la base de connaissances ChromaDB
    Utilise les 12,024 chunks de la base juridique
    """
    if not CHROMADB_AVAILABLE:
        return ""
    
    try:
        # Initialisation du système ChromaDB
        chromadb_search = get_chromadb_search()
        
        if not chromadb_search.is_available:
            return ""
        
        enriched_content = "\n\n## 📚 Base de Connaissances Juridique\n\n"
        enriched_content += "*Sources : Code de déontologie, CSP, CSS, Code pénal, Code civil*\n\n"
        
        # Recherche dans la base de connaissances
        print(f"🔍 Recherche ChromaDB: {query[:50]}...")
        
        # Recherche générale
        legal_results = chromadb_search.search_legal_knowledge(query, top_k=8)
        
        # Recherche spécifique déontologie
        deont_results = chromadb_search.search_deontologie(query, top_k=5)
        
        # Recherche CSP
        csp_results = chromadb_search.search_csp(query, top_k=5)
        
        print(f"📊 ChromaDB - Général: {len(legal_results)}, Déontologie: {len(deont_results)}, CSP: {len(csp_results)}")
        
        # Affichage des résultats par catégorie
        if deont_results:
            enriched_content += "### ⚖️ Code de Déontologie Médicale\n\n"
            for i, result in enumerate(deont_results[:3], 1):
                score_emoji = "🟢" if result['relevance_score'] >= 0.8 else "🟡" if result['relevance_score'] >= 0.6 else "🔴"
                enriched_content += f"**{i}. Article {result['article']}** {score_emoji} (Score: {result['relevance_score']:.2f})\n"
                enriched_content += f"*Source: {result['source']}*\n"
                enriched_content += f"{result['content'][:300]}...\n\n"
        
        if csp_results:
            enriched_content += "### 🏥 Code de la Santé Publique\n\n"
            for i, result in enumerate(csp_results[:3], 1):
                score_emoji = "🟢" if result['relevance_score'] >= 0.8 else "🟡" if result['relevance_score'] >= 0.6 else "🔴"
                enriched_content += f"**{i}. Article {result['article']}** {score_emoji} (Score: {result['relevance_score']:.2f})\n"
                enriched_content += f"*Source: {result['source']}*\n"
                enriched_content += f"{result['content'][:300]}...\n\n"
        
        if legal_results:
            enriched_content += "### 📖 Autres Sources Juridiques\n\n"
            # Filtrer les résultats déjà affichés
            other_results = [r for r in legal_results if r['collection'] not in ['deontologie', 'csp']]
            
            for i, result in enumerate(other_results[:3], 1):
                score_emoji = "🟢" if result['relevance_score'] >= 0.8 else "🟡" if result['relevance_score'] >= 0.6 else "🔴"
                enriched_content += f"**{i}. {result['collection'].upper()} - Article {result['article']}** {score_emoji} (Score: {result['relevance_score']:.2f})\n"
                enriched_content += f"*Source: {result['source']}*\n"
                enriched_content += f"{result['content'][:300]}...\n\n"
        
        # Résumé
        total_results = len(legal_results) + len(deont_results) + len(csp_results)
        if total_results > 0:
            enriched_content += f"✅ **{total_results} extraits juridiques trouvés dans la base de connaissances**\n\n"
            enriched_content += "*Base ChromaDB avec 12,024 chunks de textes juridiques*\n\n"
        else:
            enriched_content += "ℹ️ *Aucun extrait juridique pertinent trouvé dans la base de connaissances*\n\n"
        
        return enriched_content
        
    except Exception as e:
        print(f"❌ Erreur ChromaDB: {e}")
        return f"\n\n⚠️ Erreur lors de la recherche ChromaDB: {str(e)}\n\n"

def enrich_analysis_with_google_search(query: str, analysis_type: str = "medical_legal") -> str:
    """
    Enrichit l'analyse avec des recherches Google pour jurisprudence et ONIAM
    Utilise votre Custom Search Engine spécialisé
    """
    if not GOOGLE_SEARCH_AVAILABLE:
        return ""
    
    try:
        # Initialisation avec gestion d'erreur robuste
        search_api = GoogleSearchAPI()
        enriched_content = "\n\n## 🔍 Sources Juridiques Complémentaires\n\n"
        
        # Debug: afficher les paramètres
        print(f"🔍 Recherche Google CSE: {query[:50]}...")
        
        if analysis_type == "medical_legal":
            # Utiliser la recherche étendue pour obtenir plus de ressources
            print(f"🔍 Recherche Google CSE ÉTENDUE: {query[:50]}...")
            
            try:
                # Recherche étendue pour plus de ressources
                extended_results = search_api.search_extended_legal(query, max_results=15)
                
                if extended_results:
                    # Dédupliquer et organiser les résultats
                    seen_links = set()
                    unique_results = []
                    
                    for result in extended_results:
                        if result['link'] not in seen_links:
                            seen_links.add(result['link'])
                            unique_results.append(result)
                    
                    # Séparer jurisprudence et ONIAM
                    jur_results = [r for r in unique_results if any(src in r['source'].lower() for src in ['cassation', 'conseil', 'dalloz'])]
                    oniam_results = [r for r in unique_results if 'oniam' in r['source'].lower()]
                    other_results = [r for r in unique_results if r not in jur_results and r not in oniam_results]
                    
                    print(f"📊 Résultats étendus - Jurisprudence: {len(jur_results)}, ONIAM: {len(oniam_results)}, Autres: {len(other_results)}")
                    
                    # Affichage des résultats
                    if jur_results or oniam_results or other_results:
                        enriched_content += "### 📚 Jurisprudence Récente (Sources Officielles)\n\n"
                        enriched_content += "*Sources : Cour de Cassation, Conseil d'État, Dalloz*\n\n"
                        
                        # Afficher jurisprudence
                        for i, result in enumerate(jur_results[:3], 1):
                            enriched_content += f"**{i}. {result['title']}**\n"
                            enriched_content += f"*Source: {result['source']}*\n"
                            enriched_content += f"{result['snippet']}\n\n"
                        
                        # Afficher ONIAM
                        if oniam_results:
                            enriched_content += "### 🏛️ Informations ONIAM (Source Officielle)\n\n"
                            enriched_content += "*Source : Office National d'Indemnisation des Accidents Médicaux*\n\n"
                            
                            for i, result in enumerate(oniam_results[:3], 1):
                                enriched_content += f"**{i}. {result['title']}**\n"
                                enriched_content += f"*Source: {result['source']}*\n"
                                enriched_content += f"{result['snippet']}\n\n"
                        
                        # Afficher autres résultats
                        if other_results:
                            enriched_content += "### 🔍 Autres Sources Juridiques\n\n"
                            
                            for i, result in enumerate(other_results[:3], 1):
                                enriched_content += f"**{i}. {result['title']}**\n"
                                enriched_content += f"*Source: {result['source']}*\n"
                                enriched_content += f"{result['snippet']}\n\n"
                        
                        total_found = len(jur_results) + len(oniam_results) + len(other_results)
                        enriched_content += f"✅ **{total_found} résultats trouvés via votre Custom Search Engine spécialisé**\n\n"
                        enriched_content += "*Sources configurées : Cour de Cassation, Conseil d'État, Dalloz, HAS, ONIAM*\n\n"
                    else:
                        enriched_content += "ℹ️ *Aucun résultat pertinent trouvé dans les sources configurées*\n\n"
                        
            except Exception as e:
                print(f"❌ Erreur recherche étendue: {e}")
                enriched_content += f"⚠️ *Erreur lors de la recherche étendue: {str(e)}*\n\n"
        
        return enriched_content
        
    except Exception as e:
        print(f"❌ Erreur Google Search CSE: {e}")
        return f"\n\n⚠️ Erreur lors de la recherche Google CSE: {str(e)}\n\n"

def simple_analysis_fallback(situation: str) -> str:
    """Analyse simple de fallback si les autres méthodes échouent"""
    try:
        # Analyse basique avec Grok-4
        from grok_client import GrokClient
        
        # Initialiser le client Grok
        grok_client = GrokClient()
        
        # Prompt simple mais efficace
        prompt = f"""
Analysez cette situation médico-légale de manière professionnelle :

SITUATION : {situation}

Fournissez une analyse structurée avec :
1. **Fondements légaux** : Articles de loi applicables
2. **Jurisprudence** : Décisions de justice pertinentes  
3. **Responsabilité** : Qui peut être tenu responsable
4. **Indemnisation** : Types de dommages et intérêts possibles
5. **Recommandations** : Actions à entreprendre

Format : Analyse claire et structurée en français.
"""
        
        # Appel à Grok-4
        response = grok_client.generate_response(prompt)
        
        if response and "❌" not in response:
            return response
        else:
            return "❌ Erreur lors de l'analyse. Veuillez réessayer."
            
    except Exception as e:
        return f"❌ Erreur technique : {str(e)}"

def render_interface():
    """Interface principale avec Grok-4"""
    
    # Configuration de la page
    st.set_page_config(
        page_title="⚖️ LegalDocBot - Expert Médico-Légal avec Grok-4",
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
    
    /* Animations */
    .fade-in {
        animation: fadeIn 0.8s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Glass card styling */
    .glass-card h1, .glass-card h2, .glass-card h3 {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    .glass-card p {
        color: #e0e0e0 !important;
    }
    
    .glass-card strong, .glass-card b {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Specific styling for analysis content - FORCED VISIBILITY */
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
    
    /* Override any conflicting styles */
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
    
    /* Expert Badge */
    .expert-badge {
        background: linear-gradient(135deg, #00A9FF, #2D1B69);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 169, 255, 0.3);
    }
    
    /* Premium Footer */
    .premium-footer {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        text-align: center;
        margin-top: 2rem;
    }
    
    /* Metrics Styling */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00A9FF, #2D1B69);
    }
    
    /* Dataframe Styling */
    .dataframe {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }

    /* Expert Button Line */
    .expert-btn-line {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    /* Grand bouton Analyser */
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
    
    /* Target every Streamlit button */
    button[data-testid="baseButton-primary"] {
        height: 60px !important;
        font-size: 1.2rem !important;
        padding: 0 2rem !important;
        min-width: 220px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # --- HEADER ---
    st.markdown("""
    <div class="premium-header fade-in">
        <h1>⚖️ LegalDocBot</h1>
        <h3>Analyse Médicale & Juridique d'Expert avec Grok-4</h3>
        <p style="font-size: 1rem; color: #A0AEC0; margin-top: 0.5rem;">
            Analyse neutre et objective • Recours ONIAM sans faute • Conseils équilibrés • Powered by Grok-4
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- KPI METRICS ---
    stats = analytics.get_stats()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="kpi-card fade-in"><p class="kpi-number">{stats["total_analyses"]}</p><p class="kpi-label">Analyses</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card fade-in"><p class="kpi-number">{stats["avg_time"]:.1f}s</p><p class="kpi-label">Temps Moyen</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card fade-in"><p class="kpi-number">{stats["favorites_count"]}</p><p class="kpi-label">Favoris</p></div>', unsafe_allow_html=True)
    
    # --- TABS FOR MAIN CONTENT ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🔍 Analyse", "📝 Lettres", "🎭 Plaidoyers", "📅 Timeline", "📊 Analytics", "💰 Indemnisation"])
    
    with tab1:
        # --- STATE MANAGEMENT to control UI display (form vs. spinner/results) ---
        # Initialize all session state variables at the beginning
        if "analysis_started" not in st.session_state:
            st.session_state.analysis_started = False
        if "current_analysis" not in st.session_state:
            st.session_state.current_analysis = ""
        if "situation_input" not in st.session_state:
            st.session_state.situation_input = ""
        if "mode_input" not in st.session_state:
            st.session_state.mode_input = "hybrid"
        if "fast_mode_input" not in st.session_state:
            st.session_state.fast_mode_input = False
        if "show_spinner" not in st.session_state:
            st.session_state.show_spinner = False
        if "current_mode" not in st.session_state:
            st.session_state.current_mode = "hybrid"
        if "current_fast_mode" not in st.session_state:
            st.session_state.current_fast_mode = False
        if "current_situation" not in st.session_state:
            st.session_state.current_situation = ""
        if "current_letter" not in st.session_state:
            st.session_state.current_letter = ""
        if "current_letter_type" not in st.session_state:
            st.session_state.current_letter_type = ""
        
        # Handle reset if requested
        if "reset_analysis" in st.session_state and st.session_state.reset_analysis:
            st.session_state.situation_input = ""
            st.session_state.reset_analysis = False
        
        # --- DISPLAY THE INPUT FORM ---
        st.markdown("<div class='content-card fade-in'>", unsafe_allow_html=True)
        st.subheader("Nouvelle Analyse Juridique avec Grok-4")
        st.info("💡 **Analyse neutre et objective** : Notre système présente tous les points de vue et recours possibles, y compris les voies ONIAM sans faute médicale. Powered by Grok-4.")
        
        # --- SECTION 1: INPUT PRINCIPAL ---
        situation = st.text_area(
            "📝 Décrivez votre situation médicale ou juridique :",
            height=150,
            placeholder="Exemple : Un patient a subi une erreur médicale lors d'une intervention chirurgicale. Quels sont ses droits et les recours possibles ?",
            key="situation_input"
        )
        
        # --- SECTION 2: CONTRÔLES PRINCIPAUX REGROUPÉS ---
        st.markdown("### ⚙️ Configuration de l'Analyse")
        
        # ---------- 1ᵉʳ ligne : bouton Analyser ----------
        st.markdown('<div class="expert-btn-line">', unsafe_allow_html=True)
        analyze_button = st.button(
            "🧠 Analyser",
            type="primary",
            key="analyze_button",
            help="Lancer l'analyse juridique avec Grok-4"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # ---------- 2ᵉ ligne : les 3 autres contrôles ----------
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            mode = st.selectbox(
                "🎯 Mode d'Analyse",
                ["hybrid", "local_rag", "grok", "chromadb_rag"],
                format_func=lambda x: {
                    "hybrid": "🤖 Hybride (Grok-4 + Google)",
                    "local_rag": "📚 Base Locale",
                    "grok": "🧠 Grok-4 (Expert)",
                    "chromadb_rag": "⚖️ ChromaDB RAG"
                }[x],
                label_visibility="collapsed",
                key="mode_input"
            )

        with col2:
            fast_mode = st.checkbox("⚡ Ultra-Rapide", key="fast_mode_input")

        with col3:
            google_search = st.checkbox(
                "🔍 Google",
                key="google_search_input",
                value=GOOGLE_SEARCH_AVAILABLE,
                disabled=not GOOGLE_SEARCH_AVAILABLE
            )
        
        # --- VALIDATION ET INFORMATIONS ---
        if analyze_button and not situation.strip():
            st.warning("⚠️ Veuillez décrire une situation à analyser.")
        
        # --- INFORMATIONS CONTEXTUELLES ---
        if mode == "grok":
            st.info("🧠 **Mode Grok-4 Expert** : Utilise directement Grok-4 pour une analyse juridique de haute qualité. Analyse détaillée et approfondie.")
        elif mode == "chromadb_rag":
            st.info("⚖️ **Mode ChromaDB RAG** : Utilise directement la base ChromaDB avec 11,998 chunks de codes légaux français (CSP, CSS, Code Pénal, Code Civil, Déontologie). Analyse avec Grok-4 pour une précision maximale.")
        
        # Information sur la recherche Google
        if GOOGLE_SEARCH_AVAILABLE and google_search:
            st.info("🔍 **Recherche Google CSE activée** : L'analyse sera enrichie avec de la jurisprudence récente (Cour de Cassation, Conseil d'État, Dalloz) et des informations ONIAM officielles via votre Custom Search Engine spécialisé.")
        
        # Options simplifiées - déontologie toujours activée
        include_deontologie = True
        force_deontologie = False
        
        # --- LOGIQUE D'ANALYSE ---
        if analyze_button and situation.strip():
            # Pipeline exceptionnel 10/10 en 1 ligne
            st.session_state.analysis_started = True
            st.session_state.current_mode = mode
            st.session_state.current_fast_mode = fast_mode
            st.session_state.current_situation = situation
            st.session_state.current_google_search = google_search
            
            # Spinner pour montrer que l'analyse est en cours
            with st.spinner("🧠 Grok-4 en action... Analyse juridique exceptionnelle en cours..."):
                # Mesurer le temps
                start_time = time.time()
                
                # Pipeline exceptionnel en 1 ligne
                from ui_utils import run_exceptional_analysis
                analysis_result = run_exceptional_analysis(situation, mode, fast_mode)
                
                # Calculer le temps
                analysis_time = time.time() - start_time
                st.session_state.analysis_duration = analysis_time
                
                # Sauvegarder l'analyse
                st.session_state.current_analysis = analysis_result
                
                # Analytics
                analytics.track_analysis(situation, analysis_result, analysis_time, mode)
            
            # Rerun pour afficher les résultats
            st.rerun()
        
        # --- AFFICHAGE DES RÉSULTATS ---
        if st.session_state.current_analysis and "❌" not in st.session_state.current_analysis:
            st.markdown("<div class='analysis-result-card fade-in'>", unsafe_allow_html=True)
            
            # Affichage avec l'interface exceptionnelle 10/10
            from ui_utils import display_analysis_10
            display_analysis_10(
                st.session_state.current_analysis,
                st.session_state.current_situation,
                st.session_state.analysis_duration,
                st.session_state.current_mode,
                st.session_state.current_fast_mode
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # --- SECTION 4: AFFICHAGE DES RÉSULTATS ---
        # Cette section n'est plus nécessaire car l'analyse se fait directement dans la logique ci-dessus
    
    # Autres onglets (simplifiés pour l'exemple)
    with tab2:
        st.markdown("<div class='content-card fade-in'>", unsafe_allow_html=True)
        st.subheader("📝 Générateur de Lettres Professionnelles")
        st.markdown("Générez des lettres professionnelles exceptionnelles pour CDU, CCI, ONIAM et assurances.")
        
        # Intégration du générateur de lettres
        if hasattr(st.session_state, 'current_analysis') and st.session_state.current_analysis:
            display_letter_generator(
                st.session_state.current_situation,
                st.session_state.current_analysis
            )
        else:
            st.warning("⚠️ Veuillez d'abord effectuer une analyse juridique pour générer des lettres.")
            st.info("💡 L'analyse juridique fournit les fondements légaux nécessaires à la rédaction de lettres professionnelles.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='content-card fade-in'>", unsafe_allow_html=True)
        st.subheader("🎭 Générateur de Plaidoyers")
        st.markdown("Générez des plaidoyers structurés pour vos audiences (ONIAM, Tribunal, Cassation, Expertise).")
        
        # Intégration du générateur de plaidoyers
        if hasattr(st.session_state, 'current_situation') and st.session_state.current_situation and hasattr(st.session_state, 'current_analysis') and st.session_state.current_analysis:
            from pleadings_generator import display_pleadings_generator
            display_pleadings_generator(
                st.session_state.current_situation,
                st.session_state.current_analysis
            )
        else:
            st.warning("⚠️ Veuillez d'abord effectuer une analyse juridique pour générer des plaidoyers.")
            st.info("💡 L'analyse juridique fournit les fondements nécessaires à la rédaction de plaidoyers.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab4:
        st.markdown("<div class='content-card fade-in'>", unsafe_allow_html=True)
        st.subheader("📅 Timeline Interactive des Faits")
        st.markdown("Extraction automatique et visualisation des événements chronologiques.")
        
        # Intégration du générateur de timeline
        if hasattr(st.session_state, 'current_situation') and st.session_state.current_situation:
            display_timeline_generator(st.session_state.current_situation)
        else:
            st.warning("⚠️ Veuillez d'abord saisir une situation pour générer la timeline.")
            st.info("💡 La timeline extrait automatiquement les dates et événements de votre situation.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab5:
        st.markdown("<div class='content-card fade-in'>", unsafe_allow_html=True)
        st.subheader("📊 Analytics")
        st.markdown("Statistiques d'utilisation et performances.")
        
        # Analytics charts
        if analytics.analysis_count > 0:
            col1, col2 = st.columns(2)
            with col1:
                create_performance_chart(analytics)
            with col2:
                create_mode_usage_chart(analytics)
        else:
            st.info("📊 Aucune donnée d'analyse disponible pour le moment.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab6:
        st.markdown("<div class='content-card fade-in'>", unsafe_allow_html=True)
        st.subheader("💰 Calculateur d'Indemnisation")
        st.markdown("Calculez les indemnisations selon les barèmes ONIAM 2024 et la jurisprudence française.")
        
        # Intégration du calculateur d'indemnisation
        display_compensation_calculator()
        
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_interface()

def main():
    """Fonction principale pour Streamlit Cloud"""
    render_interface() 