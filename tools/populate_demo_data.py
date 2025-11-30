#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Populate the SQLite database with deterministic demo data."""

import json
import os
import sqlite3
from datetime import datetime, timedelta

# Resolve database path inside data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "sentiment_analysis.db")

print(f"📍 Database path: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

clientes = [
    {"id": "ACME_CORP_001", "nombre": "Acme Corporation"},
    {"id": "TECH_STARTUP_02", "nombre": "TechFlow Inc"},
    {"id": "RETAIL_CHAIN_03", "nombre": "MegaStore Retail"},
    {"id": "HEALTH_SVC_04", "nombre": "HealthCare Plus"},
    {"id": "FINANCE_GROUP_05", "nombre": "FinanceFlow"},
]

print("📋 Inserting customers...")
for cliente in clientes:
    cursor.execute(
        """
        INSERT OR IGNORE INTO customer_profiles
        (customer_id, name, context_type, first_contact, last_contact, total_interactions,
         churn_risk, lifetime_sentiment, notes)
        VALUES (?, ?, 'customer', ?, ?, 0, 0.3, 70, '')
        """,
        (
            cliente["id"],
            cliente["nombre"],
            datetime.now(),
            datetime.now(),
        ),
    )
    print(f"  ✅ {cliente['nombre']}")

conn.commit()

print("\n📊 Inserting conversations...")

conversation_payload = {
    "ACME_CORP_001": [
        (30, 85, "Excelente servicio, muy satisfecho", "RISING", "MEDIUM"),
        (24, 75, "Problemas con tiempos de respuesta", "DECLINING", "MEDIUM"),
        (18, 55, "Muy decepcionado con la calidad", "DECLINING", "HIGH"),
        (12, 35, "Considerando cambiar de proveedor", "DECLINING", "HIGH"),
        (3, 15, "Definitivamente nos vamos", "DECLINING", "HIGH"),
    ],
    "TECH_STARTUP_02": [
        (25, 85, "Excelente trabajo, dashboard intuitivo", "STABLE", "LOW"),
        (15, 86, "Muy contento, nos ayuda mucho", "STABLE", "LOW"),
        (5, 87, "Seguimos muy satisfechos", "STABLE", "LOW"),
    ],
    "RETAIL_CHAIN_03": [
        (30, 75, "Satisfecho generalmente", "STABLE", "MEDIUM"),
        (18, 55, "Algunos problemas pero nada crítico", "DECLINING", "MEDIUM"),
        (5, 45, "Consideramos otros proveedores", "DECLINING", "MEDIUM"),
    ],
    "HEALTH_SVC_04": [
        (30, 62, "Buen inicio pero necesita mejoras", "RISING", "LOW"),
        (18, 75, "Vemos mejoras significativas", "RISING", "LOW"),
        (5, 92, "Excelente, funciona perfecto", "RISING", "LOW"),
    ],
    "FINANCE_GROUP_05": [
        (25, 83, "Muy buen servicio, confiamos", "STABLE", "LOW"),
        (12, 84, "Excelente soporte continuo", "STABLE", "LOW"),
    ],
}

for customer_id, registros in conversation_payload.items():
    for days_ago, score, mensaje, tendencia, riesgo in registros:
        fecha = datetime.now() - timedelta(days=days_ago)
        cursor.execute(
            """
            INSERT INTO conversations
            (customer_id, context_type, analysis_date, messages, sentiment_score,
             trend, risk_level, predicted_action, confidence)
            VALUES (?, 'customer', ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer_id,
                fecha,
                json.dumps([mensaje]),
                score,
                tendencia,
                riesgo,
                "CHURN" if riesgo == "HIGH" else ("ESCALATION" if customer_id == "RETAIL_CHAIN_03" else "RETENTION"),
                0.78 if riesgo == "HIGH" else 0.9,
            ),
        )

conn.commit()

print("\n🔄 Updating customer aggregates...")

for cliente in clientes:
    cursor.execute(
        """
        SELECT AVG(sentiment_score), COUNT(*)
        FROM conversations
        WHERE customer_id = ?
        """,
        (cliente["id"],),
    )
    promedio, total = cursor.fetchone()

    if promedio is None:
        promedio = 70.0
    if total is None:
        total = 0

    if promedio < 40:
        churn = 0.9
    elif promedio < 55:
        churn = 0.75
    elif promedio < 70:
        churn = 0.55
    elif promedio < 80:
        churn = 0.25
    else:
        churn = 0.05

    cursor.execute(
        """
        UPDATE customer_profiles
        SET lifetime_sentiment = ?,
            churn_risk = ?,
            total_interactions = ?,
            last_contact = ?
        WHERE customer_id = ?
        """,
        (
            round(promedio, 2),
            churn,
            total,
            datetime.now(),
            cliente["id"],
        ),
    )

# Manual adjustments to align with scripted storyline
cursor.execute("UPDATE customer_profiles SET churn_risk = 0.85 WHERE customer_id = 'ACME_CORP_001'")
cursor.execute("UPDATE customer_profiles SET churn_risk = 0.55 WHERE customer_id = 'RETAIL_CHAIN_03'")
cursor.execute("UPDATE customer_profiles SET churn_risk = 0.05 WHERE customer_id IN ('TECH_STARTUP_02','FINANCE_GROUP_05')")
cursor.execute("UPDATE customer_profiles SET churn_risk = 0.09 WHERE customer_id = 'HEALTH_SVC_04'")

conn.commit()

print("\n🚨 Registering risk alerts...")

cursor.execute(
    """
    INSERT INTO risk_alerts (customer_id, alert_type, severity, created_at, resolved, notes)
    VALUES (?, 'CHURN_RISK', 'HIGH', ?, 0, ?)
    """,
    (
        "ACME_CORP_001",
        datetime.now(),
        "Crisis detectada: el sentimiento cayó de 85 a 15 en 30 días",
    ),
)

cursor.execute(
    """
    INSERT INTO risk_alerts (customer_id, alert_type, severity, created_at, resolved, notes)
    VALUES (?, 'CHURN_RISK', 'MEDIUM', ?, 0, ?)
    """,
    (
        "RETAIL_CHAIN_03",
        datetime.now() - timedelta(days=5),
        "Declive sostenido, comparando proveedores",
    ),
)

conn.commit()

print("\n📊 Database summary")
cursor.execute("SELECT COUNT(*) FROM customer_profiles")
print(f"  • Customers: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM conversations")
print(f"  • Conversations: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM risk_alerts")
print(f"  • Alerts: {cursor.fetchone()[0]}")
cursor.execute("SELECT ROUND(AVG(sentiment_score), 2) FROM conversations")
print(f"  • Avg Sentiment: {cursor.fetchone()[0]}/100")

conn.close()

print("\n✅ Demo data created successfully!")
