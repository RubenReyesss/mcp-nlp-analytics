"""
Sentiment Analysis Module
Analyzes emotional tone and sentiment evolution in messages.
"""

from textblob import TextBlob
from typing import List, Dict, Any
import re
from datetime import datetime


class SentimentAnalyzer:
    """Analyzes sentiment evolution across messages."""
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        # Extended keyword lists with Spanish and English
        self.positive_words = {
            'love', 'excellent', 'amazing', 'fantastic', 'wonderful', 'great', 'good',
            'perfect', 'best', 'awesome', 'brilliant', 'outstanding', 'superb', 'trust',
            'confident', 'happy', 'thrilled', 'delighted', 'impressed', 'satisfied',
            'encanta', 'excelente', 'perfecto', 'increible', 'genial', 'bueno', 'maravilloso',
            'fantastico', 'sobresaliente', 'impresionado', 'satisfecho', 'love', 'adoro',
            'me encanta', 'fantástico', 'fabuloso', 'me gusta', 'bien', 'obra'
        }
        
        self.negative_words = {
            'hate', 'terrible', 'awful', 'horrible', 'bad', 'poor', 'worst',
            'disappointed', 'frustrated', 'angry', 'annoyed', 'upset', 'problem',
            'issue', 'bug', 'slow', 'expensive', 'difficult', 'fail', 'cancel',
            'doubt', 'concern', 'worried', 'unsure', 'alternative', 'competitor',
            'odio', 'terrible', 'horrible', 'malo', 'peor', 'problema', 'bugs',
            'caro', 'lento', 'difícil', 'fracaso', 'cancelar', 'competencia',
            'competidor', 'preocupacion', 'inquietud', 'alternativa', 'dudoso',
            'cambiar', 'adios', 'adiós', 'otros developers', 'más barato',
            'renunciar', 'renuncia', 'renuncie', 'partir', 'irme', 'me voy',
            'dejar', 'abandonar', 'salir', 'terminar', 'fin', 'otro trabajo',
            'mejor oferta', 'buscar', 'explorar', 'mejores', 'mejores roles'
        }
    
    def analyze_evolution(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze how sentiment evolves across messages.
        
        Args:
            messages: List of {'timestamp': str, 'text': str, 'sender': str}
        
        Returns:
            Dictionary with sentiment evolution analysis
        """
        if not messages:
            return self._empty_analysis()
        
        # Analyze each message
        timeline = []
        sentiments = []
        
        for i, msg in enumerate(messages):
            # Handle both strings and dicts
            if isinstance(msg, dict):
                text = msg.get('text', '')
                timestamp = msg.get('timestamp', f'Message {i+1}')
            elif isinstance(msg, str):
                text = msg
                timestamp = f'Message {i+1}'
            else:
                text = str(msg)
                timestamp = f'Message {i+1}'
            
            sentiment_score = self._calculate_sentiment(text)
            sentiments.append(sentiment_score)
            
            timeline.append({
                'timestamp': timestamp,
                'text': text[:100] + '...' if len(text) > 100 else text,
                'sentiment_score': round(sentiment_score, 2),
                'sentiment_state': self._sentiment_state(sentiment_score),
                'message_index': i + 1
            })
        
        # Calculate trend
        trend = self._calculate_trend(sentiments)
        turning_points = self._find_turning_points(sentiments, timeline)
        overall_change = sentiments[-1] - sentiments[0] if sentiments else 0
        
        # Generate interpretation
        interpretation = self._generate_interpretation(
            sentiments, trend, turning_points
        )
        
        return {
            'timeline': timeline,
            'current_sentiment': round(sentiments[-1], 2) if sentiments else 0,
            'initial_sentiment': round(sentiments[0], 2) if sentiments else 0,
            'trend': trend,
            'turning_points': turning_points,
            'overall_change': round(overall_change, 2),
            'interpretation': interpretation,
            'message_count': len(messages)
        }
    
    def _calculate_sentiment(self, text: str) -> float:
        """
        Calculate sentiment score from 0-100.
        0 = very negative, 50 = neutral, 100 = very positive
        Uses keyword matching primarily, TextBlob for fine-tuning.
        """
        if not text:
            return 50.0
        
        text_lower = text.lower()
        
        # Primary: Count positive and negative keywords
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        # Base score from keywords
        keyword_score = 50 + (positive_count * 10) - (negative_count * 10)
        
        # Use TextBlob for fine-tuning
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        textblob_score = (polarity + 1) * 50
        
        # Combine: 70% keywords, 30% TextBlob
        # Keywords are more reliable for detecting sentiment in conversations
        final_score = (keyword_score * 0.7) + (textblob_score * 0.3)
        
        # Ensure score is in valid range
        return min(100, max(0, final_score))
    
    def _sentiment_state(self, score: float) -> str:
        """Classify sentiment into states."""
        if score >= 80:
            return "EXTREMELY_POSITIVE"
        elif score >= 60:
            return "POSITIVE"
        elif score >= 40:
            return "NEUTRAL"
        elif score >= 20:
            return "NEGATIVE"
        else:
            return "EXTREMELY_NEGATIVE"
    
    def _calculate_trend(self, sentiments: List[float]) -> str:
        """Determine overall trend."""
        if len(sentiments) < 2:
            return "insufficient_data"
        
        # Calculate slope
        first_half = sum(sentiments[:len(sentiments)//2]) / max(1, len(sentiments)//2)
        second_half = sum(sentiments[len(sentiments)//2:]) / max(1, len(sentiments) - len(sentiments)//2)
        
        diff = second_half - first_half
        
        if diff > 10:
            return "IMPROVING"
        elif diff < -10:
            return "DECLINING"
        else:
            return "STABLE"
    
    def _find_turning_points(self, sentiments: List[float], timeline: List[Dict]) -> List[Dict]:
        """Find significant sentiment changes."""
        turning_points = []
        
        for i in range(1, len(sentiments)):
            change = abs(sentiments[i] - sentiments[i-1])
            
            # Significant change: > 20 points
            if change > 20:
                turning_points.append({
                    'index': i,
                    'timestamp': timeline[i]['timestamp'],
                    'from_state': self._sentiment_state(sentiments[i-1]),
                    'to_state': self._sentiment_state(sentiments[i]),
                    'change_magnitude': round(change, 2),
                    'severity': 'CRITICAL' if change > 40 else 'HIGH' if change > 30 else 'MEDIUM'
                })
        
        return turning_points
    
    def _generate_interpretation(self, sentiments: List[float], trend: str, 
                                turning_points: List[Dict]) -> str:
        """Generate human-readable interpretation."""
        if not sentiments:
            return "No messages to analyze."
        
        current = sentiments[-1]
        initial = sentiments[0]
        
        # Base interpretation
        if trend == "DECLINING":
            base = f"Sentiment is DECLINING overall (from {initial:.0f} to {current:.0f})"
        elif trend == "IMPROVING":
            base = f"Sentiment is IMPROVING overall (from {initial:.0f} to {current:.0f})"
        else:
            base = f"Sentiment is STABLE (around {current:.0f})"
        
        # Add turning point info
        if turning_points:
            critical_points = [p for p in turning_points if p['severity'] == 'CRITICAL']
            if critical_points:
                base += f". WARNING: {len(critical_points)} critical sentiment shift(s) detected."
        
        # Final assessment
        if current < 30:
            base += " RISK LEVEL: CRITICAL - Immediate intervention recommended."
        elif current < 50:
            base += " RISK LEVEL: HIGH - Attention needed soon."
        elif current > 70:
            base += " Status: POSITIVE - No immediate action needed."
        
        return base
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure."""
        return {
            'timeline': [],
            'current_sentiment': 0,
            'initial_sentiment': 0,
            'trend': 'unknown',
            'turning_points': [],
            'overall_change': 0,
            'interpretation': 'No data provided',
            'message_count': 0
        }
