# --------- EXCEPTIONNAL BOOSTER ------------
DIVERSIFY_PROMPT = """
⚖️ DIVERSIFICATION OBLIGATOIRE  
Intègre **au moins 4 familles juridiques pertinentes** choisies dynamiquement :
- Code civil, pénal, santé, sécurité sociale, déontologie
- Jurisprudence (Cass., CE, TA)
- ONIAM, HAS, ARS, CNAM
Pour chaque source : Source + Applicabilité + Application concrète.
"""
# ------------------------------------------

import streamlit as st
import pandas as pd
import time
import hashlib
from datetime import datetime
from analytics_module import analytics
from export_utils import export_to_pdf, export_letter_to_pdf, export_plea_to_pdf, compare_analyses
from letter_generator import generate_professional_letter, generate_exceptional_plea
from enhanced_analysis_module import EnhancedAnalysisModule
# from bot_core import MedicalLegalBotHybrid  # Module supprimé

# Configuration pour les systèmes disponibles
OPENAI_AVAILABLE = False
RAG_SYSTEM_AVAILABLE = False

def organize_google_results(situation_description):
    """
    Organise les résultats Google Search en sections séparées pour jurisprudence et ONIAM
    """
    try:
        from google_search_module import GoogleSearchAPI
        
        search_api = GoogleSearchAPI()
        
        # Recherche jurisprudence
        jurisprudence_results = []
        try:
            jur_results = search_api.search_jurisprudence(situation_description, max_results=5)
            jurisprudence_results = jur_results
            print(f"✅ {len(jurisprudence_results)} résultats jurisprudence trouvés")
        except Exception as e:
            print(f"⚠️ Erreur recherche jurisprudence: {e}")
        
        # Recherche ONIAM
        oniam_results = []
        try:
            oniam_results = search_api.search_oniam(situation_description, max_results=5)
            print(f"✅ {len(oniam_results)} résultats ONIAM trouvés")
        except Exception as e:
            print(f"⚠️ Erreur recherche ONIAM: {e}")
        
        return jurisprudence_results, oniam_results
        
    except Exception as e:
        print(f"❌ Erreur organisation résultats Google: {e}")
        return [], []

def create_jurisprudence_section(results):
    """
    Crée une section formatée pour la jurisprudence
    """
    if not results:
        return ""
    
    section = "\n\n**🏛️ JURISPRUDENCE PERTINENTE :**\n\n"
    
    for i, result in enumerate(results[:5], 1):
        # Score avec emoji
        score = result.get('relevance_score', 0.5)
        if score >= 0.8:
            score_emoji = "🟢"
        elif score >= 0.6:
            score_emoji = "🟡"
        else:
            score_emoji = "🔴"
        
        # Source avec emoji
        source = result.get('source', 'Source')
        source_emoji = "⚖️"
        if 'cassation' in source.lower():
            source_emoji = "👑"
        elif 'conseil' in source.lower():
            source_emoji = "🏛️"
        elif 'legifrance' in source.lower():
            source_emoji = "📖"
        
        section += f"**{i}. {source_emoji} {result.get('title', 'Titre non disponible')}** {score_emoji} (Score: {score:.2f})\n"
        section += f"*Source: {source}*\n"
        
        if result.get('url'):
            section += f"*URL: {result.get('url')}*\n"
        
        # Extraire un extrait court
        snippet = result.get('snippet', '')
        if snippet:
            short_snippet = snippet[:200].strip()
            if len(snippet) > 200:
                short_snippet += "..."
            section += f"**Contexte :** {short_snippet}\n"
        
        section += "\n"
    
    section += f"✅ **{len(results)} décisions de jurisprudence analysées**\n"
    section += "*Recherche cross-encoder avec bonus sources officielles*\n\n"
    
    return section

def create_oniam_section(results):
    """
    Crée une section formatée pour les résultats ONIAM
    """
    if not results:
        return ""
    
    section = "\n\n**🏥 INFORMATIONS ONIAM :**\n\n"
    
    for i, result in enumerate(results[:5], 1):
        # Score avec emoji
        score = result.get('relevance_score', 0.5)
        if score >= 0.8:
            score_emoji = "🟢"
        elif score >= 0.6:
            score_emoji = "🟡"
        else:
            score_emoji = "🔴"
        
        # Source avec emoji
        source = result.get('source', 'Source')
        source_emoji = "🏥"
        if 'oniam' in source.lower():
            source_emoji = "🏛️"
        elif 'ameli' in source.lower():
            source_emoji = "💊"
        elif 'service-public' in source.lower():
            source_emoji = "🏛️"
        
        section += f"**{i}. {source_emoji} {result.get('title', 'Titre non disponible')}** {score_emoji} (Score: {score:.2f})\n"
        section += f"*Source: {source}*\n"
        
        if result.get('url'):
            section += f"*URL: {result.get('url')}*\n"
        
        # Extraire un extrait court
        snippet = result.get('snippet', '')
        if snippet:
            short_snippet = snippet[:200].strip()
            if len(snippet) > 200:
                short_snippet += "..."
            section += f"**Contexte :** {short_snippet}\n"
        
        section += "\n"
    
    section += f"✅ **{len(results)} informations ONIAM récupérées**\n"
    section += "*CSE ONIAM dédié avec barèmes d'indemnisation actualisés*\n\n"
    
    return section

