#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para mostrar datos con gráficas ASCII en la terminal
Visualización profesional sin necesidad de navegador
"""

import sqlite3
import os
from datetime import datetime

def get_project_root():
    """Obtener ruta del proyecto"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, '..')

def crear_barra_progreso(valor, max_valor=100, ancho=30):
    """Crear barra de progreso ASCII"""
    if max_valor == 0:
        porcentaje = 0
    else:
        porcentaje = (valor / max_valor) * 100
    
    barra_llena = int((porcentaje / 100) * ancho)
    barra_vacia = ancho - barra_llena
    
    barra = f"[{'█' * barra_llena}{'░' * barra_vacia}] {porcentaje:.0f}%"
    return barra

def mostrar_datos_con_graficas():
    """Mostrar datos con gráficas ASCII"""
    
    os.chdir(get_project_root())
    
    conn = sqlite3.connect('data/sentiment_analysis.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener estadísticas
    cursor.execute('SELECT COUNT(*) as count FROM customer_profiles')
    total_clientes = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) as count FROM conversations')
    total_analyses = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(sentiment_score) as avg FROM conversations')
    avg_sentiment = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) as count FROM risk_alerts WHERE resolved = 0')
    active_alerts = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT customer_id, churn_risk, lifetime_sentiment, total_interactions 
        FROM customer_profiles 
        ORDER BY churn_risk DESC
    ''')
    clientes = cursor.fetchall()
    
    # Mostrar header
    print("\n" + "="*70)
    print("   SENTIMENT EVOLUTION TRACKER - DASHBOARD EJECUTIVO")
    print("="*70 + "\n")
    
    # Estadísticas principales
    print("📊 ESTADÍSTICAS GENERALES")
    print("-" * 70)
    print(f"  Total Clientes:        {total_clientes}")
    print(f"  Total Análisis:        {total_analyses}")
    print(f"  Alertas Activas:       {active_alerts}")
    print(f"  Sentimiento Promedio:  {avg_sentiment:.1f}/100")
    print()
    
    # Gráfica de sentimiento promedio
    print("📈 SENTIMIENTO PROMEDIO (0-100)")
    print("-" * 70)
    sentimiento_barra = crear_barra_progreso(avg_sentiment, 100, 40)
    color_sentimiento = "🟢" if avg_sentiment > 60 else "🟡" if avg_sentiment > 40 else "🔴"
    print(f"  {color_sentimiento} {sentimiento_barra}")
    print()
    
    # Tabla de clientes con gráficas
    print("👥 CLIENTES POR RIESGO DE CHURN")
    print("-" * 70)
    print(f"{'ID':<15} {'RIESGO':<25} {'SENTIM':<12} {'INTERACT':<10}")
    print("-" * 70)
    
    for cliente in clientes:
        customer_id = cliente['customer_id'][:12]
        churn_risk = cliente['churn_risk']
        sentiment = cliente['lifetime_sentiment']
        interactions = cliente['total_interactions']
        
        # Barra de riesgo
        riesgo_barra = crear_barra_progreso(churn_risk * 100, 100, 20)
        
        # Icono de riesgo
        if churn_risk > 0.7:
            icon = "🔴"
        elif churn_risk > 0.5:
            icon = "🟡"
        else:
            icon = "🟢"
        
        print(f"{customer_id:<15} {icon} {riesgo_barra:<24} {sentiment:>6.1f}/100  {interactions:>8}")
    
    print()
    print("="*70)
    print("  Leyenda: 🔴 Alto Riesgo (>70%)  🟡 Medio Riesgo (>50%)  🟢 Bajo Riesgo")
    print("="*70 + "\n")
    
    # Alertas detalladas
    print("⚠️  ALERTAS ACTIVAS")
    print("-" * 70)
    cursor.execute('''
        SELECT customer_id, alert_type, severity, created_at 
        FROM risk_alerts 
        WHERE resolved = 0
        ORDER BY created_at DESC
    ''')
    alerts = cursor.fetchall()
    
    if alerts:
        for alert in alerts:
            severity_icon = "🔴" if alert['severity'] == 'HIGH' else "🟡"
            print(f"  {severity_icon} [{alert['severity']}] {alert['customer_id']}: {alert['alert_type']}")
            print(f"     Creada: {alert['created_at']}")
    else:
        print("  ✅ Sin alertas activas")
    
    print()
    
    # Análisis recientes
    print("📋 ÚLTIMOS 5 ANÁLISIS")
    print("-" * 70)
    cursor.execute('''
        SELECT customer_id, sentiment_score, trend, predicted_action, analysis_date
        FROM conversations
        ORDER BY analysis_date DESC
        LIMIT 5
    ''')
    recent = cursor.fetchall()
    
    for i, analysis in enumerate(recent, 1):
        sentiment_icon = "📈" if analysis['trend'] == 'RISING' else "📉" if analysis['trend'] == 'DECLINING' else "➡️ "
        action_icon = "🚨" if analysis['predicted_action'] == 'CHURN' else "✅" if analysis['predicted_action'] == 'RESOLUTION' else "⚠️ "
        
        print(f"  {i}. {analysis['customer_id']}")
        print(f"     {sentiment_icon} Sentimiento: {analysis['sentiment_score']:.0f}/100 | Tendencia: {analysis['trend']}")
        print(f"     {action_icon} Acción: {analysis['predicted_action']}")
        print(f"     Fecha: {analysis['analysis_date']}")
    
    print()
    print("="*70 + "\n")
    
    conn.close()

if __name__ == "__main__":
    mostrar_datos_con_graficas()
