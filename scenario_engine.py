"""
Moteur de scénarios pour LegalDocBot
Génère des hypothèses "Et si..." pour préparer les stratégies contentieuses
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple
import random
from grok_client import get_grok_client

# ============================================================================
# SCÉNARIOS PRÉDÉFINIS
# ============================================================================

SCENARIO_TEMPLATES = {
    "delai": {
        "name": "Retard de Diagnostic/Traitement",
        "variations": [
            "Et si le diagnostic avait été posé 2 jours plus tôt ?",
            "Et si le traitement avait été initié 1 semaine plus tôt ?",
            "Et si la consultation spécialisée avait eu lieu 1 mois plus tôt ?",
            "Et si l'examen complémentaire avait été prescrit immédiatement ?"
        ],
        "impact_factors": ["perte de chance", "aggravation", "séquelles"]
    },
    
    "specialiste": {
        "name": "Changement de Spécialiste",
        "variations": [
            "Et si un autre cardiologue avait été consulté ?",
            "Et si un chirurgien plus expérimenté avait opéré ?",
            "Et si un second avis avait été demandé ?",
            "Et si un centre expert avait été sollicité ?"
        ],
        "impact_factors": ["expertise", "technique", "résultat"]
    },
    
    "examen": {
        "name": "Examens Complémentaires",
        "variations": [
            "Et si un scanner avait été réalisé dès le début ?",
            "Et si une IRM avait été prescrite ?",
            "Et si des analyses sanguines complètes avaient été faites ?",
            "Et si une échographie avait été pratiquée ?"
        ],
        "impact_factors": ["diagnostic précoce", "traitement adapté", "prévention"]
    },
    
    "traitement": {
        "name": "Traitement Alternatif",
        "variations": [
            "Et si un autre médicament avait été prescrit ?",
            "Et si la posologie avait été différente ?",
            "Et si une intervention chirurgicale avait été proposée ?",
            "Et si un traitement conservateur avait été choisi ?"
        ],
        "impact_factors": ["efficacité", "effets secondaires", "résultat"]
    },
    
    "information": {
        "name": "Information du Patient",
        "variations": [
            "Et si les risques avaient été clairement expliqués ?",
            "Et si le consentement avait été éclairé ?",
            "Et si les alternatives avaient été présentées ?",
            "Et si le patient avait été informé des complications possibles ?"
        ],
        "impact_factors": ["consentement", "choix éclairé", "responsabilité"]
    },
    
    "surveillance": {
        "name": "Surveillance Post-Traitement",
        "variations": [
            "Et si la surveillance avait été plus rapprochée ?",
            "Et si des contrôles réguliers avaient été programmés ?",
            "Et si une hospitalisation avait été prolongée ?",
            "Et si un suivi spécialisé avait été mis en place ?"
        ],
        "impact_factors": ["détection précoce", "complication", "évolution"]
    }
}

# ============================================================================
# PROMPT POUR ANALYSE DE SCÉNARIO
# ============================================================================

SCENARIO_ANALYSIS_PROMPT = """Tu es LegalDocBot, expert en analyse de scénarios juridiques médicaux.

SITUATION DE BASE :
{situation}

SCÉNARIO HYPOTHÉTIQUE :
{scenario}

ANALYSE JURIDIQUE DE BASE :
{base_analysis}

INSTRUCTIONS :
Analysez l'impact juridique de ce scénario hypothétique en répondant aux questions suivantes :

1. **IMPACT SUR LA RESPONSABILITÉ** :
   - La responsabilité médicale serait-elle engagée différemment ?
   - Quels nouveaux éléments de preuve seraient disponibles ?
   - La faute serait-elle plus ou moins caractérisée ?

2. **IMPACT SUR L'INDEMNISATION** :
   - Le montant de l'indemnisation serait-il différent ?
   - Quels nouveaux préjudices pourraient être indemnisés ?
   - La perte de chance serait-elle évaluée différemment ?

3. **STRATÉGIE CONTENTIEUSE** :
   - Quels arguments juridiques seraient renforcés ?
   - Quels nouveaux moyens de défense seraient disponibles ?
   - La procédure serait-elle différente ?

4. **RECOMMANDATIONS** :
   - Quelles actions préventives recommandez-vous ?
   - Quels éléments de preuve faut-il consolider ?
   - Quelle stratégie contentieuse adopter ?

