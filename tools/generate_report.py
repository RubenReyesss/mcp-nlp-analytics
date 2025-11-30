#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para generar reporte HTML con graficas usando Chart.js
"""

import sqlite3
import os
import json
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..')
os.chdir(project_root)

def get_color(valor):
    if valor > 70:
        return '#e74c3c'
    elif valor > 50:
        return '#f39c12'
    else:
        return '#27ae60'

def generar_reporte():
    conn = sqlite3.connect('data/sentiment_analysis.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM customer_profiles ORDER BY churn_risk DESC')
    clientes = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) as count FROM conversations')
    total_analyses = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(sentiment_score) as avg FROM conversations')
    avg_sentiment = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) as count FROM risk_alerts WHERE resolved = 0')
    active_alerts = cursor.fetchone()[0]
    
    nombres_clientes = [c['customer_id'] for c in clientes]
    riesgos = [c['churn_risk'] * 100 for c in clientes]
    sentimientos = [c['lifetime_sentiment'] for c in clientes]
    colores = [get_color(r) for r in riesgos]
    
    tabla_clientes = ""
    for c in clientes:
        if c['churn_risk'] > 0.7:
            clase = "riesgo-rojo"
        elif c['churn_risk'] > 0.5:
            clase = "riesgo-naranja"
        else:
            clase = "riesgo-verde"
        
        tabla_clientes += f"""        <tr class="{clase}">
            <td>{c['customer_id']}</td>
            <td>{c['lifetime_sentiment']:.1f}/100</td>
            <td>{c['churn_risk']:.1%}</td>
            <td>{c['total_interactions']}</td>
            <td>{c['last_contact']}</td>
        </tr>
"""
    
    colores_json = json.dumps(colores)
    nombres_json = json.dumps(nombres_clientes)
    riesgos_json = json.dumps(riesgos)
    sentimientos_json = json.dumps(sentimientos)
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentiment Evolution Tracker - Reporte</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.3);
            padding: 40px;
        }}
        
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 5px;
            font-size: 2.5em;
        }}
        
        .fecha {{
            text-align: center;
            color: #999;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .stat .numero {{
            font-size: 40px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .stat .label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .graficas {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .grafica-container {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .grafica-container h3 {{
            margin-bottom: 20px;
            color: #333;
            font-size: 1.2em;
        }}
        
        h2 {{
            margin-top: 40px;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        .riesgo-rojo {{
            border-left: 4px solid #e74c3c;
            background: #ffe5e5 !important;
        }}
        
        .riesgo-naranja {{
            border-left: 4px solid #f39c12;
            background: #fff5e5 !important;
        }}
        
        .riesgo-verde {{
            border-left: 4px solid #27ae60;
            background: #e5ffe5 !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Sentiment Evolution Tracker - Dashboard</h1>
        <p class="fecha">Reporte generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        
        <div class="stats">
            <div class="stat">
                <div class="numero">{len(clientes)}</div>
                <div class="label">Clientes</div>
            </div>
            <div class="stat">
                <div class="numero">{total_analyses}</div>
                <div class="label">Analisis</div>
            </div>
            <div class="stat">
                <div class="numero">{avg_sentiment:.0f}</div>
                <div class="label">Sentimiento Promedio</div>
            </div>
            <div class="stat">
                <div class="numero">{active_alerts}</div>
                <div class="label">Alertas Activas</div>
            </div>
        </div>
        
        <h2>Graficas de Analisis</h2>
        <div class="graficas">
            <div class="grafica-container">
                <h3>Riesgo de Churn por Cliente</h3>
                <canvas id="riesgoChart"></canvas>
            </div>
            <div class="grafica-container">
                <h3>Sentimiento Promedio por Cliente</h3>
                <canvas id="sentimentoChart"></canvas>
            </div>
        </div>
        
        <h2>Clientes Registrados</h2>
        <table>
            <thead>
                <tr>
                    <th>Cliente ID</th>
                    <th>Sentimiento</th>
                    <th>Riesgo Churn</th>
                    <th>Interacciones</th>
                    <th>Ultimo Contacto</th>
                </tr>
            </thead>
            <tbody>
{tabla_clientes}            </tbody>
        </table>
    </div>
    
    <script>
        const ctxRiesgo = document.getElementById('riesgoChart').getContext('2d');
        new Chart(ctxRiesgo, {{
            type: 'bar',
            data: {{
                labels: {nombres_json},
                datasets: [{{
                    label: 'Riesgo de Churn (%)',
                    data: {riesgos_json},
                    backgroundColor: {colores_json},
                    borderColor: '#667eea',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            callback: function(value) {{ return value + '%'; }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});
        
        const ctxSentimento = document.getElementById('sentimentoChart').getContext('2d');
        new Chart(ctxSentimento, {{
            type: 'line',
            data: {{
                labels: {nombres_json},
                datasets: [{{
                    label: 'Sentimiento (0-100)',
                    data: {sentimientos_json},
                    borderColor: '#764ba2',
                    backgroundColor: 'rgba(118, 75, 162, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#764ba2',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }},
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    conn.close()
    
    with open('data/reporte_clientes.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ Reporte con graficas generado!")
    print("📊 Ubicacion: data/reporte_clientes.html")
    print("🌐 Abre el archivo en tu navegador para ver las graficas")

if __name__ == "__main__":
    generar_reporte()