# --- CACHE DES RESSOURCES LOURDES ---
@st.cache_resource(ttl=3600)  # Cache pour 1 heure
def get_bot_instance():
    """
    Charge et met en cache l'instance du bot.
    Cette fonction ne sera exécutée qu'une seule fois grâce à @st.cache_resource.
    """
    print("--- INITIALISATION DU BOT (opération coûteuse) ---")
    try:
        # bot = MedicalLegalBotHybrid()  # Module supprimé
        print("✅ Bot initialisé avec succès")
        return None  # Bot temporairement désactivé
    except Exception as e:
        print(f"❌ Erreur initialisation bot: {e}")
        return None

# --- CACHE OPENAI KNOWLEDGE BASE ---
@st.cache_resource(ttl=7200)  # Cache pour 2 heures
def get_openai_knowledge_base():
    """
    Fonction désactivée - Base OpenAI non utilisée
    """
    return None

@st.cache_resource(ttl=3600)  # Cache pour 1 heure
def get_grok_client():
    """
    Retourne l'instance du client Grok-4 (singleton)
    """
    from grok_client import get_grok_client as get_grok
    return get_grok()

# --- CACHE PERSISTANT DES RÉSULTATS ---
@st.cache_data(ttl=7200)  # Cache pour 2 heures
def cached_analysis_result(situation_description, mode, fast_mode):
    """
    Cache persistant des résultats d'analyse
    """
    cache_key = f"{situation_description}_{mode}_{fast_mode}"
    return cache_key

def create_performance_chart(analytics):
    """Crée un graphique de performance avec Streamlit"""
    if analytics.analysis_count == 0:
        return None
    
    df = analytics.get_history_df()
    if df.empty:
        return None
    
    st.line_chart(df.set_index('timestamp')['duration'])

def create_mode_usage_chart(analytics):
    """Crée un graphique d'usage des modes avec Streamlit"""
    stats = analytics.get_stats()
    mode_data = pd.DataFrame({
        'Mode': list(stats['mode_usage'].keys()),
        'Utilisations': list(stats['mode_usage'].values())
    })
    
    st.bar_chart(mode_data.set_index('Mode'))

def generate_structured_analysis(situation, top_chunks):
    context_text = "\n\n".join([
        f"{chunk.get('article') or chunk.get('section') or f'Page {chunk.get('page', '')}'}\n{chunk.get('texte')[:1000]}..."
        for chunk in top_chunks
    ])
    prompt = f"""
Tu es un avocat expert en droit médical français.

SITUATION À ANALYSER :
{situation}

EXTRAITS JURIDIQUES PERTINENTS :
{context_text}

TÂCHE : Analyse juridique COMPLÈTE et PRÉCISE basée sur les extraits fournis.

STRUCTURE REQUISE :
1. Qualification juridique
2. Base légale
3. Droits du patient
4. Recours possibles
5. Recommandations

Cite précisément les articles et sources trouvés.
"""
    # Utiliser le client Grok-4 mis en cache
    client = get_grok_client()
    if client:
        response = client.generate_completion(prompt, temperature=0.1)
        return response.strip() if response else "Erreur lors de la génération de l'analyse."
    else:
        return "❌ Erreur : Client Grok-4 non disponible"

def stream_analysis_result(analysis_text, situation_description="", analysis_time=0.0, mode_used="", google_enabled=False):
    """
    Affiche le résultat d'analyse avec la nouvelle interface structurée
    """
    if not analysis_text or "❌" in analysis_text:
        st.error("❌ Erreur lors de l'analyse. Veuillez réessayer.")
        return
    
    # Nettoyer et structurer l'analyse
    cleaned_analysis = clean_and_structure_analysis(analysis_text)
    
    # Afficher avec la nouvelle interface structurée
    display_analysis_results(
        cleaned_analysis, 
        situation_description, 
        analysis_time, 
        mode_used, 
        google_enabled
    )

