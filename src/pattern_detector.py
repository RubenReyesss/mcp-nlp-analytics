"""
Pattern Detection Module
Detects risk signals and warning patterns in conversations.
"""

from typing import List, Dict, Any
import re


class PatternDetector:
    """Detects risk signals in message patterns."""
    
    def __init__(self):
        """Initialize pattern detector."""
        self.comparison_keywords = [
            'competitor', 'alternative', 'better', 'cheaper', 'faster',
            'other', 'someone else', 'another', 'different', 'switch',
            'change', 'similar', 'compare', 'versus', 'instead'
        ]
        
        self.frustration_keywords = [
            'slow', 'late', 'delayed', 'wait', 'frustrated', 'annoyed',
            'angry', 'upset', 'disappointed', 'problem', 'issue', 'bug',
            'broken', 'not working', 'fail', 'error', 'impossible'
        ]
        
        self.disengagement_keywords = [
            'cancel', 'stop', 'end', 'quit', 'leave', 'exit', 'goodbye',
            'farewell', 'thanks anyway', 'no thanks', 'decline', 'refuse',
            'not interested', 'moving on', 'consider', 'think about',
            'evaluate', 'looking at'
        ]
        
        self.price_keywords = [
            'expensive', 'cost', 'price', 'cheap', 'expensive', 'fee',
            'charge', 'budget', 'discount', 'negotiate', 'lower'
        ]
    
    def detect_signals(self, messages: List[Dict[str, Any]], 
                      context: str = "general") -> Dict[str, Any]:
        """
        Detect risk signals in conversations.
        
        Args:
            messages: List of messages
            context: Type of relationship (customer/employee/investor/general)
        
        Returns:
            Dictionary with detected signals and risk assessment
        """
        if not messages:
            return self._empty_signals()
        
        signals = []
        risk_scores = []
        breaking_point = None
        key_phrases = []
        
        for i, msg in enumerate(messages):
            # Handle both strings and dicts
            if isinstance(msg, dict):
                text = msg.get('text', '').lower()
                timestamp = msg.get('timestamp', f'Message {i+1}')
            elif isinstance(msg, str):
                text = msg.lower()
                timestamp = f'Message {i+1}'
            else:
                text = str(msg).lower()
                timestamp = f'Message {i+1}'
            
            # Check for various signal types
            comparison_signal = self._check_comparisons(text)
            frustration_signal = self._check_frustration(text)
            disengagement_signal = self._check_disengagement(text)
            price_signal = self._check_price(text)
            
            msg_signals = []
            msg_risk = 0
            
            if comparison_signal['found']:
                msg_signals.append(comparison_signal)
                msg_risk += 25
                key_phrases.append(comparison_signal['text'])
                if breaking_point is None:
                    breaking_point = i + 1
            
            if frustration_signal['found']:
                msg_signals.append(frustration_signal)
                msg_risk += 30
                key_phrases.append(frustration_signal['text'])
                if breaking_point is None and msg_risk > 30:
                    breaking_point = i + 1
            
            if disengagement_signal['found']:
                msg_signals.append(disengagement_signal)
                msg_risk += 35
                key_phrases.append(disengagement_signal['text'])
                if breaking_point is None:
                    breaking_point = i + 1
            
            if price_signal['found']:
                msg_signals.append(price_signal)
                msg_risk += 20
                key_phrases.append(price_signal['text'])
            
            if msg_signals:
                signals.append({
                    'message_index': i + 1,
                    'timestamp': timestamp,
                    'signals': msg_signals,
                    'risk_score': min(100, msg_risk)
                })
                risk_scores.append(msg_risk)
        
        # Calculate overall risk
        overall_risk = max(risk_scores) if risk_scores else 0
        risk_level = self._assess_risk_level(overall_risk)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            context, risk_level, signals, breaking_point
        )
        
        return {
            'signals': signals,
            'risk_level': risk_level,
            'confidence': min(100, len(signals) * 15),
            'breaking_point': breaking_point,
            'key_phrases': list(set(key_phrases))[:5],  # Top 5 unique phrases
            'recommendations': recommendations,
            'total_risk_score': min(100, overall_risk)
        }
    
    def _check_comparisons(self, text: str) -> Dict[str, Any]:
        """Check for competitor/alternative mentions."""
        for keyword in self.comparison_keywords:
            if keyword in text:
                return {
                    'found': True,
                    'type': 'COMPETITOR_COMPARISON',
                    'text': keyword,
                    'description': 'Comparing with alternatives or competitors'
                }
        return {'found': False}
    
    def _check_frustration(self, text: str) -> Dict[str, Any]:
        """Check for frustration indicators."""
        for keyword in self.frustration_keywords:
            if keyword in text:
                return {
                    'found': True,
                    'type': 'FRUSTRATION',
                    'text': keyword,
                    'description': 'Expressing dissatisfaction or frustration'
                }
        return {'found': False}
    
    def _check_disengagement(self, text: str) -> Dict[str, Any]:
        """Check for disengagement signals."""
        for keyword in self.disengagement_keywords:
            if keyword in text:
                return {
                    'found': True,
                    'type': 'DISENGAGEMENT',
                    'text': keyword,
                    'description': 'Showing intent to leave or end relationship'
                }
        return {'found': False}
    
    def _check_price(self, text: str) -> Dict[str, Any]:
        """Check for price-related concerns."""
        for keyword in self.price_keywords:
            if keyword in text:
                return {
                    'found': True,
                    'type': 'PRICE_CONCERN',
                    'text': keyword,
                    'description': 'Mentioning cost or pricing concerns'
                }
        return {'found': False}
    
    def _assess_risk_level(self, risk_score: float) -> str:
        """Assess overall risk level."""
        if risk_score >= 70:
            return "CRITICAL"
        elif risk_score >= 50:
            return "HIGH"
        elif risk_score >= 30:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_recommendations(self, context: str, risk_level: str,
                                 signals: List[Dict], breaking_point: int) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if risk_level == "CRITICAL":
            recommendations.append("⚠️ URGENT: Immediate intervention required")
            if breaking_point:
                recommendations.append(f"Breaking point detected at message {breaking_point}")
        
        if context == "customer":
            if risk_level in ["CRITICAL", "HIGH"]:
                recommendations.append("Contact customer immediately to address concerns")
                recommendations.append("Prepare retention offer (discount/upgrade)")
                recommendations.append("Escalate to account manager")
        
        elif context == "employee":
            if risk_level in ["CRITICAL", "HIGH"]:
                recommendations.append("Schedule 1-on-1 with HR or manager")
                recommendations.append("Identify root cause of dissatisfaction")
                recommendations.append("Prepare retention plan")
        
        elif context == "investor":
            if risk_level in ["CRITICAL", "HIGH"]:
                recommendations.append("Prepare detailed response addressing concerns")
                recommendations.append("Schedule follow-up meeting")
        
        # Add general recommendations
        if any(s.get('type') == 'COMPETITOR_COMPARISON' for s in signals):
            recommendations.append("Counter competitive threats with unique value proposition")
        
        if any(s.get('type') == 'PRICE_CONCERN' for s in signals):
            recommendations.append("Review pricing strategy and alternative plans")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _empty_signals(self) -> Dict[str, Any]:
        """Return empty signals structure."""
        return {
            'signals': [],
            'risk_level': 'UNKNOWN',
            'confidence': 0,
            'breaking_point': None,
            'key_phrases': [],
            'recommendations': []
        }
