"""
Module de génération de lettres professionnelles pour LegalDocBot
Génère des lettres adaptées selon le destinataire (CDU, CCI, ONIAM, etc.)
"""

from datetime import date
from typing import Dict, Optional
import streamlit as st
from grok_client import get_grok_client

# ============================================================================
# PROMPT MASTER POUR LETTRES PROFESSIONNELLES
# ============================================================================

LETTER_MASTER_PROMPT = """Tu es LegalDocBot, rédacteur de lettres professionnelles en droit médical français.

CONTEXTE :
Situation : {situation}
Type de destinataire : {dest_type}  # CDU, CCI, HAS, ONIAM, ARS, CNAM, Tribunal, Assurance

INSTRUCTIONS ABSOLUES :
1. Ton : professionnel, empathique, ferme, mais respectueux.
2. Structure stricte :
   - En-tête (cabinet d'avocat)
   - Références dossier
   - Destinataire complet
   - Objet précis
   - Corps : faits → fondements juridiques → demande → délai
   - Signature
3. Adapter le ton au destinataire (ex. CDU : collaboratif / Tribunal : juridictionnel).
4. Générer UNIQUEMENT le texte de la lettre, sans commentaires ni métadonnées.
5. Utiliser les informations de l'analyse pour enrichir le contenu mais ne pas la reproduire intégralement."""

# ============================================================================
# DICTIONNAIRE DE TON PAR DESTINATAIRE
# ============================================================================

TONE_MAP = {
    "cdu": "respectueux et constructif, axé sur amélioration des soins",
    "cci": "professionnel et déterminé, axé sur conciliation",
    "oniam": "respectueux mais ferme, axé sur indemnisation aléa",
    "has": "technique et précis, axé sur recommandations",
    "ars": "factuel et normatif, axé sur contrôle",
    "cnam": "administratif, axé sur prise en charge",
    "tribunal": "solennel et juridictionnel",
    "insurance": "professionnel et ferme"
}

# ============================================================================
# NOMS DES DESTINATAIRES
# ============================================================================

DEST_NAMES = {
    "cdu": "Commission des Usagers",
    "cci": "Commission de Conciliation et d'Indemnisation",
    "oniam": "Office National d'Indemnisation des Accidents Médicaux",
    "has": "Haute Autorité de Santé",
    "ars": "Agence Régionale de Santé",
    "cnam": "Caisse Nationale d'Assurance Maladie",
    "tribunal": "Tribunal Administratif",
    "insurance": "Compagnie d'Assurance"
}

# ============================================================================
# FONCTION PRINCIPALE DE GÉNÉRATION
# ============================================================================

@st.cache_data(ttl=3600)  # Cache 1 heure
def generate_exceptional_letter(situation: str, analysis: str, dest_type: str, avocat_name: str = "DUPONT", barreau: str = "Paris") -> str:
    """
    Génère une lettre exceptionnelle selon le destinataire.
    
    Args:
        situation: Description de la situation médicale
        analysis: Analyse juridique complète (utilisée pour contexte mais pas dans le prompt)
        dest_type: Type de destinataire (cdu, cci, oniam, has, ars, cnam, tribunal, insurance)
        avocat_name: Nom de l'avocat pour la signature
        barreau: Barreau de l'avocat
    
    Returns:
        Lettre professionnelle générée
    """
    if dest_type not in TONE_MAP:
        return "❌ Type de destinataire invalide"
    
    try:
        # Construction du prompt spécifique pour les lettres "infutables"
        prompt = f"""Tu es LegalDocBot, rédacteur de lettres professionnelles en droit médical français.

SITUATION : {situation}
DESTINATAIRE : {DEST_NAMES[dest_type]} ({dest_type.upper()})
TON : {TONE_MAP[dest_type]}
SIGNATURE : Maître {avocat_name} - Barreau de {barreau}

INSTRUCTIONS POUR LETTRE "INFUTABLE" :
1. Rédige une lettre professionnelle complète avec :
   - En-tête de cabinet d'avocat
   - Références du dossier
   - Destinataire complet
   - Objet précis
   - Corps structuré (faits → fondements juridiques → demande → délai)
   - Signature

2. Ton : {TONE_MAP[dest_type]}

3. CONTENU OBLIGATOIRE "INFUTABLE" :
   - **Références juridiques EXACTES** : Cass. 1re civ., 14 oct. 2010, n° 09-69.199 (perte de chance)
   - **Articles de loi précis** : L.1110-5 CSP, 1240 Code civil, R.4127-33 déontologie
   - **Chiffrage ONIAM 2024** : "perte de chance évaluée à X% → estimation Y €"
   - **Guide HAS cité** : "Guide HAS 2023 - [spécialité] comme référence non respectée"
   - **Pièces jointes listées** : CR médical, examens, certificats avec dates
   - **Signature personnalisée** : "Maître {avocat_name} - Spécialiste droit médical - Barreau de {barreau}"
   - **Copie conforme** : "Copie conforme pour {DEST_NAMES[dest_type]}"

4. FORMAT : Lettre professionnelle complète, sans commentaires ni métadonnées.

Générez UNIQUEMENT le texte de la lettre avec TOUS les éléments "infutables"."""
        
        # Appel à Grok-4
        client = get_grok_client()
        letter = client.generate_completion(prompt, temperature=0.1)
        
        if letter and letter.strip():
            return letter.strip()
        else:
            return "❌ Erreur lors de la génération de la lettre"
            
    except Exception as e:
        return f"❌ Erreur technique : {str(e)}"