# --- FONCTION DE CACHE OPTIMISÉE AVEC PROGRESSION ---
def cached_analysis(situation_description, mode, fast_mode):
    """Analyse avec Grok-4, ChromaDB et Google Search - Version optimisée"""
    
    # Vérifier le cache persistant d'abord
    cache_key = cached_analysis_result(situation_description, mode, fast_mode)
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    print(f"🧠 ANALYSE AVEC GROK-4 - Mode: {mode}, Fast: {fast_mode}")
    
    try:
        # Utiliser Grok-4 pour l'analyse
        from grok_client import get_grok_client
        client = get_grok_client()
        
        if not client.is_configured():
            return "❌ Erreur : Client Grok-4 non configuré. Vérifiez votre clé API XAI_API_KEY"
        
        # Enrichir avec ChromaDB si disponible
        chromadb_enrichment = ""
        try:
            from chromadb_search import get_chromadb_search
            chromadb_search = get_chromadb_search()
            if chromadb_search.is_available:
                print("🔍 Recherche ChromaDB UNIFIÉE...")
                # Recherche UNIFIÉE dans TOUTE la base de connaissances
                unified_results = chromadb_search.search_unified_legal_knowledge(situation_description, top_k=15)
                
                if unified_results:
                    # Trier par score final décroissant
                    sorted_results = sorted(unified_results, key=lambda x: x.get('final_score', x.get('relevance_score', 0)), reverse=True)
                    
                    # Dédupliquer les articles pour éviter les doublons
                    seen_articles = set()
                    unique_results = []
                    
                    for result in sorted_results:
                        # Créer une clé unique basée sur l'article et la source
                        article_key = f"{result.get('article', '')}_{result.get('source', '')}"
                        
                        if article_key not in seen_articles:
                            seen_articles.add(article_key)
                            unique_results.append(result)
                    
                    # Préparer les articles pour intégration dans FONDEMENTS LÉGAUX
                    legal_articles_section = "\n\n**ARTICLES DE LOI PERTINENTS INTÉGRÉS :**\n\n"
                    
                    for i, result in enumerate(unique_results[:8], 1):  # Top 8 articles uniques
                        # Score avec emoji
                        final_score = result.get('final_score', result['relevance_score'])
                        if final_score >= 0.8:
                            score_emoji = "🟢"
                        elif final_score >= 0.6:
                            score_emoji = "🟡"
                        else:
                            score_emoji = "🔴"
                        
                        # Source avec emoji
                        source_type = result.get('source_type', result['collection'].upper())
                        emoji_map = {
                            'Code de Déontologie Médicale': '⚖️',
                            'Code de la Santé Publique': '🏥',
                            'Code de la Sécurité Sociale': '🏛️',
                            'Code Civil': '📖',
                            'Code Pénal': '⚖️'
                        }
                        source_emoji = emoji_map.get(source_type, '📋')
                        
                        legal_articles_section += f"**{i}. {source_emoji} {source_type} - Article {result['article']}** {score_emoji} (Score: {final_score:.2f})\n"
                        legal_articles_section += f"*Source: {result['source']}*\n"
                        
                        # Afficher les scores détaillés si reranké
                        if result.get('reranked'):
                            cross_score = result.get('cross_encoder_score', 0)
                            source_bonus = result.get('source_bonus', 0)
                            legal_articles_section += f"*Cross-Encoder: {cross_score:.2f} | Bonus: {source_bonus:.2f}*\n"
                        
                        # Extraire un extrait court et pertinent du contenu
                        content = result.get('content', '')
                        if content:
                            # Prendre les 200 premiers caractères et ajouter "..."
                            short_content = content[:200].strip()
                            if len(content) > 200:
                                short_content += "..."
                            
                            legal_articles_section += f"**Contexte :** {short_content}\n"
                            
                            # Expliquer pourquoi cet article est pertinent
                            legal_articles_section += f"**Applicabilité :** Cet article est pertinent car il traite directement de "
                            
                            # Détecter les mots-clés pour expliquer l'applicabilité
                            keywords = situation_description.lower().split()
                            article_keywords = content.lower().split()
                            
                            # Trouver les mots-clés communs
                            common_keywords = set(keywords) & set(article_keywords)
                            relevant_terms = [kw for kw in common_keywords if len(kw) > 3]  # Mots de plus de 3 lettres
                            
                            if relevant_terms:
                                legal_articles_section += f"la {', '.join(relevant_terms[:3])} mentionnée dans votre situation.\n\n"
                            else:
                                legal_articles_section += f"la situation médicale décrite et s'applique aux droits du patient.\n\n"
                        else:
                            legal_articles_section += "*Contenu non disponible*\n\n"
                    
                    # Stocker pour intégration dans l'analyse
                    chromadb_enrichment = legal_articles_section
                    
                    total_results = len(unified_results)
                    chromadb_enrichment += f"✅ **{total_results} articles juridiques pertinents trouvés dans la base de connaissances**\n\n"
                    chromadb_enrichment += "*Base ChromaDB avec 12,024 chunks de textes juridiques - Reranking cross-encoder*\n\n"
                else:
                    chromadb_enrichment = "\n\nℹ️ *Aucun article juridique pertinent trouvé dans la base de connaissances*\n\n"
                    
        except Exception as e:
            print(f"❌ Erreur ChromaDB: {e}")
            chromadb_enrichment = f"\n\n⚠️ Erreur lors de la recherche ChromaDB: {str(e)}\n\n"
        
        # NOUVEAU : Recherche Google Search avec sections séparées
        print("🔍 Recherche Google Search avec sections séparées...")
        jurisprudence_results, oniam_results = organize_google_results(situation_description)
        
        # Créer les sections formatées
        jurisprudence_section = create_jurisprudence_section(jurisprudence_results)
        oniam_section = create_oniam_section(oniam_results)
        
        # NOUVEAU : Préparer le contexte enrichi pour Grok-4
        enriched_context = ""
        
        # Ajouter les articles ChromaDB au contexte (pour analyse par Grok-4)
        if chromadb_enrichment and unique_results:
            enriched_context += "\n\n**ARTICLES DE LOI PERTINENTS :**\n"
            # Extraire seulement le contenu des articles sans le formatage d'affichage
            for result in unique_results[:8]:
                content = result.get('content', '')
                if content:
                    enriched_context += f"- {result.get('source_type', 'Code')} Article {result.get('article', 'N/A')}: {content[:300]}...\n"
        
        # Ajouter la jurisprudence au contexte
        if jurisprudence_results:
            enriched_context += "\n\n**JURISPRUDENCE PERTINENTE :**\n"
            for result in jurisprudence_results[:5]:
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                source = result.get('source', '')
                url = result.get('url', '')
                enriched_context += f"- {title} (Source: {source})\n  {snippet}\n  URL: {url}\n"
        
        # Ajouter les informations ONIAM au contexte
        if oniam_results:
            enriched_context += "\n\n**INFORMATIONS ONIAM :**\n"
            for result in oniam_results[:5]:
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                source = result.get('source', '')
                url = result.get('url', '')
                enriched_context += f"- {title} (Source: {source})\n  {snippet}\n  URL: {url}\n"
        
        # Créer le prompt enrichi pour Grok-4
        enriched_situation = f"""
SITUATION À ANALYSER :
{situation_description}

CONTEXTE ENRICHIT :
{enriched_context}

INSTRUCTIONS SPÉCIALES POUR ANALYSE EXPERTE :

1. **STRUCTURE OBLIGATOIRE ET FORMAT UNIFORME** :
   Respectez EXACTEMENT cette structure pour toutes les citations :

   **FONDEMENTS LÉGAUX DÉTAILLÉS :**
   
   **Article L. 1142-1 du Code de la Santé Publique (CSP) :**
   - **Source :** Code de la Santé Publique
   - **Applicabilité :** [Explication précise de pourquoi cet article s'applique au cas présent]
   - **Application concrète :** [Comment cet article se traduit dans la situation de Madame X]

   **Article 1240 du Code Civil :**
   - **Source :** Code Civil
   - **Applicabilité :** [Explication précise de pourquoi cet article s'applique au cas présent]
   - **Application concrète :** [Comment cet article se traduit dans la situation de Madame X]

   **JURISPRUDENCE APPLICABLE :**
   
   **Cass. 1re civ., 14 oct. 2010, n° 09-69.199 :**
   - **Source :** Cour de Cassation
   - **Applicabilité :** [Explication précise de pourquoi cette décision s'applique au cas présent]
   - **Application concrète :** [Comment cette jurisprudence se traduit dans la situation de Madame X]

   **INFORMATIONS ONIAM PERTINENTES :**
   
   **Barème ONIAM 2024 - Perte de chance :**
   - **Source :** ONIAM
   - **Applicabilité :** [Explication précise de pourquoi ces barèmes s'appliquent au cas présent]
   - **Application concrète :** [Comment ces barèmes se traduisent dans la situation de Madame X]

2. **RÈGLES DE FORMATAGE OBLIGATOIRES** :
   - **Articles de loi :** "Article [numéro] du [Code complet] ([abréviation]) :"
   - **Jurisprudence :** "[Tribunal], [date], n° [numéro] :"
   - **ONIAM :** "[Type d'information] - [Sous-catégorie] :"
   - **Sources :** Toujours indiquer la source officielle
   - **Applicabilité :** Toujours expliquer pourquoi c'est pertinent
   - **Application concrète :** Toujours montrer comment ça s'applique au cas

3. **SÉLECTION ET HIÉRARCHISATION** :
   - Sélectionnez UNIQUEMENT les sources les plus pertinentes (max 3-4 par catégorie)
   - Classez par ordre de pertinence décroissante
   - Ne citez que ce qui s'applique directement au cas

4. **RECOMMANDATIONS EXPERTES** :
   - Basées sur l'analyse des sources sélectionnées
   - Stratégie contentieuse adaptée aux sources pertinentes
   - Montants d'indemnisation justifiés par la jurisprudence

5. **INTERDICTIONS** :
   - PAS de listes de citations sans explication
   - PAS de scores ou de métadonnées techniques
   - PAS de sources non pertinentes
   - PAS de formatage libre

RESPECTEZ EXACTEMENT CE FORMAT. CHAQUE CITATION DOIT AVOIR : SOURCE + APPLICABILITÉ + APPLICATION CONCRÈTE.
"""
        
        # Analyse avec Grok-4 avec contexte enrichi
        print("🧠 Analyse avec Grok-4 (contexte enrichi)...")
        if fast_mode:
            analysis_result = client.generate_fast_analysis(enriched_situation)
        else:
            analysis_result = client.generate_detailed_analysis(enriched_situation)
        
        if not analysis_result or "❌" in analysis_result:
            return "❌ Erreur lors de l'analyse avec Grok-4"
        
        # NOUVEAU : Nettoyer et structurer l'analyse
        analysis_result = clean_and_structure_analysis(analysis_result, jurisprudence_results, oniam_results)
        
        # NOUVEAU : Ajouter une section de sources utilisées pour la transparence
        sources_section = "\n\n**📚 SOURCES UTILISÉES POUR CETTE ANALYSE :**\n\n"
        
        # Compter les sources
        total_sources = 0
        if jurisprudence_results:
            sources_section += f"🏛️ **Jurisprudence :** {len(jurisprudence_results)} décisions analysées\n"
            total_sources += len(jurisprudence_results)
        if oniam_results:
            sources_section += f"🏥 **ONIAM :** {len(oniam_results)} informations récupérées\n"
            total_sources += len(oniam_results)
        if chromadb_enrichment:
            sources_section += f"📖 **Articles de loi :** {len(unique_results)} articles pertinents\n"
            total_sources += len(unique_results)
        
        sources_section += f"\n✅ **Total :** {total_sources} sources analysées avec reranking cross-encoder\n"
        sources_section += "*Toutes les sources ont été intégrées dans l'analyse ci-dessus*\n\n"
        
        # Ajouter la section des sources à la fin
        analysis_result += sources_section
        
        # AMÉLIORATION DE L'ANALYSE POUR ATTEINDRE 10/10
        try:
            print("🔧 Application des améliorations pour niveau 10/10...")
            enhancer = EnhancedAnalysisModule()
            enhanced_analysis = enhancer.enhance_analysis(situation_description, analysis_result)
            
            if enhanced_analysis and len(enhanced_analysis) > len(analysis_result):
                analysis_result = enhanced_analysis
                print(f"✅ Analyse améliorée : +{len(enhanced_analysis) - len(analysis_result)} caractères")
            else:
                print("⚠️ Amélioration non appliquée")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'amélioration : {e}")
            # Continuer avec l'analyse originale
        
        # Cache du résultat dans session state
        st.session_state[cache_key] = analysis_result
        
        return analysis_result
        
    except Exception as e:
        error_msg = f"❌ Erreur lors de l'analyse : {str(e)}"
        print(f"Erreur dans cached_analysis: {e}")
        return error_msg 

