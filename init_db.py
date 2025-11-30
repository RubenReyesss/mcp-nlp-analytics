#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Initialize database with all required tables
"""
import sqlite3
import os

# Ensure data directory exists
data_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(data_dir, exist_ok=True)

db_path = os.path.join(data_dir, 'sentiment_analysis.db')

# Remove old database if exists
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"🗑️  Removed old database: {db_path}")

# Connect and create tables
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("📋 Creating tables...")

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
print("✅ Created: customer_profiles")

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
print("✅ Created: conversations")

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
print("✅ Created: risk_alerts")

conn.commit()

# Verify tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"\n📊 Tables in database: {len(tables)}")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"   • {table[0]}: {count} rows")

conn.close()
print(f"\n✅ Database initialized successfully at: {db_path}")
