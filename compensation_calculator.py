"""
Calculateur d'indemnisation dynamique pour LegalDocBot
Basé sur les barèmes ONIAM 2024 et la jurisprudence française
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple
from datetime import date
import json

# ============================================================================
# BARÈMES ONIAM 2024 (SIMPLIFIÉS)
# ============================================================================

ONIAM_BAREMES_2024 = {
    "death": {
        "name": "Décès",
        "base_range": (15000, 150000),
        "age_factors": {
            "0-15": 1.5,    # Multiplicateur pour enfants
            "16-25": 1.3,   # Multiplicateur pour jeunes adultes
            "26-65": 1.0,   # Multiplicateur standard
            "66+": 0.8      # Multiplicateur pour personnes âgées
        },
        "dependents_bonus": 0.2  # +20% par personne à charge
    },
    
    "permanent_disability": {
        "name": "Incapacité Permanente",
        "base_range": (5000, 100000),
        "severity_levels": {
            "very_light": (5000, 15000),    # 1-5%
            "light": (15000, 30000),        # 6-15%
            "moderate": (30000, 60000),     # 16-30%
            "severe": (60000, 100000),      # 31-50%
            "very_severe": (100000, 200000) # 51%+
        }
    },
    
    "temporary_injury": {
        "name": "Incapacité Temporaire",
        "base_range": (1000, 50000),
        "duration_factors": {
            "1-7_days": 1.0,
            "8-30_days": 1.5,
            "1-3_months": 2.0,
            "3-6_months": 2.5,
            "6+_months": 3.0
        }
    },
    
    "loss_of_chance": {
        "name": "Perte de Chance",
        "base_range": (2000, 80000),
        "chance_percentages": {
            "10-25%": (2000, 15000),
            "26-50%": (15000, 35000),
            "51-75%": (35000, 60000),
            "76-90%": (60000, 80000)
        }
    },
    
    "moral_damage": {
        "name": "Préjudice Moral",
        "base_range": (3000, 25000),
        "severity_factors": {
            "light": 1.0,
            "moderate": 1.5,
            "severe": 2.0,
            "very_severe": 2.5
        }
    }
}

# ============================================================================
# FACTEURS RÉGIONAUX (COURTS D'APPELLATION)
# ============================================================================

REGIONAL_FACTORS = {
    "paris": 1.3,      # Cour d'appel de Paris
    "lyon": 1.2,       # Cour d'appel de Lyon
    "marseille": 1.1,  # Cour d'appel de Marseille
    "toulouse": 1.0,   # Cour d'appel de Toulouse
    "bordeaux": 1.0,   # Cour d'appel de Bordeaux
    "nantes": 0.9,     # Cour d'appel de Nantes
    "rennes": 0.9,     # Cour d'appel de Rennes
    "other": 1.0       # Autres cours
}

# ============================================================================
# CLASSE PRINCIPALE DU CALCULATEUR
# ============================================================================

class CompensationCalculator:
    """
    Calculateur d'indemnisation basé sur les barèmes ONIAM 2024
    """
    
    def __init__(self):
        self.baremes = ONIAM_BAREMES_2024
        self.regional_factors = REGIONAL_FACTORS
    
    def calculate_age_factor(self, age: int) -> float:
        """Calcule le facteur multiplicateur selon l'âge"""
        if age <= 15:
            return self.baremes["death"]["age_factors"]["0-15"]
        elif age <= 25:
            return self.baremes["death"]["age_factors"]["16-25"]
        elif age <= 65:
            return self.baremes["death"]["age_factors"]["26-65"]
        else:
            return self.baremes["death"]["age_factors"]["66+"]
    
    def calculate_death_compensation(self, age: int, dependents: int = 0, region: str = "other") -> Dict:
        """Calcule l'indemnisation pour décès"""
        base_min, base_max = self.baremes["death"]["base_range"]
        age_factor = self.calculate_age_factor(age)
        dependents_bonus = 1 + (dependents * self.baremes["death"]["dependents_bonus"])
        regional_factor = self.regional_factors.get(region, 1.0)
        
        # Calcul de base
        base_compensation = (base_min + base_max) / 2
        
        # Application des facteurs
        final_compensation = base_compensation * age_factor * dependents_bonus * regional_factor
        
        return {
            "type": "death",
            "base_amount": base_compensation,
            "age_factor": age_factor,
            "dependents_bonus": dependents_bonus,
            "regional_factor": regional_factor,
            "final_amount": round(final_compensation, 2),
            "range": (round(base_min * age_factor * dependents_bonus * regional_factor, 2),
                     round(base_max * age_factor * dependents_bonus * regional_factor, 2))
        }
    
    def calculate_disability_compensation(self, severity: str, age: int, region: str = "other") -> Dict:
        """Calcule l'indemnisation pour incapacité permanente"""
        if severity not in self.baremes["permanent_disability"]["severity_levels"]:
            return {"error": "Niveau de sévérité invalide"}
        
        base_min, base_max = self.baremes["permanent_disability"]["severity_levels"][severity]
        age_factor = self.calculate_age_factor(age)
        regional_factor = self.regional_factors.get(region, 1.0)
        
        # Calcul de base
        base_compensation = (base_min + base_max) / 2
        
        # Application des facteurs
        final_compensation = base_compensation * age_factor * regional_factor
        
        return {
            "type": "permanent_disability",
            "severity": severity,
            "base_amount": base_compensation,
            "age_factor": age_factor,
            "regional_factor": regional_factor,
            "final_amount": round(final_compensation, 2),
            "range": (round(base_min * age_factor * regional_factor, 2),
                     round(base_max * age_factor * regional_factor, 2))
        }
    
    def calculate_loss_of_chance(self, chance_percentage: int, region: str = "other") -> Dict:
        """Calcule l'indemnisation pour perte de chance"""
        if chance_percentage <= 10:
            return {"error": "Perte de chance trop faible pour être indemnisable"}
        elif chance_percentage <= 25:
            range_key = "10-25%"
        elif chance_percentage <= 50:
            range_key = "26-50%"
        elif chance_percentage <= 75:
            range_key = "51-75%"
        elif chance_percentage <= 90:
            range_key = "76-90%"
        else:
            return {"error": "Perte de chance trop élevée (probablement indemnisable à 100%)"}
        
        base_min, base_max = self.baremes["loss_of_chance"]["chance_percentages"][range_key]
        regional_factor = self.regional_factors.get(region, 1.0)
        
        # Calcul proportionnel selon le pourcentage
        if range_key == "10-25%":
            factor = (chance_percentage - 10) / 15
        elif range_key == "26-50%":
            factor = (chance_percentage - 26) / 24
        elif range_key == "51-75%":
            factor = (chance_percentage - 51) / 24
        else:  # 76-90%
            factor = (chance_percentage - 76) / 14
        
        base_compensation = base_min + (base_max - base_min) * factor
        final_compensation = base_compensation * regional_factor
        
        return {
            "type": "loss_of_chance",
            "chance_percentage": chance_percentage,
            "base_amount": base_compensation,
            "regional_factor": regional_factor,
            "final_amount": round(final_compensation, 2),
            "range": (round(base_min * regional_factor, 2),
                     round(base_max * regional_factor, 2))
        }
    
    def calculate_total_compensation(self, damages: List[Dict]) -> Dict:
        """Calcule l'indemnisation totale pour plusieurs préjudices"""
        total = 0
        breakdown = []
        
        for damage in damages:
            if "final_amount" in damage:
                total += damage["final_amount"]
                breakdown.append(damage)
            elif "error" in damage:
                breakdown.append(damage)
        
        return {
            "total_compensation": round(total, 2),
            "breakdown": breakdown,
            "count": len([d for d in breakdown if "final_amount" in d])
        }

# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================

def display_compensation_calculator():
    """
    Interface Streamlit pour le calculateur d'indemnisation
    """
    st.markdown("---")
    st.markdown("### 💰 Calculateur d'Indemnisation ONIAM 2024")
    st.markdown("*Basé sur les barèmes officiels et la jurisprudence française*")
    
    # Initialisation du calculateur
    calculator = CompensationCalculator()
    
    # Sélection du type de préjudice avec bouton aligné à droite
    with st.container():
        cols = st.columns([2, 1, 1])   # 3 colonnes : type, région, bouton
        with cols[0]:
            damage_type = st.selectbox(
                "🎯 Type de Préjudice",
                options=["death", "permanent_disability", "loss_of_chance", "multiple"],
                format_func=lambda x: {
                    "death": "Décès",
                    "permanent_disability": "Incapacité Permanente", 
                    "loss_of_chance": "Perte de Chance",
                    "multiple": "Préjudices Multiples"
                }[x]
            )
        
        with cols[1]:
            region = st.selectbox(
                "🏛️ Région",
                options=list(REGIONAL_FACTORS.keys()),
                format_func=lambda x: {
                    "paris": "Paris (CA Paris)",
                    "lyon": "Lyon (CA Lyon)",
                    "marseille": "Marseille (CA Marseille)",
                    "toulouse": "Toulouse (CA Toulouse)",
                    "bordeaux": "Bordeaux (CA Bordeaux)",
                    "nantes": "Nantes (CA Nantes)",
                    "rennes": "Rennes (CA Rennes)",
                    "other": "Autre région"
                }[x]
            )
        
        with cols[2]:
            calculate_clicked = st.button("🧮 Calculer", type="primary", use_container_width=False, key="calculate_main")
    
    # Calcul selon le type de préjudice
    if damage_type == "death":
        st.markdown("#### 💀 Indemnisation pour Décès")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            age = st.number_input("👤 Âge de la victime", min_value=0, max_value=120, value=45)
        
        with col2:
            dependents = st.number_input("👨‍👩‍👧‍👦 Personnes à charge", min_value=0, max_value=10, value=2)
        
        # Logique de calcul pour décès
        if calculate_clicked:
            result = calculator.calculate_death_compensation(age, dependents, region)
            
            if "error" not in result:
                st.session_state.compensation_result = result
                st.success("✅ Calcul terminé !")
                st.rerun()   # rafraîchit pour afficher le résultat immédiatement
            else:
                st.error(f"❌ {result['error']}")
    
    elif damage_type == "permanent_disability":
        st.markdown("#### 🦽 Indemnisation pour Incapacité Permanente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            severity = st.selectbox(
                "📊 Niveau de Sévérité",
                options=list(ONIAM_BAREMES_2024["permanent_disability"]["severity_levels"].keys()),
                format_func=lambda x: {
                    "very_light": "Très légère (1-5%)",
                    "light": "Légère (6-15%)",
                    "moderate": "Modérée (16-30%)",
                    "severe": "Sévère (31-50%)",
                    "very_severe": "Très sévère (51%+)"
                }[x]
            )
        
        with col2:
            age = st.number_input("👤 Âge de la victime", min_value=0, max_value=120, value=45)
        
        if st.button("🧮 Calculer", type="primary", key="calculate_disability"):
            result = calculator.calculate_disability_compensation(severity, age, region)
            
            if "error" not in result:
                st.session_state.compensation_result = result
                st.success("✅ Calcul terminé !")
            else:
                st.error(f"❌ {result['error']}")
    
    elif damage_type == "loss_of_chance":
        st.markdown("#### 🎯 Indemnisation pour Perte de Chance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            chance_percentage = st.slider(
                "📈 Pourcentage de chance perdue",
                min_value=5,
                max_value=95,
                value=30,
                help="Pourcentage de chance de guérison ou de survie perdue"
            )
        
        with col2:
            if st.button("🧮 Calculer", type="primary", key="calculate_loss_of_chance"):
                result = calculator.calculate_loss_of_chance(chance_percentage, region)
                
                if "error" not in result:
                    st.session_state.compensation_result = result
                    st.success("✅ Calcul terminé !")
                else:
                    st.error(f"❌ {result['error']}")
    
    # Affichage des résultats
    if hasattr(st.session_state, 'compensation_result') and st.session_state.compensation_result:
        result = st.session_state.compensation_result
        
        st.markdown("---")
        st.markdown("### 📊 Résultats du Calcul")
        
        # Métriques principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "💰 Indemnisation",
                f"{result['final_amount']:,} €",
                help="Montant calculé selon les barèmes ONIAM 2024"
            )
        
        with col2:
            if "range" in result:
                st.metric(
                    "📈 Fourchette",
                    f"{result['range'][0]:,} - {result['range'][1]:,} €",
                    help="Fourchette d'indemnisation possible"
                )
        
        with col3:
            if "age_factor" in result:
                st.metric(
                    "👤 Facteur Âge",
                    f"{result['age_factor']:.2f}x",
                    help="Multiplicateur selon l'âge de la victime"
                )
        
        # Détails du calcul
        with st.expander("🔍 Détails du Calcul"):
            st.json(result)
        
        # Boutons d'action
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Exporter PDF", key="export_pdf"):
                st.info("🔄 Fonctionnalité d'export PDF en cours de développement")
        
        with col2:
            if st.button("🔄 Nouveau Calcul", key="new_calculation"):
                del st.session_state.compensation_result
                st.rerun()

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_regional_courts() -> Dict[str, str]:
    """Retourne la liste des cours d'appel par région"""
    return {
        "paris": "Cour d'appel de Paris",
        "lyon": "Cour d'appel de Lyon", 
        "marseille": "Cour d'appel de Marseille",
        "toulouse": "Cour d'appel de Toulouse",
        "bordeaux": "Cour d'appel de Bordeaux",
        "nantes": "Cour d'appel de Nantes",
        "rennes": "Cour d'appel de Rennes"
    }

def validate_compensation_inputs(age: int, severity: str = None, chance_percentage: int = None) -> Dict[str, bool]:
    """Valide les entrées du calculateur"""
    checks = {
        "age_valid": 0 <= age <= 120,
        "severity_valid": severity is None or severity in ONIAM_BAREMES_2024["permanent_disability"]["severity_levels"],
        "chance_valid": chance_percentage is None or (5 <= chance_percentage <= 95)
    }
    
    return checks 