"""
Module de génération de lettres et plaidoiries juridiques
Intégré dans LegalDocBot pour la génération de documents professionnels
"""

import streamlit as st
from datetime import datetime

# Configuration des types de lettres
LETTER_TYPES = {
    "cci": {
        "name": "Commission de Conciliation et d'Indemnisation",
        "description": "Lettre pour saisir la CCI en cas de dommage médical"
    },
    "oniam": {
        "name": "Office National d'Indemnisation des Accidents Médicaux",
        "description": "Lettre pour l'ONIAM en cas d'aléa thérapeutique"
    },
    "insurance": {
        "name": "Assurance Responsabilité Civile",
        "description": "Lettre pour l'assurance en cas de dommage"
    },
    "commission_usagers": {
        "name": "Commission des Usagers",
        "description": "Lettre pour la commission des usagers de l'établissement"
    },
    "ars": {
        "name": "Agence Régionale de Santé",
        "description": "Lettre pour l'ARS en cas de dysfonctionnement"
    },
    "defenseur_droits": {
        "name": "Défenseur des Droits",
        "description": "Lettre pour le Défenseur des Droits"
    },
    "has": {
        "name": "Haute Autorité de Santé",
        "description": "Lettre pour la HAS"
    },
    "cnam": {
        "name": "Caisse Nationale d'Assurance Maladie",
        "description": "Lettre pour la CNAM"
    },
    "tribunal_administratif": {
        "name": "Tribunal Administratif",
        "description": "Lettre pour le tribunal administratif"
    }
}

# Configuration des types de plaidoiries
PLEA_TYPES = {
    "cci": {
        "name": "Plaidoirie CCI",
        "description": "Plaidoirie pour la Commission de Conciliation et d'Indemnisation"
    },
    "oniam": {
        "name": "Plaidoirie ONIAM",
        "description": "Plaidoirie pour l'Office National d'Indemnisation"
    },
    "commission_usagers": {
        "name": "Plaidoirie Commission Usagers",
        "description": "Plaidoirie pour la commission des usagers"
    },
    "tribunal": {
        "name": "Plaidoirie Tribunal",
        "description": "Plaidoirie générale pour tribunal"
    }
}

def generate_professional_letter(situation, analysis_result, letter_type="cci", additional_info=""):
    """
    Génère une lettre professionnelle basée sur l'analyse juridique
    
    Args:
        situation (str): Description de la situation
        analysis_result (str): Résultat de l'analyse juridique
        letter_type (str): Type de lettre (cci, oniam, etc.)
        additional_info (str): Informations supplémentaires
    
    Returns:
        str: Lettre générée
    """
    try:
        # En-tête de la lettre
        header = f"""
        {datetime.now().strftime('%d/%m/%Y')}
        
        {LETTER_TYPES[letter_type]['name']}
        Objet : Demande d'indemnisation - {letter_type.upper()}
        
        Madame, Monsieur,
        """
        
        # Corps de la lettre selon le type
        if letter_type == "cci":
            body = f"""
        Par la présente, je me permets de vous saisir concernant un dommage médical survenu lors de ma prise en charge.

        SITUATION :
        {situation}

        ANALYSE JURIDIQUE :
        {analysis_result}

        {additional_info if additional_info else ""}

        En conséquence, je vous prie de bien vouloir examiner ma demande d'indemnisation et me faire connaître votre décision dans les meilleurs délais.

        Je reste à votre disposition pour tout complément d'information que vous pourriez souhaiter.
        """
        
        elif letter_type == "oniam":
            body = f"""
        Par la présente, je me permets de vous saisir concernant un aléa thérapeutique survenu lors de ma prise en charge.

        SITUATION :
        {situation}

        ANALYSE JURIDIQUE :
        {analysis_result}

        {additional_info if additional_info else ""}

        Conformément à la loi du 4 mars 2002, je sollicite l'indemnisation de ce préjudice au titre de la solidarité nationale.

        Je vous prie de bien vouloir examiner ma demande et me faire connaître votre décision.
        """
        
        elif letter_type == "insurance":
            body = f"""
        Par la présente, je me permets de vous saisir concernant un dommage survenu dans le cadre de votre garantie.

        SITUATION :
        {situation}

        ANALYSE JURIDIQUE :
        {analysis_result}

        {additional_info if additional_info else ""}

        Je vous prie de bien vouloir examiner ma demande d'indemnisation et me faire connaître votre décision dans les meilleurs délais.
        """
        
        else:
            # Lettre générique pour les autres types
            body = f"""
        Par la présente, je me permets de vous saisir concernant la situation suivante.

        SITUATION :
        {situation}

        ANALYSE JURIDIQUE :
        {analysis_result}

        {additional_info if additional_info else ""}

        Je vous prie de bien vouloir examiner ma demande et me faire connaître votre décision dans les meilleurs délais.
        """
        
        # Signature
        signature = """
        Je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.

        [Votre nom]
        [Votre adresse]
        [Téléphone]
        [Email]
        """
        
        return (header + body + signature).strip()
        
    except Exception as e:
        return f"Erreur lors de la génération de la lettre : {str(e)}"