FORMAT DE RÉPONSE :
- Structure claire avec titres
- Citations d'articles de loi pertinents
- Références à la jurisprudence applicable
- Recommandations concrètes et actionnables

Générez UNIQUEMENT l'analyse juridique, sans commentaires supplémentaires."""

# ============================================================================
# CLASSE PRINCIPALE DU MOTEUR DE SCÉNARIOS
# ============================================================================

class ScenarioEngine:
    """
    Moteur de génération et d'analyse de scénarios hypothétiques
    """
    
    def __init__(self):
        self.templates = SCENARIO_TEMPLATES
        self.client = get_grok_client()
    
    def generate_scenarios(self, situation: str, scenario_types: List[str] = None) -> List[Dict]:
        """
        Génère des scénarios hypothétiques basés sur la situation
        """
        if scenario_types is None:
            scenario_types = list(self.templates.keys())
        
        scenarios = []
        
        for scenario_type in scenario_types:
            if scenario_type in self.templates:
                template = self.templates[scenario_type]
                
                # Sélection aléatoire d'une variation
                variation = random.choice(template["variations"])
                
                scenario = {
                    "type": scenario_type,
                    "name": template["name"],
                    "question": variation,
                    "impact_factors": template["impact_factors"],
                    "description": self._generate_scenario_description(variation, situation)
                }
                
                scenarios.append(scenario)
        
        return scenarios
    
    def _generate_scenario_description(self, question: str, situation: str) -> str:
        """
        Génère une description détaillée du scénario
        """
        # Analyse rapide de la situation pour adapter le scénario
        medical_keywords = ["diagnostic", "traitement", "chirurgie", "médicament", "examen"]
        found_keywords = [kw for kw in medical_keywords if kw.lower() in situation.lower()]
        
        if "diagnostic" in found_keywords:
            return f"Ce scénario explore l'impact d'un {question.lower()}. Cela pourrait modifier la chronologie des événements et potentiellement améliorer le pronostic du patient."
        elif "traitement" in found_keywords:
            return f"Ce scénario examine les conséquences d'un {question.lower()}. Cela pourrait influencer l'efficacité du traitement et les résultats obtenus."
        else:
            return f"Ce scénario hypothétique analyse l'impact d'un {question.lower()}. Cela pourrait modifier l'évolution de la situation médicale."
    
    def analyze_scenario(self, situation: str, scenario: Dict, base_analysis: str) -> str:
        """
        Analyse l'impact juridique d'un scénario hypothétique
        """
        try:
            # Construction du prompt
            prompt = SCENARIO_ANALYSIS_PROMPT.format(
                situation=situation,
                scenario=scenario["question"],
                base_analysis=base_analysis
            )
            
            # Appel à Grok-4
            analysis = self.client.generate_completion(prompt, temperature=0.3)
            
            if analysis and analysis.strip():
                return analysis.strip()
            else:
                return "❌ Erreur lors de l'analyse du scénario"
                
        except Exception as e:
            return f"❌ Erreur technique : {str(e)}"
    
    def get_scenario_impact_score(self, scenario_analysis: str) -> Dict[str, float]:
        """
        Calcule un score d'impact pour le scénario
        """
        scores = {
            "responsabilite": 0.0,
            "indemnisation": 0.0,
            "strategie": 0.0
        }
        
        # Analyse simple basée sur les mots-clés
        if "responsabilité" in scenario_analysis.lower() or "faute" in scenario_analysis.lower():
            scores["responsabilite"] += 0.3
        
        if "indemnisation" in scenario_analysis.lower() or "préjudice" in scenario_analysis.lower():
            scores["indemnisation"] += 0.3
        
        if "stratégie" in scenario_analysis.lower() or "argument" in scenario_analysis.lower():
            scores["strategie"] += 0.3
        
        # Normalisation
        for key in scores:
            scores[key] = min(scores[key], 1.0)
        
        return scores

# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================

