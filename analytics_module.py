"""
Module d'analytics simplifié pour LegalDocBot
"""

import pandas as pd
from datetime import datetime

class Analytics:
    def __init__(self):
        self.analysis_count = 0
        self.analyses = []
        self.favorites = []
        self.analysis_times = []  # Pour calculer le temps moyen
        self.mode_usage = {}      # Pour tracker l'usage des modes
    
    def add_analysis(self, situation, analysis, duration=None, mode=None):
        """Ajoute une analyse à l'historique"""
        self.analysis_count += 1
        
        # Tracker le temps d'analyse
        if duration is not None:
            self.analysis_times.append(duration)
        
        # Tracker l'usage des modes
        if mode:
            self.mode_usage[mode] = self.mode_usage.get(mode, 0) + 1
        
        self.analyses.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'situation': situation,
            'analysis': analysis,
            'duration': duration,
            'mode': mode
        })
    
    def get_history_df(self):
        """Retourne l'historique des analyses sous forme de DataFrame"""
        if not self.analyses:
            return pd.DataFrame()
        return pd.DataFrame(self.analyses)
    
    def get_favorites_df(self):
        """Retourne les favoris sous forme de DataFrame"""
        if not self.favorites:
            return pd.DataFrame()
        return pd.DataFrame(self.favorites)

    def add_favorite(self, situation, analysis):
        """Ajoute une analyse aux favoris"""
        self.favorites.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'situation': situation,
            'analysis': analysis
        })
    
    def add_to_favorites(self, situation, analysis):
        """Alias pour add_favorite"""
        self.add_favorite(situation, analysis)
    
    def get_favorites(self):
        """Retourne la liste des favoris"""
        return self.favorites
    
    def track_analysis(self, situation, analysis, duration=None, mode=None):
        """Alias pour add_analysis avec paramètres supplémentaires"""
        self.add_analysis(situation, analysis, duration, mode)
    
    def get_stats(self):
        """Retourne les statistiques complètes"""
        # Calculer le temps moyen
        avg_time = 0.0
        if self.analysis_times:
            avg_time = sum(self.analysis_times) / len(self.analysis_times)
        
        # S'assurer que mode_usage a des valeurs par défaut
        if not self.mode_usage:
            self.mode_usage = {
                'hybrid': 0,
                'local_rag': 0,
                'xai_websearch': 0,
                'groq_selection': 0,
                'chromadb_rag': 0
            }
        
        return {
            'total_analyses': self.analysis_count,
            'avg_time': avg_time,
            'favorites_count': len(self.favorites),
            'mode_usage': self.mode_usage,
            'last_analysis': self.analyses[-1]['timestamp'] if self.analyses else None
        }

# Instance globale
analytics = Analytics() 