"""
Générateur de timeline interactive pour LegalDocBot
Extrait et visualise les événements chronologiques d'une situation médicale
"""

import streamlit as st
import re
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================================
# EXTRACTION D'ÉVÉNEMENTS CHRONOLOGIQUES
# ============================================================================

def extract_timeline_events(situation: str) -> List[Dict]:
    """
    Extrait les événements chronologiques d'une situation médicale
    """
    events = []
    
    # Patterns pour détecter les dates
    date_patterns = [
        r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/YYYY
        r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY
        r'(\d{1,2})\.(\d{1,2})\.(\d{4})', # DD.MM.YYYY
        r'le (\d{1,2})/(\d{1,2})/(\d{4})', # le DD/MM/YYYY
        r'(\d{1,2})/(\d{1,2})/(\d{2})',   # DD/MM/YY
    ]
    
    # Patterns pour détecter les événements médicaux
    medical_keywords = [
        'consultation', 'hospitalisation', 'opération', 'chirurgie', 'diagnostic',
        'examen', 'analyse', 'radiographie', 'scanner', 'IRM', 'échographie',
        'traitement', 'médicament', 'douleur', 'symptôme', 'aggravation',
        'amélioration', 'guérison', 'décès', 'complication', 'erreur médicale'
    ]
    
    # Patterns pour détecter les événements juridiques
    legal_keywords = [
        'plainte', 'dépôt', 'expertise', 'commission', 'CCI', 'CDU', 'ONIAM',
        'tribunal', 'cour', 'jugement', 'arrêt', 'décision', 'conciliation',
        'médiation', 'procédure', 'prescription', 'délai'
    ]
    
    # Extraction des dates et événements
    for pattern in date_patterns:
        matches = re.finditer(pattern, situation, re.IGNORECASE)
        for match in matches:
            try:
                if len(match.groups()) == 3:
                    day, month, year = match.groups()
                    if len(year) == 2:
                        year = '20' + year
                    
                    event_date = datetime(int(year), int(month), int(day))
                    
                    # Recherche du contexte autour de la date
                    start_pos = max(0, match.start() - 100)
                    end_pos = min(len(situation), match.end() + 100)
                    context = situation[start_pos:end_pos]
                    
                    # Classification de l'événement
                    event_type = "other"
                    event_category = "Événement"
                    
                    # Vérification des mots-clés médicaux
                    for keyword in medical_keywords:
                        if keyword.lower() in context.lower():
                            event_type = "medical"
                            event_category = "Médical"
                            break
                    
                    # Vérification des mots-clés juridiques
                    for keyword in legal_keywords:
                        if keyword.lower() in context.lower():
                            event_type = "legal"
                            event_category = "Juridique"
                            break
                    
                    # Création de l'événement
                    event = {
                        'date': event_date,
                        'date_str': match.group(),
                        'context': context.strip(),
                        'type': event_type,
                        'category': event_category,
                        'description': extract_event_description(context)
                    }
                    
                    events.append(event)
                    
            except (ValueError, TypeError):
                continue
    
    # Tri par date
    events.sort(key=lambda x: x['date'])
    
    return events

def extract_event_description(context: str) -> str:
    """
    Extrait une description concise de l'événement
    """
    # Nettoyage du contexte
    context = re.sub(r'\s+', ' ', context).strip()
    
    # Recherche de phrases complètes
    sentences = re.split(r'[.!?]', context)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10 and len(sentence) < 200:
            return sentence
    
    # Si pas de phrase complète, retourner le contexte tronqué
    return context[:100] + "..." if len(context) > 100 else context

# ============================================================================
# GÉNÉRATION DE TIMELINE INTERACTIVE
# ============================================================================