def display_scenario_engine(situation: str, base_analysis: str):
    """
    Interface Streamlit pour le moteur de scénarios
    """
    st.markdown("---")
    st.markdown("### 🎭 Moteur de Scénarios")
    st.markdown("*Générez des hypothèses \"Et si...\" pour préparer vos stratégies contentieuses*")
    
    if not situation or not base_analysis:
        st.warning("⚠️ Veuillez d'abord effectuer une analyse juridique pour générer des scénarios.")
        return
    
    # Initialisation du moteur
    engine = ScenarioEngine()
    
    # Sélection des types de scénarios
    st.markdown("#### 🎯 Types de Scénarios")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_types = st.multiselect(
            "Sélectionnez les types de scénarios à générer :",
            options=list(SCENARIO_TEMPLATES.keys()),
            default=["delai", "specialiste", "examen"],
            format_func=lambda x: SCENARIO_TEMPLATES[x]["name"]
        )
    
    with col2:
        if st.button("🚀 Générer Scénarios", type="primary", key="generate_scenarios"):
            if selected_types:
                with st.spinner("🎭 Génération des scénarios en cours..."):
                    scenarios = engine.generate_scenarios(situation, selected_types)
                    st.session_state.generated_scenarios = scenarios
                st.success(f"✅ {len(scenarios)} scénarios générés !")
            else:
                st.error("❌ Veuillez sélectionner au moins un type de scénario")
    
    # Affichage des scénarios générés
    if hasattr(st.session_state, 'generated_scenarios') and st.session_state.generated_scenarios:
        st.markdown("---")
        st.markdown("#### 📋 Scénarios Générés")
        
        for i, scenario in enumerate(st.session_state.generated_scenarios, 1):
            with st.expander(f"🎭 Scénario {i} : {scenario['name']}"):
                st.markdown(f"**Question :** {scenario['question']}")
                st.markdown(f"**Description :** {scenario['description']}")
                
                # Facteurs d'impact
                st.markdown("**Facteurs d'impact :**")
                for factor in scenario['impact_factors']:
                    st.markdown(f"- {factor}")
                
                # Bouton d'analyse
                if st.button(f"🔍 Analyser Scénario {i}", key=f"analyze_{i}"):
                    with st.spinner("🔍 Analyse juridique du scénario..."):
                        analysis = engine.analyze_scenario(situation, scenario, base_analysis)
                        st.session_state.scenario_analysis = analysis
                        st.session_state.current_scenario = scenario
                    st.success("✅ Analyse terminée !")
        
        # Affichage de l'analyse du scénario sélectionné
        if hasattr(st.session_state, 'scenario_analysis') and st.session_state.scenario_analysis:
            st.markdown("---")
            st.markdown("#### 🔍 Analyse du Scénario")
            
            # Informations sur le scénario analysé
            if hasattr(st.session_state, 'current_scenario'):
                scenario = st.session_state.current_scenario
                st.info(f"**Scénario analysé :** {scenario['question']}")
            
            # Affichage de l'analyse
            st.markdown(st.session_state.scenario_analysis)
            
            # Score d'impact
            scores = engine.get_scenario_impact_score(st.session_state.scenario_analysis)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("⚖️ Impact Responsabilité", f"{scores['responsabilite']:.1%}")
            with col2:
                st.metric("💰 Impact Indemnisation", f"{scores['indemnisation']:.1%}")
            with col3:
                st.metric("🎯 Impact Stratégie", f"{scores['strategie']:.1%}")
            
            # Boutons d'action
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Exporter Analyse", key="export_analysis"):
                    st.info("🔄 Fonctionnalité d'export en cours de développement")
            
            with col2:
                if st.button("🔄 Nouvelle Analyse", key="new_analysis"):
                    del st.session_state.scenario_analysis
                    st.rerun()

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_scenario_statistics(scenarios: List[Dict]) -> Dict:
    """
    Calcule les statistiques des scénarios générés
    """
    if not scenarios:
        return {}
    
    stats = {
        'total_scenarios': len(scenarios),
        'scenario_types': {},
        'impact_factors': set()
    }
    
    for scenario in scenarios:
        # Comptage par type
        scenario_type = scenario['type']
        stats['scenario_types'][scenario_type] = stats['scenario_types'].get(scenario_type, 0) + 1
        
        # Facteurs d'impact uniques
        stats['impact_factors'].update(scenario['impact_factors'])
    
    stats['impact_factors'] = list(stats['impact_factors'])
    
    return stats

def validate_scenario_inputs(situation: str, base_analysis: str) -> Dict[str, bool]:
    """
    Valide les entrées pour la génération de scénarios
    """
    checks = {
        "situation_valid": len(situation.strip()) > 50,
        "analysis_valid": len(base_analysis.strip()) > 100,
        "medical_content": any(word in situation.lower() for word in ["diagnostic", "traitement", "médical", "santé"])
    }
    
    return checks 