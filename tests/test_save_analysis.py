"""
Test para verificar que la herramienta save_analysis funciona correctamente
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database_manager import AnalysisDatabase
import json

def test_save_analysis():
    """Prueba que save_analysis guarda correctamente en la BD"""
    
    print("\n" + "="*80)
    print("TEST: save_analysis")
    print("="*80)
    
    # Crear instancia de DB (usa BD existente)
    db = AnalysisDatabase(db_path="data/sentiment_analysis.db")
    
    # Datos de prueba: análisis del cliente Luis Ramírez
    customer_id = "LUIS_RAMIREZ"
    context_type = "customer"
    messages = [
        "Cliente: Hola, necesito ayuda urgente con mi cuenta",
        "Soporte: Claro, ¿cuál es el problema específicamente?",
        "Cliente: Llevo UNA SEMANA esperando una respuesta y nadie me ayuda",
        "Soporte: Disculpe el retraso, voy a verificar inmediatamente",
        "Cliente: Esto es inaceptable. Ya perdí la confianza en ustedes",
        "Soporte: Lamento mucho. ¿Qué información necesita?",
        "Cliente: Ya es demasiado tarde. Me voy con la competencia. No quiero seguir aquí",
        "Soporte: Por favor, permítame escalarlo",
        "Cliente: No, ya decidí. Cancelen mi contrato. Adiós"
    ]
    
    analysis = {
        "current_sentiment": 48,  # Muy negativo
        "trend": "DECLINING",      # De positivo a muy negativo
        "risk_level": "HIGH",
        "predicted_action": "CHURN",
        "confidence": 0.85
    }
    
    print(f"\n📝 Guardando análisis para cliente: {customer_id}")
    print(f"   - Mensajes: {len(messages)}")
    print(f"   - Sentimiento: {analysis['current_sentiment']}/100")
    print(f"   - Tendencia: {analysis['trend']}")
    print(f"   - Confianza: {analysis['confidence']}")
    
    # Guardar
    try:
        analysis_id = db.save_analysis(customer_id, context_type, messages, analysis)
        print(f"\n✅ ÉXITO: Análisis guardado con ID: {analysis_id}")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False
    
    # Verificar que se guardó
    print(f"\n🔍 Verificando que se guardó...")
    try:
        history = db.get_customer_history(customer_id)
        
        if history['profile']:
            print(f"✅ Perfil encontrado:")
            print(f"   - ID: {history['profile']['customer_id']}")
            print(f"   - Total interacciones: {history['profile']['total_interactions']}")
            print(f"   - Riesgo de churn: {history['profile']['churn_risk']}")
        
        if history['analyses']:
            print(f"\n✅ Análisis encontrados: {len(history['analyses'])}")
            latest = history['analyses'][0]  # El más reciente
            print(f"   - Fecha: {latest['analysis_date']}")
            print(f"   - Sentimiento: {latest['sentiment_score']}")
            print(f"   - Tendencia: {latest['trend']}")
            print(f"   - Acción: {latest['predicted_action']}")
        
        if history['active_alerts']:
            print(f"\n⚠️  Alertas activas: {len(history['active_alerts'])}")
            for alert in history['active_alerts']:
                print(f"   - Tipo: {alert['alert_type']}")
                print(f"   - Severidad: {alert['severity']}")
        
        return True
    
    except Exception as e:
        print(f"❌ ERROR en verificación: {str(e)}")
        return False

def test_get_statistics():
    """Verifica que las estadísticas se actualizaron"""
    print("\n" + "="*80)
    print("TEST: get_database_statistics")
    print("="*80)
    
    db = AnalysisDatabase(db_path="data/sentiment_analysis.db")
    
    stats = db.get_statistics()
    
    print(f"\n📊 Estadísticas de la BD:")
    print(f"   - Total clientes: {stats['total_customers']}")
    print(f"   - Clientes en riesgo: {stats['customers_at_risk']}")
    print(f"   - Alertas activas: {stats['active_alerts']}")
    print(f"   - Sentimiento promedio: {stats['average_sentiment']:.1f}/100")
    print(f"   - BD: {stats['database_file']}")
    
    if stats['total_customers'] > 0:
        print("\n✅ Base de datos contiene datos")
        return True
    else:
        print("\n❌ Base de datos vacía")
        return False

if __name__ == "__main__":
    print("\n" + "🧪 "*20)
    print("PRUEBAS DE save_analysis")
    print("🧪 "*20)
    
    try:
        result1 = test_save_analysis()
        result2 = test_get_statistics()
        
        print("\n" + "="*80)
        if result1 and result2:
            print("✅ TODAS LAS PRUEBAS PASARON")
        else:
            print("❌ ALGUNAS PRUEBAS FALLARON")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {str(e)}")
        import traceback
        traceback.print_exc()
