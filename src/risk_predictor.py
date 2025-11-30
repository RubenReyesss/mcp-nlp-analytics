"""
Risk Predictor Module
Predicts likely outcomes and next actions.
"""

from typing import List, Dict, Any
from sentiment_analyzer import SentimentAnalyzer


class RiskPredictor:
    """Predicts next actions and outcomes."""
    
    def __init__(self):
        """Initialize risk predictor."""
        self.sentiment_analyzer = SentimentAnalyzer()
        
        self.churn_indicators = [
            'cancel', 'leave', 'stop', 'switch', 'competitor', 'alternative',
            'expensive', 'slow', 'disappointed', 'problem', 'issue'
        ]
        
        self.resolution_indicators = [
            'understand', 'sorry', 'appreciate', 'help', 'support', 'solution',
            'fix', 'improve', 'better', 'thanks'
        ]
    
    def predict_action(self, messages: List[Dict[str, Any]], 
                      context: str = "general") -> Dict[str, Any]:
        """
        Predict likely next action or outcome.
        
        Args:
            messages: List of messages
            context: Type of relationship
        
        Returns:
            Prediction with confidence and recommendations
        """
        if not messages:
            return self._empty_prediction()
        
        # Get sentiment evolution
        sentiment_data = self.sentiment_analyzer.analyze_evolution(messages)
        sentiments = [item['sentiment_score'] for item in sentiment_data['timeline']]
        current_sentiment = sentiment_data['current_sentiment']
        trend = sentiment_data['trend']
        
        # Analyze final messages for intent
        final_messages = messages[-3:] if len(messages) >= 3 else messages
        final_text = ' '.join([
            m.get('text', '') if isinstance(m, dict) else m
            for m in final_messages
        ]).lower()
        
        # Detect indicators
        churn_score = self._score_churn_risk(final_text)
        resolution_score = self._score_resolution_likelihood(final_text)
        
        # Predict action
        action = self._predict_primary_action(
            current_sentiment, trend, churn_score, resolution_score, context
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(sentiments, churn_score, resolution_score)
        
        # Predict timeline
        timeline = self._predict_timeline(
            trend, current_sentiment, churn_score, context
        )
        
        # Calculate urgency
        urgency = self._assess_urgency(current_sentiment, churn_score, action)
        
        # Generate interventions
        interventions = self._generate_interventions(
            action, context, urgency, current_sentiment
        )
        
        # Calculate success rate
        success_rate = self._calculate_intervention_success(
            context, urgency, action
        )
        
        explanation = self._generate_explanation(
            action, current_sentiment, trend, churn_score
        )
        
        return {
            'action': action,
            'confidence': round(confidence, 1),
            'timeline': timeline,
            'urgency': urgency,
            'interventions': interventions,
            'success_rate': round(success_rate, 1),
            'explanation': explanation,
            'sentiment_trajectory': {
                'initial': sentiment_data['initial_sentiment'],
                'current': current_sentiment,
                'trend': trend,
                'overall_change': sentiment_data['overall_change']
            }
        }
    
    def _score_churn_risk(self, text: str) -> float:
        """Score risk of churn/leaving."""
        score = 0
        for indicator in self.churn_indicators:
            if indicator in text:
                score += 15
        return min(100, score)
    
    def _score_resolution_likelihood(self, text: str) -> float:
        """Score likelihood of resolution."""
        score = 0
        for indicator in self.resolution_indicators:
            if indicator in text:
                score += 15
        return min(100, score)
    
    def _predict_primary_action(self, current_sentiment: float, trend: str,
                               churn_score: float, resolution_score: float,
                               context: str) -> str:
        """Predict primary action."""
        
        # Churn risk high and sentiment low
        if churn_score > 50 and current_sentiment < 40:
            return "LIKELY_CHURN"
        
        # Resolution likely
        if resolution_score > 50 and trend == "IMPROVING":
            return "LIKELY_RESOLUTION"
        
        # Neutral/staying
        if current_sentiment > 50 and trend != "DECLINING":
            return "LIKELY_STAY"
        
        # Escalation needed
        if current_sentiment < 30 and trend == "DECLINING":
            return "ESCALATION_NEEDED"
        
        # Uncertain but watching
        return "MONITOR_CLOSELY"
    
    def _calculate_confidence(self, sentiments: List[float],
                            churn_score: float, resolution_score: float) -> float:
        """Calculate confidence in prediction."""
        base_confidence = 50
        
        # More messages = more data = more confidence
        if len(sentiments) >= 5:
            base_confidence += 20
        elif len(sentiments) >= 3:
            base_confidence += 10
        
        # Clear trend patterns = more confidence
        if len(sentiments) >= 3:
            trend_strength = abs(sum(sentiments[-2:]) - sum(sentiments[:2])) / len(sentiments)
            base_confidence += min(20, trend_strength)
        
        # Strong indicators = more confidence
        if max(churn_score, resolution_score) > 60:
            base_confidence += 15
        
        return min(100, base_confidence)
    
    def _predict_timeline(self, trend: str, current_sentiment: float,
                         churn_score: float, context: str) -> str:
        """Predict timeline to action."""
        
        # Immediate if critical
        if current_sentiment < 20 and churn_score > 80:
            return "IMMEDIATE (0-24 hours)"
        
        # Very soon if declining rapidly
        if trend == "DECLINING" and churn_score > 60:
            return "VERY_SOON (1-3 days)"
        
        # Soon if high risk
        if churn_score > 50 or current_sentiment < 40:
            return "SOON (3-7 days)"
        
        # Medium term
        if current_sentiment < 50:
            return "MEDIUM_TERM (1-4 weeks)"
        
        # Extended
        return "EXTENDED (1-3 months)"
    
    def _assess_urgency(self, current_sentiment: float, churn_score: float,
                       action: str) -> str:
        """Assess urgency level."""
        
        if current_sentiment < 20 or churn_score > 80 or action == "LIKELY_CHURN":
            return "CRITICAL"
        
        if current_sentiment < 40 or churn_score > 60 or action == "ESCALATION_NEEDED":
            return "HIGH"
        
        if current_sentiment < 50 or churn_score > 40:
            return "MEDIUM"
        
        return "LOW"
    
    def _generate_interventions(self, action: str, context: str,
                               urgency: str, sentiment: float) -> List[str]:
        """Generate intervention recommendations."""
        interventions = []
        
        if action == "LIKELY_CHURN":
            interventions.append("🚨 Immediate outreach required")
            interventions.append("Prepare retention offer")
            interventions.append("Escalate to senior management")
        
        elif action == "ESCALATION_NEEDED":
            interventions.append("⚠️ Schedule urgent meeting")
            interventions.append("Identify root cause")
            interventions.append("Prepare solution options")
        
        elif action == "LIKELY_RESOLUTION":
            interventions.append("✅ Prepare resolution proposal")
            interventions.append("Schedule follow-up")
        
        # Context-specific interventions
        if context == "customer":
            if urgency in ["CRITICAL", "HIGH"]:
                interventions.append("Offer priority support/upgrade")
                interventions.append("Consider special pricing")
        
        elif context == "employee":
            if urgency in ["CRITICAL", "HIGH"]:
                interventions.append("Schedule HR meeting")
                interventions.append("Assess job satisfaction")
        
        return interventions[:4]
    
    def _calculate_intervention_success(self, context: str, urgency: str,
                                       action: str) -> float:
        """Calculate likelihood of successful intervention."""
        
        base_success = 60
        
        # Urgency affects success
        urgency_map = {
            "CRITICAL": -20,
            "HIGH": -10,
            "MEDIUM": 0,
            "LOW": 10
        }
        base_success += urgency_map.get(urgency, 0)
        
        # Action type affects success
        action_map = {
            "LIKELY_RESOLUTION": 20,
            "LIKELY_STAY": 15,
            "MONITOR_CLOSELY": 5,
            "ESCALATION_NEEDED": -5,
            "LIKELY_CHURN": -15
        }
        base_success += action_map.get(action, 0)
        
        # Context affects success
        if context in ["customer", "employee"]:
            base_success += 10
        
        return max(20, min(95, base_success))
    
    def _generate_explanation(self, action: str, sentiment: float,
                            trend: str, churn_score: float) -> str:
        """Generate explanation of prediction."""
        
        explanation = f"Based on current sentiment ({sentiment:.0f}/100) and {trend.lower()} trend, "
        
        if action == "LIKELY_CHURN":
            explanation += f"the subject shows strong churn indicators ({churn_score:.0f}/100). "
            explanation += "Immediate action strongly recommended to prevent departure."
        
        elif action == "LIKELY_RESOLUTION":
            explanation += "the situation appears to be resolving. "
            explanation += "Continue supportive approach and follow up soon."
        
        elif action == "LIKELY_STAY":
            explanation += "the relationship appears stable. "
            explanation += "Maintain current level of service and monitor for changes."
        
        elif action == "ESCALATION_NEEDED":
            explanation += "the situation has deteriorated significantly. "
            explanation += "Escalation and intervention are necessary."
        
        else:  # MONITOR_CLOSELY
            explanation += "signals are mixed. Continue monitoring closely."
        
        return explanation
    
    def _empty_prediction(self) -> Dict[str, Any]:
        """Return empty prediction."""
        return {
            'action': 'UNKNOWN',
            'confidence': 0,
            'timeline': 'UNKNOWN',
            'urgency': 'UNKNOWN',
            'interventions': [],
            'success_rate': 0,
            'explanation': 'No data provided'
        }