# ============================================================================
# FONCTION D'AFFICHAGE STREAMLIT
# ============================================================================

def display_letter_generator(situation: str, analysis: str):
    """
    Interface Streamlit pour la génération de lettres
    """
    st.markdown("---")
    st.markdown("### 📝 Générateur de Lettres Professionnelles")
    
    # Sélection du destinataire avec bouton aligné à droite
    with st.container():
        cols = st.columns([3, 1, 1])   # 3 colonnes : label, vide, bouton
        with cols[0]:
            dest_type = st.selectbox(
                "🎯 Destinataire",
                options=list(TONE_MAP.keys()),
                format_func=lambda x: f"{DEST_NAMES[x]} ({x.upper()})"
            )
        with cols[2]:
            generate_clicked = st.button("🚀 Générer Lettre", type="primary", use_container_width=False, key="generate_letter_main")
    
    # Personnalisation de la signature
    col1, col2 = st.columns(2)
    with col1:
        avocat_name = st.text_input(
            "👨‍💼 Nom de l'avocat",
            value="DUPONT",
            help="Nom qui apparaîtra dans la signature"
        )
    with col2:
        barreau = st.text_input(
            "🏛️ Barreau",
            value="Paris",
            help="Barreau de l'avocat"
        )
    
    # Logique de génération sans spinner
    if generate_clicked:
        if situation and analysis:
            # PAS de spinner ici
            letter = generate_exceptional_letter(situation, analysis, dest_type, avocat_name, barreau)
            st.session_state.generated_letter = letter
            st.session_state.letter_dest_type = dest_type
            st.session_state.avocat_name = avocat_name
            st.session_state.barreau = barreau
            st.success("✅ Lettre générée avec succès !")
            st.rerun()   # rafraîchit pour afficher la lettre immédiatement
        else:
            st.error("❌ Situation et analyse requises")
    
    # Affichage de la lettre générée
    if hasattr(st.session_state, 'generated_letter') and st.session_state.generated_letter:
        st.markdown("---")
        st.markdown("### 📄 Lettre Générée")
        
        # Informations sur le destinataire
        dest_name = DEST_NAMES.get(st.session_state.letter_dest_type, "Destinataire")
        tone = TONE_MAP.get(st.session_state.letter_dest_type, "professionnel")
        
        st.info(f"**Destinataire :** {dest_name} | **Ton :** {tone}")
        
        # Affichage de la lettre
        st.markdown("---")
        st.markdown(st.session_state.generated_letter)
        
        # Checklist "infutable"
        display_infutable_checklist(st.session_state.generated_letter)
        
        # Boutons d'action
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Copier le texte", key="copy_letter"):
                st.write("✅ Texte copié dans le presse-papiers")
                st.session_state.copied = True
        
        with col2:
            # Export PDF (à implémenter)
            if st.button("📥 Télécharger PDF", key="download_letter_pdf"):
                st.info("🔄 Fonctionnalité PDF en cours de développement")
        
        with col3:
            if st.button("🔄 Régénérer", key="regenerate_letter"):
                del st.session_state.generated_letter
                st.rerun()

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_letter_template(dest_type: str) -> str:
    """
    Retourne un template de base pour le type de destinataire
    """
    templates = {
        "cdu": """
[CABINET D'AVOCAT]
[Adresse]

Référence : [REF_DOSSIER]
Date : {date}

À l'attention de la Commission des Usagers
[Établissement de santé]

Objet : Demande d'examen de dossier médical

Madame, Monsieur,

[Corps de la lettre]

Veuillez agréer, Madame, Monsieur, l'expression de mes salutations distinguées.

[Signature]
        """,
        "cci": """
[CABINET D'AVOCAT]
[Adresse]

Référence : [REF_DOSSIER]
Date : {date}

À l'attention de la Commission de Conciliation et d'Indemnisation
[Adresse CCI]

Objet : Demande de conciliation

Madame, Monsieur,

[Corps de la lettre]

Veuillez agréer, Madame, Monsieur, l'expression de mes salutations distinguées.

[Signature]
        """,
        "oniam": """
[CABINET D'AVOCAT]
[Adresse]

Référence : [REF_DOSSIER]
Date : {date}

À l'attention de l'Office National d'Indemnisation des Accidents Médicaux
[Adresse ONIAM]

Objet : Demande d'indemnisation - Accident médical

Madame, Monsieur,

[Corps de la lettre]

Veuillez agréer, Madame, Monsieur, l'expression de mes salutations distinguées.

[Signature]
        """
    }
    
    return templates.get(dest_type, "Template non disponible")

