#!/usr/bin/env python3
"""
Configuration pour Streamlit Cloud - Version sans ChromaDB
"""

import os
import streamlit as st

# Désactiver ChromaDB pour éviter l'erreur sentencepiece
os.environ['DISABLE_CHROMADB'] = 'true'

# Configuration de la page
st.set_page_config(
    page_title="LegalDocBot - Assistant Juridique",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import et lancement de l'application principale
try:
    from medical_legal_bot_grok import main
    main()
except ImportError as e:
    st.error(f"❌ Erreur d'import: {e}")
    st.info("Vérifiez que tous les modules sont installés")
except Exception as e:
    st.error(f"❌ Erreur lors du lancement: {e}")
    st.info("Consultez les logs pour plus de détails") 