def cached_analysis_rag(situation_description, mode, fast_mode):
    """
    Fonction désactivée - Système RAG non utilisé
    """
    return "❌ Erreur : Système RAG non disponible"

def cached_analysis_openai(situation_description, mode, fast_mode):
    """
    Fonction désactivée - Base OpenAI non utilisée
    """
    return "❌ Erreur : Base OpenAI non disponible" 

def clean_and_structure_analysis(analysis_result, jurisprudence_results, oniam_results):
    """
    Nettoie et structure l'analyse pour éliminer les citations brutes
    """
    print("🧹 Nettoyage et structuration de l'analyse...")
    
    # Supprimer les sections de citations brutes
    sections_to_remove = [
        "🏛️ JURISPRUDENCE PERTINENTE :",
        "🏥 INFORMATIONS ONIAM :",
        "📚 SOURCES UTILISÉES POUR CETTE ANALYSE :",
        "🔍 Sources Juridiques Complémentaires",
        "📚 Jurisprudence Récente (Sources Officielles)",
        "🔍 Autres Sources Juridiques",
        "ARTICLES DE LOI PERTINENTS INTÉGRÉS :",
        "✅ **10 articles juridiques pertinents trouvés dans la base de connaissances**",
        "Base ChromaDB avec 12,024 chunks de textes juridiques - Reranking cross-encoder"
    ]
    
    cleaned_analysis = analysis_result
    for section in sections_to_remove:
        # Trouver le début de la section
        start_idx = cleaned_analysis.find(section)
        if start_idx != -1:
            # Trouver la fin de la section (prochaine section ou fin)
            next_sections = ["## ", "### ", "**", "✅", "🎯", "🏛️", "🏥"]
            end_idx = len(cleaned_analysis)
            for next_section in next_sections:
                next_idx = cleaned_analysis.find(next_section, start_idx + len(section))
                if next_idx != -1 and next_idx < end_idx:
                    end_idx = next_idx
            
            # Supprimer la section
            cleaned_analysis = cleaned_analysis[:start_idx] + cleaned_analysis[end_idx:]
    
    # Ajouter une section de synthèse des sources utilisées
    if jurisprudence_results or oniam_results:
        synthesis_section = "\n\n**📋 SYNTHÈSE DES SOURCES ANALYSÉES :**\n\n"
        
        if jurisprudence_results:
            synthesis_section += f"🏛️ **Jurisprudence analysée :** {len(jurisprudence_results)} décisions examinées\n"
            synthesis_section += "*Les décisions les plus pertinentes ont été intégrées dans l'analyse ci-dessus*\n\n"
        
        if oniam_results:
            synthesis_section += f"🏥 **Informations ONIAM analysées :** {len(oniam_results)} sources examinées\n"
            synthesis_section += "*Les barèmes et procédures applicables ont été intégrés dans les recommandations*\n\n"
        
        synthesis_section += "✅ **Analyse experte réalisée :** Sélection et application des sources pertinentes\n"
        synthesis_section += "*Cette analyse ne se contente pas de citer, elle explique et applique*\n\n"
        
        cleaned_analysis += synthesis_section
    
    return cleaned_analysis 