def generate_exceptional_plea(situation, analysis_result, plea_type="cci", additional_info=""):
    """
    Génère un plaidoyer exceptionnel basé sur l'analyse juridique
    
    Args:
        situation (str): Description de la situation
        analysis_result (str): Résultat de l'analyse juridique
        plea_type (str): Type de plaidoirie
        additional_info (str): Informations supplémentaires
    
    Returns:
        str: Plaidoyer généré
    """
    try:
        # En-tête du plaidoyer
        header = f"""
        PLAIDOYER {PLEA_TYPES[plea_type]['name'].upper()}
        
        Date : {datetime.now().strftime('%d/%m/%Y')}
        """
        
        # Corps du plaidoyer selon le type
        if plea_type == "cci":
            body = f"""
        EXPOSÉ DES FAITS :
        
        {situation}

        ANALYSE JURIDIQUE :
        {analysis_result}

        {additional_info if additional_info else ""}

        MOYENS :
        
        1. Sur la responsabilité médicale :
        Les faits établissent une faute dans la prise en charge médicale, constitutive d'un dommage indemnisable.

        2. Sur le préjudice :
        Le préjudice subi est certain, direct et légitime, justifiant une indemnisation intégrale.

        3. Sur la causalité :
        Il existe un lien de causalité direct entre la faute commise et le préjudice subi.

        CONCLUSION :
        
        Il est demandé à la Commission de bien vouloir reconnaître la responsabilité médicale et accorder une indemnisation équitable du préjudice subi.

        Fait pour valoir ce que de droit.
        """
        
        elif plea_type == "oniam":
            body = f"""
        EXPOSÉ DES FAITS :
        
        {situation}

        ANALYSE JURIDIQUE :
        {analysis_result}

        {additional_info if additional_info else ""}

        MOYENS :
        
        1. Sur l'aléa thérapeutique :
        Les faits établissent un aléa thérapeutique indemnisable au titre de la solidarité nationale.

        2. Sur le préjudice :
        Le préjudice subi est certain, direct et légitime, justifiant une indemnisation intégrale.

        3. Sur l'application de la loi du 4 mars 2002 :
        L'aléa thérapeutique est indemnisable sans faute, au titre de la solidarité nationale.

        CONCLUSION :
        
        Il est demandé à l'ONIAM de bien vouloir reconnaître l'aléa thérapeutique et accorder une indemnisation équitable.

        Fait pour valoir ce que de droit.
        """
        
        else:
            # Plaidoyer générique
            body = f"""
        EXPOSÉ DES FAITS :
        
        {situation}

        ANALYSE JURIDIQUE :
        {analysis_result}

        {additional_info if additional_info else ""}

        MOYENS :
        
        1. Sur les faits :
        Les faits établissent un préjudice indemnisable.

        2. Sur le droit :
        Le préjudice subi est certain, direct et légitime, justifiant une indemnisation intégrale.

        3. Sur la responsabilité :
        La responsabilité est engagée et justifie une indemnisation équitable.

        CONCLUSION :
        
        Il est demandé de bien vouloir reconnaître la responsabilité et accorder une indemnisation équitable.

        Fait pour valoir ce que de droit.
        """
        
        return (header + body).strip()
        
    except Exception as e:
        return f"Erreur lors de la génération du plaidoyer : {str(e)}"

def export_letter_to_pdf(letter_data):
    """
    Exporte une lettre en PDF (simulation)
    
    Args:
        letter_data (dict): Données de la lettre
    
    Returns:
        str: Données PDF encodées en base64
    """
    try:
        # Simulation d'export PDF
        pdf_content = f"""
        LETTRE {letter_data['letter_type']}
        
        {letter_data['letter']}
        """
        
        # Encodage en base64 (simulation)
        import base64
        return base64.b64encode(pdf_content.encode()).decode()
        
    except Exception as e:
        return f"Erreur lors de l'export PDF : {str(e)}"

def export_plea_to_pdf(plea_data):
    """
    Exporte un plaidoyer en PDF (simulation)
    
    Args:
        plea_data (dict): Données du plaidoyer
    
    Returns:
        str: Données PDF encodées en base64
    """
    try:
        # Simulation d'export PDF
        pdf_content = f"""
        PLAIDOYER {plea_data['plea_type']}
        
        {plea_data['plea']}
        """
        
        # Encodage en base64 (simulation)
        import base64
        return base64.b64encode(pdf_content.encode()).decode()
        
    except Exception as e:
        return f"Erreur lors de l'export PDF : {str(e)}" 