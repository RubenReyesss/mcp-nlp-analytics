"""
Test suite for Sentiment Evolution Tracker
Basic tests to verify core functionality
"""

import sys
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sentiment_analyzer import SentimentAnalyzer
from pattern_detector import PatternDetector
from risk_predictor import RiskPredictor


class TestSentimentAnalyzer:
    """Test sentiment analysis functionality"""
    
    def test_positive_sentiment(self):
        """Test positive sentiment detection"""
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_evolution([
            {"content": "Excelente servicio, muy satisfecho", "timestamp": "2025-11-27 10:00"}
        ])
        score = result.get("current_sentiment", 0)
        assert 60 <= score <= 100, f"Expected positive score, got {score}"
        print(f"✓ Positive sentiment: {score}/100")
    
    def test_negative_sentiment(self):
        """Test negative sentiment detection"""
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_evolution([
            {"content": "Terrible servicio, muy insatisfecho", "timestamp": "2025-11-27 10:00"}
        ])
        score = result.get("current_sentiment", 50)
        assert score < 40, f"Expected negative score, got {score}"
        print(f"✓ Negative sentiment: {score}/100")
    
    def test_neutral_sentiment(self):
        """Test neutral sentiment detection"""
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_evolution([
            {"content": "El servicio existe", "timestamp": "2025-11-27 10:00"}
        ])
        score = result.get("current_sentiment", 50)
        assert 40 <= score <= 60, f"Expected neutral score, got {score}"
        print(f"✓ Neutral sentiment: {score}/100")
    
    def test_score_range(self):
        """Test that scores are in valid range"""
        analyzer = SentimentAnalyzer()
        test_messages = [
            "Increíble",
            "Bueno",
            "Normal",
            "Malo",
            "Terrible"
        ]
        
        for message in test_messages:
            result = analyzer.analyze_evolution([
                {"content": message, "timestamp": "2025-11-27 10:00"}
            ])
            score = result.get("current_sentiment", 0)
            assert 0 <= score <= 100, f"Score out of range: {score}"
        
        print(f"✓ All scores in valid range [0-100]")


class TestPatternDetector:
    """Test pattern detection functionality"""
    
    def test_declining_trend(self):
        """Test declining trend detection"""
        detector = PatternDetector()
        timeline = [
            {"score": 80, "time": "10:00"},
            {"score": 75, "time": "11:00"},
            {"score": 70, "time": "12:00"},
            {"score": 65, "time": "13:00"},
            {"score": 60, "time": "14:00"}
        ]
        trend = detector.detect_trend([t["score"] for t in timeline])
        assert trend == "DECLINING", f"Expected DECLINING, got {trend}"
        print(f"✓ Declining trend detected")
    
    def test_rising_trend(self):
        """Test rising trend detection"""
        detector = PatternDetector()
        timeline = [
            {"score": 30, "time": "10:00"},
            {"score": 40, "time": "11:00"},
            {"score": 50, "time": "12:00"},
            {"score": 60, "time": "13:00"},
            {"score": 70, "time": "14:00"}
        ]
        trend = detector.detect_trend([t["score"] for t in timeline])
        assert trend == "RISING", f"Expected RISING, got {trend}"
        print(f"✓ Rising trend detected")
    
    def test_stable_trend(self):
        """Test stable trend detection"""
        detector = PatternDetector()
        timeline = [
            {"score": 50, "time": "10:00"},
            {"score": 50, "time": "11:00"},
            {"score": 50, "time": "12:00"},
            {"score": 50, "time": "13:00"},
            {"score": 50, "time": "14:00"}
        ]
        trend = detector.detect_trend([t["score"] for t in timeline])
        assert trend == "STABLE", f"Expected STABLE, got {trend}"
        print(f"✓ Stable trend detected")


class TestRiskPredictor:
    """Test risk prediction functionality"""
    
    def test_high_risk(self):
        """Test high risk prediction"""
        predictor = RiskPredictor()
        risk = predictor.predict_churn_risk(30.0, "DECLINING")
        assert risk > 0.5, f"Expected high risk, got {risk}"
        print(f"✓ High risk detected: {risk:.1%}")
    
    def test_low_risk(self):
        """Test low risk prediction"""
        predictor = RiskPredictor()
        risk = predictor.predict_churn_risk(80.0, "RISING")
        assert risk < 0.3, f"Expected low risk, got {risk}"
        print(f"✓ Low risk detected: {risk:.1%}")
    
    def test_medium_risk(self):
        """Test medium risk prediction"""
        predictor = RiskPredictor()
        risk = predictor.predict_churn_risk(50.0, "STABLE")
        assert 0.2 <= risk <= 0.8, f"Expected medium risk, got {risk}"
        print(f"✓ Medium risk detected: {risk:.1%}")


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*60)
    print("SENTIMENT EVOLUTION TRACKER - TEST SUITE")
    print("="*60 + "\n")
    
    tests_passed = 0
    tests_total = 0
    
    # Test SentimentAnalyzer
    print("Testing SentimentAnalyzer:")
    print("-" * 40)
    try:
        test_sa = TestSentimentAnalyzer()
        test_sa.test_positive_sentiment()
        tests_passed += 1
        test_sa.test_negative_sentiment()
        tests_passed += 1
        test_sa.test_neutral_sentiment()
        tests_passed += 1
        test_sa.test_score_range()
        tests_passed += 1
        tests_total += 4
    except Exception as e:
        print(f"✗ Error: {e}")
        tests_total += 4
    
    # Test PatternDetector
    print("\nTesting PatternDetector:")
    print("-" * 40)
    try:
        test_pd = TestPatternDetector()
        test_pd.test_declining_trend()
        tests_passed += 1
        test_pd.test_rising_trend()
        tests_passed += 1
        test_pd.test_stable_trend()
        tests_passed += 1
        tests_total += 3
    except Exception as e:
        print(f"✗ Error: {e}")
        tests_total += 3
    
    # Test RiskPredictor
    print("\nTesting RiskPredictor:")
    print("-" * 40)
    try:
        test_rp = TestRiskPredictor()
        test_rp.test_high_risk()
        tests_passed += 1
        test_rp.test_low_risk()
        tests_passed += 1
        test_rp.test_medium_risk()
        tests_passed += 1
        tests_total += 3
    except Exception as e:
        print(f"✗ Error: {e}")
        tests_total += 3
    
    # Summary
    print("\n" + "="*60)
    print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
    print("="*60 + "\n")
    
    if tests_passed == tests_total:
        print("✅ All tests passed!")
        return True
    else:
        print(f"❌ {tests_total - tests_passed} tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
