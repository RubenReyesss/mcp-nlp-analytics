"""
Database Manager for Sentiment Evolution Tracker
Stores analysis results and provides historical comparisons.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional


class AnalysisDatabase:
    """Manages persistent storage of sentiment analyses."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database."""
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, "..", "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "sentiment_analysis.db")
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for conversations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                context_type TEXT NOT NULL,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                messages TEXT NOT NULL,
                sentiment_score REAL,
                trend TEXT,
                risk_level TEXT,
                predicted_action TEXT,
                confidence REAL
            )
        ''')
        
        # Table for risk alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                alert_type TEXT,
                severity TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved INTEGER DEFAULT 0,
                notes TEXT
            )
        ''')
        
        # Table for customer profiles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT UNIQUE NOT NULL,
                name TEXT,
                context_type TEXT,
                first_contact TIMESTAMP,
                last_contact TIMESTAMP,
                total_interactions INTEGER DEFAULT 0,
                churn_risk REAL DEFAULT 0,
                lifetime_sentiment REAL DEFAULT 0,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_analysis(self, customer_id: str, context_type: str, 
                     messages: List[str], analysis: Dict[str, Any]) -> int:
        """
        Save an analysis result to the database.
        
        Args:
            customer_id: Unique customer identifier
            context_type: 'customer', 'employee', or 'email'
            messages: List of message strings
            analysis: Analysis result dictionary
        
        Returns:
            Analysis ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations 
            (customer_id, context_type, messages, sentiment_score, 
             trend, risk_level, predicted_action, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_id,
            context_type,
            json.dumps(messages),
            analysis.get('current_sentiment', 0),
            analysis.get('trend', 'UNKNOWN'),
            analysis.get('risk_level', 'UNKNOWN'),
            analysis.get('predicted_action', 'UNKNOWN'),
            analysis.get('confidence', 0)
        ))
        
        analysis_id = cursor.lastrowid
        
        # Update or create customer profile
        cursor.execute('SELECT id FROM customer_profiles WHERE customer_id = ?', (customer_id,))
        profile = cursor.fetchone()
        
        if profile:
            cursor.execute('''
                UPDATE customer_profiles 
                SET last_contact = CURRENT_TIMESTAMP,
                    total_interactions = total_interactions + 1,
                    churn_risk = ?,
                    lifetime_sentiment = (lifetime_sentiment * total_interactions + ?) / (total_interactions + 1)
                WHERE customer_id = ?
            ''', (
                analysis.get('confidence', 0),
                analysis.get('current_sentiment', 0),
                customer_id
            ))
        else:
            cursor.execute('''
                INSERT INTO customer_profiles 
                (customer_id, context_type, first_contact, last_contact, 
                 total_interactions, churn_risk, lifetime_sentiment)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, ?, ?)
            ''', (
                customer_id,
                context_type,
                analysis.get('confidence', 0),
                analysis.get('current_sentiment', 0)
            ))
        
        # Create alert if risk is high
        if analysis.get('confidence', 0) > 0.7:
            cursor.execute('''
                INSERT INTO risk_alerts (customer_id, alert_type, severity, notes)
                VALUES (?, ?, ?, ?)
            ''', (
                customer_id,
                analysis.get('predicted_action', 'UNKNOWN'),
                'HIGH' if analysis.get('confidence', 0) > 0.85 else 'MEDIUM',
                f"Detected {analysis.get('trend')} trend with {analysis.get('confidence', 0)*100:.0f}% confidence"
            ))
        
        conn.commit()
        conn.close()
        
        return analysis_id
    
    def get_customer_history(self, customer_id: str) -> Dict[str, Any]:
        """
        Get complete history for a customer.
        
        Args:
            customer_id: Unique customer identifier
        
        Returns:
            Customer profile and analysis history
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get profile
        cursor.execute('SELECT * FROM customer_profiles WHERE customer_id = ?', (customer_id,))
        profile_row = cursor.fetchone()
        profile = dict(profile_row) if profile_row else None
        
        # Get recent analyses
        cursor.execute('''
            SELECT * FROM conversations 
            WHERE customer_id = ? 
            ORDER BY analysis_date DESC 
            LIMIT 10
        ''', (customer_id,))
        
        analyses = [dict(row) for row in cursor.fetchall()]
        
        # Get active alerts
        cursor.execute('''
            SELECT * FROM risk_alerts 
            WHERE customer_id = ? AND resolved = 0
            ORDER BY created_at DESC
        ''', (customer_id,))
        
        alerts = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'profile': profile,
            'analyses': analyses,
            'active_alerts': alerts
        }
    
    def get_high_risk_customers(self, threshold: float = 0.75) -> List[Dict[str, Any]]:
        """
        Get all customers with high churn risk.
        
        Args:
            threshold: Confidence threshold (0-1)
        
        Returns:
            List of high-risk customers
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cp.*, 
                   COUNT(ra.id) as active_alerts,
                   MAX(c.analysis_date) as last_analysis
            FROM customer_profiles cp
            LEFT JOIN risk_alerts ra ON cp.customer_id = ra.customer_id AND ra.resolved = 0
            LEFT JOIN conversations c ON cp.customer_id = c.customer_id
            WHERE cp.churn_risk > ?
            GROUP BY cp.customer_id
            ORDER BY cp.churn_risk DESC
        ''', (threshold,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def resolve_alert(self, alert_id: int, notes: str = ""):
        """Mark an alert as resolved."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE risk_alerts 
            SET resolved = 1, notes = ?
            WHERE id = ?
        ''', (notes, alert_id))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total customers
        cursor.execute('SELECT COUNT(DISTINCT customer_id) as count FROM conversations')
        total_customers = cursor.fetchone()[0]
        
        # Customers at risk
        cursor.execute('SELECT COUNT(*) as count FROM customer_profiles WHERE churn_risk > 0.7')
        at_risk = cursor.fetchone()[0]
        
        # Active alerts
        cursor.execute('SELECT COUNT(*) as count FROM risk_alerts WHERE resolved = 0')
        active_alerts = cursor.fetchone()[0]
        
        # Average sentiment
        cursor.execute('SELECT AVG(sentiment_score) as avg FROM conversations')
        avg_sentiment = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_customers': total_customers,
            'customers_at_risk': at_risk,
            'active_alerts': active_alerts,
            'average_sentiment': round(avg_sentiment, 2),
            'database_file': self.db_path
        }
