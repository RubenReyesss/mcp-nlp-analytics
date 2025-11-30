#!/usr/bin/env python
# -*- coding: utf-8 -*-


import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

st.set_page_config(page_title="Sentiment Evolution Tracker", layout="wide")

# CSS personalizado
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 14px;
        opacity: 0.8;
    }
    .high-risk {
        background-color: #ffe5e5;
        border-left: 4px solid #e74c3c;
    }
    .medium-risk {
        background-color: #fff5e5;
        border-left: 4px solid #f39c12;
    }
    .low-risk {
        background-color: #e5ffe5;
        border-left: 4px solid #27ae60;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect('data/sentiment_analysis.db')
    conn.row_factory = sqlite3.Row
    return conn

# Título y descripción
st.title("🎯 Sentiment Evolution Tracker")
st.markdown("*Sistema MCP para monitoreo de satisfacción empresarial*")

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Detalles Clientes", "📈 Tendencias", "🛠️ MCP Tools"])

# TAB 1: DASHBOARD
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Métricas
    cursor.execute('SELECT COUNT(*) as count FROM customer_profiles')
    num_clientes = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) as count FROM conversations')
    num_analyses = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(sentiment_score) as avg FROM conversations')
    avg_sentiment = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) as count FROM risk_alerts WHERE resolved = 0')
    active_alerts = cursor.fetchone()[0]
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Clientes</div>
            <div class="metric-value">{num_clientes}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Análisis</div>
            <div class="metric-value">{num_analyses}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Sentimiento Promedio</div>
            <div class="metric-value">{avg_sentiment:.0f}/100</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Alertas Activas</div>
            <div class="metric-value">{active_alerts}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Gráficas
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Gráfica de riesgo por cliente
        cursor.execute('SELECT customer_id, churn_risk * 100 as risk FROM customer_profiles ORDER BY risk DESC')
        datos = cursor.fetchall()
        
        clientes_ids = [d['customer_id'] for d in datos]
        riesgos = [d['risk'] for d in datos]
        
        fig_riesgo = go.Figure(data=[
            go.Bar(x=clientes_ids, y=riesgos,
                   marker=dict(color=['#e74c3c' if r > 70 else '#f39c12' if r > 50 else '#27ae60' for r in riesgos]))
        ])
        fig_riesgo.update_layout(title="Riesgo de Churn por Cliente (%)", xaxis_title="Cliente", yaxis_title="Riesgo (%)")
        st.plotly_chart(fig_riesgo, use_container_width=True)
    
    with col_right:
        # Gráfica de sentimiento por cliente
        cursor.execute('SELECT customer_id, lifetime_sentiment FROM customer_profiles ORDER BY lifetime_sentiment DESC')
        datos_sent = cursor.fetchall()
        
        clientes_sent = [d['customer_id'] for d in datos_sent]
        sentimientos = [d['lifetime_sentiment'] for d in datos_sent]
        
        fig_sent = go.Figure(data=[
            go.Bar(x=clientes_sent, y=sentimientos,
                   marker=dict(color='#764ba2'))
        ])
        fig_sent.update_layout(title="Sentimiento Promedio por Cliente", xaxis_title="Cliente", yaxis_title="Sentimiento (0-100)")
        st.plotly_chart(fig_sent, use_container_width=True)
    
    st.divider()
    
    # Tabla de clientes
    st.subheader("📋 Clientes Registrados")
    cursor.execute('''
        SELECT customer_id, lifetime_sentiment, churn_risk, total_interactions, last_contact
        FROM customer_profiles
        ORDER BY churn_risk DESC
    ''')
    
    clientes_data = []
    for row in cursor.fetchall():
        clientes_data.append({
            'Cliente': row['customer_id'],
            'Sentimiento': f"{row['lifetime_sentiment']:.1f}",
            'Riesgo Churn': f"{row['churn_risk']:.1%}",
            'Interacciones': row['total_interactions'],
            'Último Contacto': row['last_contact'][:10] if row['last_contact'] else 'N/A'
        })
    
    df = pd.DataFrame(clientes_data)
    st.dataframe(df, use_container_width=True)
    
    conn.close()

