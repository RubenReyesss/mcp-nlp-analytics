#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para inspeccionar la base de datos SQLite que el MCP crea
"""

import sqlite3
import sys
import os

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ir al directorio raíz del proyecto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..')
os.chdir(project_root)

def show_database():
    """Mostrar contenido de la base de datos"""
    
    try:
        conn = sqlite3.connect('data/sentiment_analysis.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("\n" + "="*80)
        print("📊 EXPLORANDO LA BASE DE DATOS SQLITE3")
        print("="*80)
        
        # 1. customer_profiles
        print("\n1️⃣  TABLA: customer_profiles (Perfiles de Clientes)")
        print("-" * 80)
        cursor.execute('SELECT customer_id, churn_risk, lifetime_sentiment, total_interactions FROM customer_profiles')
        rows = cursor.fetchall()
        print(f"Total de clientes: {len(rows)}\n")
        if rows:
            for row in rows:
                print(f"  • {row['customer_id']:20} | Riesgo: {row['churn_risk']:6.1%} | Sentimiento: {row['lifetime_sentiment']:5.1f}/100 | Interacciones: {row['total_interactions']}")
        else:
            print("  (Sin datos aún)")
        
        # 2. conversations
        print("\n2️⃣  TABLA: conversations (Análisis Realizadas)")
        print("-" * 80)
        cursor.execute('SELECT customer_id, analysis_date, sentiment_score, trend, risk_level, predicted_action FROM conversations ORDER BY analysis_date DESC LIMIT 10')
        rows = cursor.fetchall()
        print(f"Total de análisis guardadas (mostrando últimas 10):\n")
        if rows:
            for i, row in enumerate(rows, 1):
                print(f"  {i}. {row['analysis_date']} | {row['customer_id']:18} | Sent: {row['sentiment_score']:5.1f} | Trend: {row['trend']:10} | Risk: {row['risk_level']:6} | Action: {row['predicted_action']}")
        else:
            print("  (Sin datos aún)")
        
        # 3. risk_alerts
        print("\n3️⃣  TABLA: risk_alerts (Alertas Automáticas)")
        print("-" * 80)
        cursor.execute('SELECT customer_id, alert_type, severity, created_at, resolved FROM risk_alerts ORDER BY created_at DESC')
        rows = cursor.fetchall()
        print(f"Total de alertas: {len(rows)}\n")
        if rows:
            for i, row in enumerate(rows, 1):
                status = "✅ RESUELTA" if row['resolved'] else "🚨 ACTIVA"
                print(f"  {i}. {row['created_at']} | {row['customer_id']:18} | Tipo: {row['alert_type']:15} | Severidad: {row['severity']:6} | {status}")
        else:
            print("  (Sin alertas aún)")
        
        # 4. Estadísticas
        print("\n4️⃣  ESTADÍSTICAS GLOBALES")
        print("-" * 80)
        
        cursor.execute('SELECT COUNT(DISTINCT customer_id) as count FROM conversations')
        unique_customers = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) as count FROM conversations')
        total_analyses = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(sentiment_score) as avg FROM conversations')
        avg_sentiment = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) as count FROM customer_profiles WHERE churn_risk > 0.7')
        at_risk = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) as count FROM risk_alerts WHERE resolved = 0')
        active_alerts = cursor.fetchone()[0]
        
        print(f"  • Clientes únicos: {unique_customers}")
        print(f"  • Análisis totales guardadas: {total_analyses}")
        print(f"  • Sentimiento promedio: {avg_sentiment:.1f}/100")
        print(f"  • Clientes en alto riesgo (>70%): {at_risk}")
        print(f"  • Alertas activas: {active_alerts}")
        
        conn.close()
        
        print("\n" + "="*80)
        print("✅ DATOS REALES EN sentiment_analysis.db")
        print("="*80)
        print("\nEsta BD se crea automáticamente cuando Claude usa las herramientas de análisis.")
        print("Cada análisis que realiza se guarda persistentemente aquí.\n")
        
    except FileNotFoundError:
        print("\n❌ BASE DE DATOS NO ENCONTRADA")
        print("   Aún no se ha creado sentiment_analysis.db")
        print("   Se creará automáticamente cuando uses el MCP en Claude Desktop\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")

if __name__ == "__main__":
    show_database()
