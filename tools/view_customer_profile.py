#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para ver el perfil COMPLETO de un cliente específico
"""

import sqlite3
import json
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

def ver_perfil_cliente(customer_id):
    """Ver perfil completo de un cliente"""
    
    try:
        conn = sqlite3.connect('data/sentiment_analysis.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Obtener perfil
        cursor.execute('SELECT * FROM customer_profiles WHERE customer_id = ?', (customer_id,))
        profile = cursor.fetchone()
        
        if not profile:
            print(f"\n❌ Cliente '{customer_id}' no encontrado en la BD\n")
            return
        
        print("\n" + "="*80)
        print(f"👤 PERFIL COMPLETO DEL CLIENTE: {customer_id}")
        print("="*80)
        
        print("\n📊 INFORMACIÓN DEL CLIENTE:")
        print("-" * 80)
        print(f"  Cliente ID:            {profile['customer_id']}")
        print(f"  Tipo de contexto:      {profile['context_type']}")
        print(f"  Primer contacto:       {profile['first_contact']}")
        print(f"  Último contacto:       {profile['last_contact']}")
        print(f"  Total de interacciones: {profile['total_interactions']}")
        print(f"  Sentimiento promedio:  {profile['lifetime_sentiment']:.1f}/100")
        print(f"  Riesgo de churn:       {profile['churn_risk']:.1%}")
        if profile['notes']:
            print(f"  Notas:                 {profile['notes']}")
        
        # 2. Análisis previas
        print("\n📝 ANÁLISIS REALIZADAS:")
        print("-" * 80)
        cursor.execute('''
            SELECT id, analysis_date, sentiment_score, trend, risk_level, 
                   predicted_action, confidence, messages 
            FROM conversations 
            WHERE customer_id = ? 
            ORDER BY analysis_date DESC
        ''', (customer_id,))
        analyses = cursor.fetchall()
        
        if analyses:
            print(f"Total de análisis guardadas: {len(analyses)}\n")
            for i, analysis in enumerate(analyses, 1):
                print(f"  {i}. {analysis['analysis_date']}")
                print(f"     Sentimiento: {analysis['sentiment_score']:.1f}/100")
                print(f"     Tendencia: {analysis['trend']}")
                print(f"     Nivel de riesgo: {analysis['risk_level']}")
                print(f"     Acción predicha: {analysis['predicted_action']}")
                if analysis['confidence']:
                    print(f"     Confianza: {analysis['confidence']:.1%}")
                
                # Mostrar mensajes
                try:
                    messages = json.loads(analysis['messages'])
                    print(f"     Mensajes analizados ({len(messages)}):")
                    for msg in messages:
                        print(f"       - {msg}")
                except:
                    pass
                print()
        else:
            print("  (Sin análisis previas)")
        
        # 3. Alertas activas
        print("🚨 ALERTAS:")
        print("-" * 80)
        cursor.execute('''
            SELECT id, alert_type, severity, created_at, resolved, notes
            FROM risk_alerts 
            WHERE customer_id = ? 
            ORDER BY created_at DESC
        ''', (customer_id,))
        alerts = cursor.fetchall()
        
        if alerts:
            print(f"Total de alertas: {len(alerts)}\n")
            for i, alert in enumerate(alerts, 1):
                status = "✅ RESUELTA" if alert['resolved'] else "🚨 ACTIVA"
                print(f"  {i}. {status}")
                print(f"     Tipo: {alert['alert_type']}")
                print(f"     Severidad: {alert['severity']}")
                print(f"     Creada: {alert['created_at']}")
                if alert['notes']:
                    print(f"     Notas: {alert['notes']}")
                print()
        else:
            print("  (Sin alertas)")
        
        # 4. Resumen
        print("📈 RESUMEN:")
        print("-" * 80)
        if len(analyses) > 1:
            first_sentiment = json.loads(analyses[-1]['messages']) if analyses else []
            last_sentiment = analyses[0]['sentiment_score']
            trend = analyses[0]['trend']
            
            print(f"  Tendencia general: {trend}")
            print(f"  Sentimiento inicial (primer análisis): {analyses[-1]['sentiment_score']:.1f}/100")
            print(f"  Sentimiento actual (último análisis): {last_sentiment:.1f}/100")
            print(f"  Cambio neto: {last_sentiment - analyses[-1]['sentiment_score']:+.1f} puntos")
            
            if profile['churn_risk'] > 0.7:
                print(f"\n  ⚠️  CLIENTE EN ALTO RIESGO ({profile['churn_risk']:.1%})")
                print(f"  Recomendación: INTERVENCIÓN INMEDIATA NECESARIA")
            elif profile['churn_risk'] > 0.5:
                print(f"\n  ⚠️  CLIENTE EN RIESGO MEDIO ({profile['churn_risk']:.1%})")
                print(f"  Recomendación: Monitoreo cercano")
            else:
                print(f"\n  ✅ Cliente en buen estado ({profile['churn_risk']:.1%} riesgo)")
        
        conn.close()
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")


def listar_clientes():
    """Listar todos los clientes disponibles"""
    
    try:
        conn = sqlite3.connect('sentiment_analysis.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT customer_id FROM customer_profiles ORDER BY customer_id')
        clientes = cursor.fetchall()
        
        if clientes:
            print("\n📋 CLIENTES DISPONIBLES EN LA BD:\n")
            for i, (customer_id,) in enumerate(clientes, 1):
                print(f"  {i}. {customer_id}")
            print()
        else:
            print("\n  (Sin clientes aún)\n")
        
        conn.close()
        
    except:
        pass


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        # Mostrar clientes disponibles
        print("\n" + "="*80)
        print("👤 VER PERFIL DE CLIENTE")
        print("="*80)
        
        listar_clientes()
        
        print("USO:")
        print("  python ver_perfil_cliente.py CUST_NUEVO_001")
        print("  python ver_perfil_cliente.py CUST_001_ACME")
        print()
    else:
        customer_id = sys.argv[1]
        ver_perfil_cliente(customer_id)