# TAB 2: DETALLES CLIENTES
with tab2:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT customer_id FROM customer_profiles ORDER BY customer_id')
    clientes = [row[0] for row in cursor.fetchall()]
    
    cliente_seleccionado = st.selectbox("Selecciona un cliente:", clientes)
    
    if cliente_seleccionado:
        cursor.execute('SELECT * FROM customer_profiles WHERE customer_id = ?', (cliente_seleccionado,))
        cliente = cursor.fetchone()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sentimiento Promedio", f"{cliente['lifetime_sentiment']:.1f}/100")
        with col2:
            st.metric("Riesgo Churn", f"{cliente['churn_risk']:.1%}")
        with col3:
            st.metric("Interacciones", cliente['total_interactions'])
        
        st.subheader(f"Historial de {cliente_seleccionado}")
        
        cursor.execute('''
            SELECT timestamp, message, sentiment_score
            FROM conversations
            WHERE customer_id = ?
            ORDER BY timestamp DESC
        ''', (cliente_seleccionado,))
        
        conversaciones = cursor.fetchall()
        
        for conv in conversaciones:
            sentiment = conv['sentiment_score']
            if sentiment > 70:
                color = "🟢"
            elif sentiment > 50:
                color = "🟡"
            else:
                color = "🔴"
            
            st.write(f"{color} **{conv['timestamp'][:10]}** - Sentimiento: {sentiment}/100")
            st.write(f"*{conv['message']}*")
            st.divider()
    
    conn.close()

# TAB 3: TENDENCIAS
with tab3:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT customer_id FROM customer_profiles ORDER BY customer_id')
    clientes = [row[0] for row in cursor.fetchall()]
    
    clientes_multi = st.multiselect("Selecciona clientes para comparar:", clientes, default=clientes[:2])
    
    if clientes_multi:
        for cliente in clientes_multi:
            cursor.execute('''
                SELECT timestamp, sentiment_score
                FROM conversations
                WHERE customer_id = ?
                ORDER BY timestamp
            ''', (cliente,))
            
            datos = cursor.fetchall()
            
            if datos:
                fechas = [d['timestamp'][:10] for d in datos]
                sentimientos = [d['sentiment_score'] for d in datos]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=fechas, y=sentimientos, mode='lines+markers', name=cliente))
                fig.update_layout(title=f"Evolución de Sentimiento - {cliente}")
                st.plotly_chart(fig, use_container_width=True)
    
    conn.close()

# TAB 4: MCP TOOLS
with tab4:
    st.subheader("🛠️ Herramientas MCP Disponibles")
    
    tool_info = {
        "analyze_sentiment_evolution": {
            "desc": "Analiza si el sentimiento SUBE (RISING), BAJA (DECLINING) o se mantiene (STABLE)",
            "uso": "Detecta tendencias para alertar sobre clientes en riesgo"
        },
        "detect_risk_signals": {
            "desc": "Detecta palabras clave de riesgo en mensajes (cancelar, problema, insatisfecho)",
            "uso": "Identifica inmediatamente problemas graves"
        },
        "predict_next_action": {
            "desc": "Predice si el cliente hará CHURN, RESOLUTION o ESCALATION",
            "uso": "Anticipa próximas acciones para intervenir"
        },
        "get_customer_history": {
            "desc": "Obtiene perfil completo del cliente con historial",
            "uso": "Análisis detallado para decisiones gerenciales"
        },
        "get_high_risk_customers": {
            "desc": "Lista clientes por encima de threshold de riesgo",
            "uso": "Priorizar intervención en clientes críticos"
        },
        "get_database_statistics": {
            "desc": "Estadísticas globales del sistema",
            "uso": "Dashboard ejecutivo de KPIs"
        },
        "save_analysis": {
            "desc": "Guarda análisis manual de un cliente",
            "uso": "Registro de decisiones y acciones tomadas"
        }
    }
    
    for tool, info in tool_info.items():
        with st.expander(f"📌 {tool}"):
            st.write(f"**Descripción:** {info['desc']}")
            st.write(f"**Uso:** {info['uso']}")

st.divider()
st.markdown("---")
st.markdown("""
    **Sentiment Evolution Tracker v1.0**
    
    Sistema MCP para monitoreo de satisfacción empresarial.
    Desarrollado para Hugging Face MCP 1st Birthday Hackathon.
    
    [📖 Docs](https://github.com/rubenreyes/mcp-nlp-server) | [🐙 GitHub](https://github.com) | [💬 Discord](https://discord.gg/huggingface)
""")