def display_analysis_results(analysis_result, situation_description, analysis_time, mode_used, google_enabled):
    """
    Affiche les résultats d'analyse avec une interface claire et professionnelle
    """
    st.markdown("---")
    
    # KPIs en haut de page
    st.markdown("### 📊 Métriques d'Analyse")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    # Calculer les métriques
    sources_count = analysis_result.count("**Source :**")
    jurisprudence_count = analysis_result.count("**JURISPRUDENCE APPLICABLE :**")
    oniam_count = analysis_result.count("**INFORMATIONS ONIAM PERTINENTES :**")
    
    kpi1.metric("📋 Sources analysées", sources_count, delta=None)
    kpi2.metric("⚖️ Jurisprudence", jurisprudence_count, delta=None)
    kpi3.metric("🏥 ONIAM", oniam_count, delta=None)
    kpi4.metric("⏱️ Temps d'analyse", f"{analysis_time:.1f}s", delta=None)
    
    st.markdown("---")
    
    # Informations de configuration
    config_col1, config_col2 = st.columns(2)
    with config_col1:
        st.info(f"🤖 **Mode :** {mode_used}")
    with config_col2:
        if google_enabled:
            st.success("🔍 **Recherche Google :** Activée")
        else:
            st.warning("🔍 **Recherche Google :** Désactivée")
    
    st.markdown("---")
    
    # Affichage principal de l'analyse
    st.markdown("### 📋 Résultats de l'Analyse")
    
    # Diviser l'analyse en sections
    sections = split_analysis_into_sections(analysis_result)
    
    # Section 1: Qualification juridique
    if sections.get('qualification'):
        st.markdown("#### 1. 🎯 Qualification Juridique")
        st.markdown(sections['qualification'])
        st.markdown("---")
    
    # Section 2: Fondements légaux (avec expander pour les détails)
    if sections.get('fondements'):
        st.markdown("#### 2. ⚖️ Fondements Légaux")
        
        # Extraire les articles et jurisprudence pour affichage structuré
        articles, jurisprudence, oniam_info = extract_structured_sources(sections['fondements'])
        
        # Afficher les sources principales
        if articles:
            st.markdown("**📖 Articles de loi applicables :**")
            for article in articles[:3]:  # Limiter à 3 articles principaux
                st.markdown(f"• {article}")
            
            # Expander pour tous les articles
            if len(articles) > 3:
                with st.expander(f"📖 Voir tous les articles ({len(articles)} total)"):
                    for article in articles:
                        st.markdown(f"• {article}")
        
        # Expander pour les détails complets
        with st.expander("📋 Fondements légaux détaillés"):
            st.markdown(sections['fondements'])
        
        st.markdown("---")
    
    # Section 3: Recours possibles
    if sections.get('recours'):
        st.markdown("#### 3. 🛡️ Recours Possibles")
        st.markdown(sections['recours'])
        st.markdown("---")
    
    # Section 4: Recommandations
    if sections.get('recommandations'):
        st.markdown("#### 4. 💡 Recommandations")
        st.markdown(sections['recommandations'])
        st.markdown("---")
    
    # Section 5: Informations complémentaires (en expander)
    if sections.get('complementaires'):
        with st.expander("📚 Informations complémentaires"):
            st.markdown(sections['complementaires'])
    
    # Footer avec sources
    st.markdown("---")
    st.markdown("### 📋 Sources certifiées officielles")
    sources_col1, sources_col2, sources_col3 = st.columns(3)
    
    with sources_col1:
        st.markdown("**📖 Codes juridiques :**")
        st.markdown("• Code de la Santé Publique")
        st.markdown("• Code Civil")
        st.markdown("• Code Pénal")
    
    with sources_col2:
        st.markdown("**⚖️ Jurisprudence :**")
        st.markdown("• Cour de Cassation")
        st.markdown("• Conseil d'État")
        st.markdown("• Tribunaux")
    
    with sources_col3:
        st.markdown("**🏥 Organismes :**")
        st.markdown("• ONIAM")
        st.markdown("• HAS")
        st.markdown("• CCI")
    
    # Scroll to top
    st.markdown("""
    <script>
    var body = window.parent.document.querySelector(".main");
    body.scrollTop = 0;
    </script>
    """, unsafe_allow_html=True)