def create_interactive_timeline(events: List[Dict]) -> go.Figure:
    """
    Crée une timeline interactive avec Plotly
    """
    if not events:
        # Timeline vide
        fig = go.Figure()
        fig.add_annotation(
            text="Aucun événement chronologique détecté",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Timeline des Événements",
            xaxis_title="Date",
            yaxis_title="Événements",
            height=400
        )
        return fig
    
    # Préparation des données
    dates = [event['date'] for event in events]
    descriptions = [event['description'] for event in events]
    categories = [event['category'] for event in events]
    colors = []
    
    # Couleurs selon le type d'événement
    for event in events:
        if event['type'] == 'medical':
            colors.append('#1f77b4')  # Bleu pour médical
        elif event['type'] == 'legal':
            colors.append('#ff7f0e')  # Orange pour juridique
        else:
            colors.append('#2ca02c')  # Vert pour autres
    
    # Création de la timeline
    fig = go.Figure()
    
    # Ajout des événements
    for i, (date, desc, category, color) in enumerate(zip(dates, descriptions, categories, colors)):
        fig.add_trace(go.Scatter(
            x=[date],
            y=[i],
            mode='markers+text',
            marker=dict(
                size=15,
                color=color,
                symbol='circle'
            ),
            text=[f"{category}"],
            textposition="top center",
            name=category,
            hovertemplate=f"<b>{date.strftime('%d/%m/%Y')}</b><br>{desc}<extra></extra>",
            showlegend=False
        ))
    
    # Mise en forme
    fig.update_layout(
        title="📅 Timeline des Événements",
        xaxis_title="Date",
        yaxis_title="Événements",
        height=400,
        hovermode='closest',
        xaxis=dict(
            tickformat='%d/%m/%Y',
            tickmode='auto',
            nticks=min(10, len(events))
        ),
        yaxis=dict(
            showticklabels=False,
            range=[-0.5, len(events) - 0.5]
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_gantt_chart(events: List[Dict]) -> go.Figure:
    """
    Crée un diagramme de Gantt pour les événements
    """
    if not events:
        return create_interactive_timeline([])
    
    # Préparation des données pour Gantt
    tasks = []
    for i, event in enumerate(events):
        tasks.append(dict(
            Task=f"Événement {i+1}",
            Start=event['date'],
            Finish=event['date'],  # Événement ponctuel
            Resource=event['category'],
            Description=event['description']
        ))
    
    # Création du Gantt
    fig = ff.create_gantt(
        tasks,
        colors={
            'Médical': '#1f77b4',
            'Juridique': '#ff7f0e',
            'Événement': '#2ca02c'
        },
        index_col='Resource',
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True
    )
    
    fig.update_layout(
        title="📊 Diagramme de Gantt des Événements",
        xaxis_title="Date",
        height=400,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================

def display_timeline_generator(situation: str):
    """
    Interface Streamlit pour le générateur de timeline
    """
    st.markdown("---")
    st.markdown("### 📅 Timeline Interactive des Faits")
    st.markdown("*Extraction automatique des événements chronologiques*")
    
    if not situation:
        st.warning("⚠️ Veuillez d'abord saisir une situation pour générer la timeline.")
        return
    
    # Extraction des événements
    with st.spinner("🔍 Extraction des événements chronologiques..."):
        events = extract_timeline_events(situation)
    
    # Statistiques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Événements", len(events))
    
    with col2:
        medical_events = len([e for e in events if e['type'] == 'medical'])
        st.metric("🏥 Médicaux", medical_events)
    
    with col3:
        legal_events = len([e for e in events if e['type'] == 'legal'])
        st.metric("⚖️ Juridiques", legal_events)
    
    with col4:
        if events:
            date_range = f"{(max(e['date'] for e in events) - min(e['date'] for e in events)).days} jours"
            st.metric("📅 Période", date_range)
        else:
            st.metric("📅 Période", "N/A")
    
    # Affichage des timelines
    if events:
        # Onglets pour différents types de visualisation
        tab1, tab2 = st.tabs(["📅 Timeline", "📊 Gantt"])
        
        with tab1:
            st.markdown("#### Timeline Interactive")
            fig_timeline = create_interactive_timeline(events)
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        with tab2:
            st.markdown("#### Diagramme de Gantt")
            fig_gantt = create_gantt_chart(events)
            st.plotly_chart(fig_gantt, use_container_width=True)
        
        # Détails des événements
        with st.expander("📋 Détails des Événements"):
            for i, event in enumerate(events, 1):
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    if event['type'] == 'medical':
                        st.markdown("🏥")
                    elif event['type'] == 'legal':
                        st.markdown("⚖️")
                    else:
                        st.markdown("📅")
                
                with col2:
                    st.markdown(f"**{event['date'].strftime('%d/%m/%Y')}** - {event['category']}")
                    st.markdown(f"*{event['description']}*")
                
                if i < len(events):
                    st.markdown("---")
        
        # Alertes de délai
        display_deadline_alerts(events)
        
    else:
        st.info("ℹ️ Aucun événement chronologique détecté dans la situation.")
        st.markdown("**Conseils pour améliorer la détection :**")
        st.markdown("- Utilisez des dates au format DD/MM/YYYY")
        st.markdown("- Mentionnez les consultations, hospitalisations, etc.")
        st.markdown("- Incluez les événements juridiques (plaintes, expertises)")

def display_deadline_alerts(events: List[Dict]):
    """
    Affiche les alertes de délai de prescription
    """
    st.markdown("---")
    st.markdown("### ⏰ Alertes de Délai")
    
    if not events:
        return
    
    # Calcul des délais de prescription
    today = datetime.now()
    prescription_deadlines = {
        "Responsabilité médicale": 10,  # 10 ans
        "Accident médical": 10,        # 10 ans
        "Infection nosocomiale": 10,   # 10 ans
        "Produit défectueux": 10,      # 10 ans
        "Obligation d'information": 5  # 5 ans
    }
    
    alerts = []
    
    for event in events:
        if event['type'] == 'medical':
            for deadline_type, years in prescription_deadlines.items():
                deadline_date = event['date'].replace(year=event['date'].year + years)
                days_remaining = (deadline_date - today).days
                
                if days_remaining > 0 and days_remaining <= 365:  # Alerte si moins d'1 an
                    alerts.append({
                        'type': deadline_type,
                        'event_date': event['date'],
                        'deadline_date': deadline_date,
                        'days_remaining': days_remaining,
                        'description': event['description']
                    })
    
    if alerts:
        # Tri par urgence
        alerts.sort(key=lambda x: x['days_remaining'])
        
        for alert in alerts[:3]:  # Top 3 plus urgents
            if alert['days_remaining'] <= 30:
                st.error(f"🚨 **URGENT** : {alert['type']} - {alert['days_remaining']} jours restants")
            elif alert['days_remaining'] <= 90:
                st.warning(f"⚠️ **ATTENTION** : {alert['type']} - {alert['days_remaining']} jours restants")
            else:
                st.info(f"ℹ️ **RAPPEL** : {alert['type']} - {alert['days_remaining']} jours restants")
            
            st.markdown(f"*Événement déclencheur : {alert['description']}*")
            st.markdown(f"*Date limite : {alert['deadline_date'].strftime('%d/%m/%Y')}*")
            st.markdown("---")
    else:
        st.success("✅ Aucun délai de prescription critique détecté")

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def validate_date_format(date_str: str) -> bool:
    """
    Valide le format d'une date
    """
    patterns = [
        r'^\d{1,2}/\d{1,2}/\d{4}$',
        r'^\d{1,2}-\d{1,2}-\d{4}$',
        r'^\d{1,2}\.\d{1,2}\.\d{4}$'
    ]
    
    return any(re.match(pattern, date_str) for pattern in patterns)

def get_event_statistics(events: List[Dict]) -> Dict:
    """
    Calcule les statistiques des événements
    """
    if not events:
        return {}
    
    stats = {
        'total_events': len(events),
        'medical_events': len([e for e in events if e['type'] == 'medical']),
        'legal_events': len([e for e in events if e['type'] == 'legal']),
        'other_events': len([e for e in events if e['type'] == 'other']),
        'date_range': (max(e['date'] for e in events) - min(e['date'] for e in events)).days,
        'first_event': min(e['date'] for e in events),
        'last_event': max(e['date'] for e in events)
    }
    
    return stats 