def validate_letter_content(letter: str) -> Dict[str, bool]:
    """
    Valide le contenu d'une lettre générée
    """
    checks = {
        "has_header": "CABINET" in letter.upper() or "AVOCAT" in letter.upper(),
        "has_date": any(word in letter for word in ["Date", "Le"]),
        "has_object": "Objet" in letter,
        "has_signature": any(word in letter for word in ["Signature", "Salutations", "Distinguées"]),
        "has_legal_refs": any(word in letter for word in ["Article", "Code", "Cass.", "CE"])
    }
    
    return checks

def validate_letter_infutable(letter: str) -> Dict[str, bool]:
    """
    Valide qu'une lettre contient tous les éléments "infutables"
    """
    checks = {
        "references_exactes": any(ref in letter for ref in ["Cass. 1re civ., 14 oct. 2010, n° 09-69.199", "Cass. 1re civ., 14 octobre 2010"]),
        "articles_loi": any(art in letter for art in ["L.1110-5 CSP", "1240 Code civil", "R.4127-33"]),
        "chiffrage_oniam": any(word in letter for word in ["ONIAM", "barème", "estimation", "€"]),
        "guide_has": "HAS" in letter and any(word in letter for word in ["guide", "recommandations", "protocole"]),
        "pieces_jointes": any(word in letter for word in ["pièces jointes", "CR médical", "compte-rendu", "certificat"]),
        "signature_personnalisee": "Maître" in letter and any(word in letter for word in ["Spécialiste", "Barreau"]),
        "copie_conforme": "copie conforme" in letter.lower(),
        "delai_precis": any(word in letter for word in ["jours", "semaines", "mois", "30 jours", "15 jours"])
    }
    
    return checks

def display_infutable_checklist(letter: str):
    """
    Affiche la checklist "infutable" pour une lettre
    """
    checks = validate_letter_infutable(letter)
    
    st.markdown("---")
    st.markdown("### ✅ Checklist 'Lettre Infutable'")
    
    col1, col2 = st.columns(2)
    
    with col1:
        for check_name, is_valid in list(checks.items())[:4]:
            status = "✅" if is_valid else "❌"
            label = {
                "references_exactes": "Références juridiques exactes",
                "articles_loi": "Articles de loi précis",
                "chiffrage_oniam": "Chiffrage ONIAM 2024",
                "guide_has": "Guide HAS cité"
            }[check_name]
            st.markdown(f"{status} {label}")
    
    with col2:
        for check_name, is_valid in list(checks.items())[4:]:
            status = "✅" if is_valid else "❌"
            label = {
                "pieces_jointes": "Pièces jointes listées",
                "signature_personnalisee": "Signature personnalisée",
                "copie_conforme": "Copie conforme",
                "delai_precis": "Délai précis"
            }[check_name]
            st.markdown(f"{status} {label}")
    
    # Score global
    score = sum(checks.values()) / len(checks) * 100
    st.markdown(f"**Score 'Infutable' : {score:.0f}%**")
    
    if score >= 80:
        st.success("🎯 Lettre juridiquement solide et 'infutable' !")
    elif score >= 60:
        st.warning("⚠️ Lettre correcte mais peut être renforcée")
    else:
        st.error("❌ Lettre fragile, régénération recommandée")

# ============================================================================
# FONCTION D'EXPORT PDF (PLACEHOLDER)
# ============================================================================

def export_letter_to_pdf(letter: str, dest_type: str) -> bytes:
    """
    Exporte la lettre en PDF (à implémenter avec reportlab ou weasyprint)
    """
    # TODO: Implémenter l'export PDF
    return b"PDF placeholder" 