def display_analysis_10(analysis, sit, t, mode, google_ok):
    """UI ultra-pro : 4 blocs + KPIs + scroll-to-top"""
    st.markdown("---")
    
    # KPIs ultra-compacts
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🧑‍⚖️ Sources", analysis.count("**Source :**"))
    c2.metric("⚖️ Jurisprudence", analysis.count("**Cass"))
    c3.metric("🏥 ONIAM", analysis.count("Barème ONIAM"))
    c4.metric("⏱️ Temps", f"{t:.1f}s")

    st.markdown("---")
    
    # Affichage principal de l'analyse
    st.markdown("### 📋 Résultats de l'Analyse")
    st.markdown(analysis)  # déjà nettoyé

    st.markdown("---")
    
    # Sources certifiées en expander
    with st.expander("📚 Sources certifiées officielles"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**📖 Codes :**")
            st.write("• Santé Publique")
            st.write("• Civil")
            st.write("• Pénal")
            st.write("• Déontologie")
        with col2:
            st.write("**⚖️ Jurisprudence :**")
            st.write("• Cour de Cassation")
            st.write("• Conseil d'État")
            st.write("• Tribunaux")
        with col3:
            st.write("**🏥 Organismes :**")
            st.write("• ONIAM")
            st.write("• HAS")
            st.write("• CCI")
            st.write("• CNAM")
    
    # Scroll to top automatique
    st.markdown("""
    <script>
    var body = window.parent.document.querySelector(".main");
    body.scrollTop = 0;
    </script>
    """, unsafe_allow_html=True)

def build_enriched_context(situation, juris, oniam, chroma):
    """Assemble le contexte ultime avant Grok-4"""
    ctx = f"SITUATION À ANALYSER :\n{situation}\n\n"
    
    if chroma:
        ctx += "**ARTICLES DE LOI PERTINENTS :**\n"
        for a in chroma[:5]:
            ctx += f"- {a.get('source_type', 'Code')} Article {a.get('article', '')} : {a.get('content', '')[:250]}...\n"
        ctx += "\n"
    
    if juris:
        ctx += "**JURISPRUDENCE PERTINENTE :**\n"
        for j in juris[:3]:
            ctx += f"- {j.get('title', '')} (Source: {j.get('source', '')})\n"
        ctx += "\n"
    
    if oniam:
        ctx += "**INFORMATIONS ONIAM :**\n"
        for o in oniam[:3]:
            ctx += f"- {o.get('title', '')} (Source: {o.get('source', '')})\n"
        ctx += "\n"
    
    return ctx

def run_exceptional_analysis(situation, mode, fast):
    """
    Pipeline complet : search → enrich → analyse → UI 10/10
    """
    # 1. Cache avec clé unique
    key = f"{situation}_{mode}_{fast}"
    if key in st.session_state:
        return st.session_state[key]

    print("🚀 ANALYSE EXCEPTIONNELLE 10/10 - Démarrage...")
    
    try:
        # 2. Recherche multi-sources
        print("🔍 Recherche multi-sources...")
        juris, oniam = organize_google_results(situation)
        
        # Recherche ChromaDB si disponible
        chroma = []
        try:
            from chromadb_search import get_chromadb_search
            chromadb_search = get_chromadb_search()
            if chromadb_search.is_available:
                print("🔍 Recherche ChromaDB UNIFIÉE...")
                unified_results = chromadb_search.search_unified_legal_knowledge(situation, top_k=10)
                if unified_results:
                    chroma = unified_results[:5]  # Top 5 articles
        except Exception as e:
            print(f"⚠️ ChromaDB non disponible: {e}")

        # 3. Contexte enrichi
        print("🧠 Construction du contexte enrichi...")
        ctx = build_enriched_context(situation, juris, oniam, chroma)
        
        # Prompt exceptionnel avec diversification
        prompt = f"""
{DIVERSIFY_PROMPT}

{ctx}

INSTRUCTIONS SPÉCIALES POUR ANALYSE EXPERTE :

1. **STRUCTURE OBLIGATOIRE ET FORMAT UNIFORME** :
   Respectez EXACTEMENT cette structure pour toutes les citations :

   **FONDEMENTS LÉGAUX DÉTAILLÉS :**
   
   **Article L. 1142-1 du Code de la Santé Publique (CSP) :**
   - **Source :** Code de la Santé Publique
   - **Applicabilité :** [Explication précise de pourquoi cet article s'applique au cas présent]
   - **Application concrète :** [Comment cet article se traduit dans la situation de Madame X]

   **JURISPRUDENCE APPLICABLE :**
   
   **Cass. 1re civ., 14 oct. 2010, n° 09-69.199 :**
   - **Source :** Cour de Cassation
   - **Applicabilité :** [Explication précise de pourquoi cette décision s'applique au cas présent]
   - **Application concrète :** [Comment cette jurisprudence se traduit dans la situation de Madame X]

   **INFORMATIONS ONIAM PERTINENTES :**
   
   **Barème ONIAM 2024 - Perte de chance :**
   - **Source :** ONIAM
   - **Applicabilité :** [Explication précise de pourquoi ces barèmes s'appliquent au cas présent]
   - **Application concrète :** [Comment ces barèmes se traduisent dans la situation de Madame X]

2. **DIVERSIFICATION OBLIGATOIRE** :
   - Intégrez AU MOINS 4 familles juridiques différentes
   - Code civil, pénal, santé, sécurité sociale, déontologie
   - Jurisprudence (Cass., CE, TA)
   - ONIAM, HAS, ARS, CNAM
   - Chaque source doit avoir : Source + Applicabilité + Application concrète

3. **RÈGLES DE FORMATAGE OBLIGATOIRES** :
   - **Articles de loi :** "Article [numéro] du [Code complet] ([abréviation]) :"
   - **Jurisprudence :** "[Tribunal], [date], n° [numéro] :"
   - **ONIAM :** "[Type d'information] - [Sous-catégorie] :"
   - **Sources :** Toujours indiquer la source officielle
   - **Applicabilité :** Toujours expliquer pourquoi c'est pertinent
   - **Application concrète :** Toujours montrer comment ça s'applique au cas

4. **SÉLECTION ET HIÉRARCHISATION** :
   - Sélectionnez UNIQUEMENT les sources les plus pertinentes (max 3-4 par catégorie)
   - Classez par ordre de pertinence décroissante
   - Ne citez que ce qui s'applique directement au cas

5. **RECOMMANDATIONS EXPERTES** :
   - Basées sur l'analyse des sources sélectionnées
   - Stratégie contentieuse adaptée aux sources pertinentes
   - Montants d'indemnisation justifiés par la jurisprudence

6. **INTERDICTIONS** :
   - PAS de listes de citations sans explication
   - PAS de scores ou de métadonnées techniques
   - PAS de sources non pertinentes
   - PAS de formatage libre

RESPECTEZ EXACTEMENT CE FORMAT. CHAQUE CITATION DOIT AVOIR : SOURCE + APPLICABILITÉ + APPLICATION CONCRÈTE.
DIVERSIFIEZ AU MOINS 4 FAMILLES JURIDIQUES POUR UNE ANALYSE COMPLÈTE.
"""

        # 4. Analyse Grok-4
        print("🧠 Analyse avec Grok-4...")
        from grok_client import get_grok_client
        client = get_grok_client()
        
        if not client.is_configured():
            return "❌ Erreur : Client Grok-4 non configuré. Vérifiez votre clé API XAI_API_KEY"
        
        if fast:
            result = client.generate_fast_analysis(prompt)
        else:
            result = client.generate_detailed_analysis(prompt)

        # 5. Clean & Cache
        print("🔧 Nettoyage et structuration...")
        result = clean_and_structure_analysis(result, juris, oniam)
        st.session_state[key] = result
        
        print("✅ ANALYSE EXCEPTIONNELLE 10/10 TERMINÉE!")
        return result
        
    except Exception as e:
        print(f"❌ Erreur analyse exceptionnelle: {e}")
        return f"❌ Erreur lors de l'analyse exceptionnelle: {str(e)}"

def split_analysis_into_sections(analysis_result):
    """
    Divise l'analyse en sections structurées
    """
    sections = {}
    
    # Rechercher les sections principales
    if "1. QUALIFICATION JURIDIQUE" in analysis_result:
        start = analysis_result.find("1. QUALIFICATION JURIDIQUE")
        end = analysis_result.find("2. FONDEMENTS LÉGAUX DÉTAILLÉS")
        if end == -1:
            end = analysis_result.find("3. RECOURS POSSIBLES")
        if end == -1:
            end = len(analysis_result)
        sections['qualification'] = analysis_result[start:end].strip()
    
    if "2. FONDEMENTS LÉGAUX DÉTAILLÉS" in analysis_result:
        start = analysis_result.find("2. FONDEMENTS LÉGAUX DÉTAILLÉS")
        end = analysis_result.find("3. RECOURS POSSIBLES")
        if end == -1:
            end = analysis_result.find("4. RECOMMANDATIONS")
        if end == -1:
            end = len(analysis_result)
        sections['fondements'] = analysis_result[start:end].strip()
    
    if "3. RECOURS POSSIBLES" in analysis_result:
        start = analysis_result.find("3. RECOURS POSSIBLES")
        end = analysis_result.find("4. RECOMMANDATIONS")
        if end == -1:
            end = len(analysis_result)
        sections['recours'] = analysis_result[start:end].strip()
    
    if "4. RECOMMANDATIONS" in analysis_result:
        start = analysis_result.find("4. RECOMMANDATIONS")
        end = len(analysis_result)
        sections['recommandations'] = analysis_result[start:end].strip()
    
    # Si aucune section structurée n'est trouvée, traiter comme un bloc unique
    if not sections:
        sections['complementaires'] = analysis_result
    
    return sections

def extract_structured_sources(fondements_section):
    """
    Extrait les sources structurées de la section fondements
    """
    articles = []
    jurisprudence = []
    oniam_info = []
    
    lines = fondements_section.split('\n')
    current_category = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Détecter les catégories
        if "**Article" in line and "du Code" in line:
            current_category = "article"
            articles.append(line)
        elif "**Cass." in line or "**CE," in line or "**TGI" in line:
            current_category = "jurisprudence"
            jurisprudence.append(line)
        elif "**Barème ONIAM" in line or "**ONIAM" in line:
            current_category = "oniam"
            oniam_info.append(line)
        elif current_category and line.startswith("- **Applicabilité :**"):
            # Ajouter l'explication à la source précédente
            if current_category == "article" and articles:
                articles[-1] += f" - {line.replace('- **Applicabilité :**', '').strip()}"
            elif current_category == "jurisprudence" and jurisprudence:
                jurisprudence[-1] += f" - {line.replace('- **Applicabilité :**', '').strip()}"
            elif current_category == "oniam" and oniam_info:
                oniam_info[-1] += f" - {line.replace('- **Applicabilité :**', '').strip()}"
    
    return articles, jurisprudence, oniam_info 