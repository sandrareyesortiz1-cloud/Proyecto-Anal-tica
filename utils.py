import requests
import plotly.graph_objects as go
from config import API_URL, COLORS, COLORS_ALPHA, UMBRALES_RIESGO, UMBRALES_CLUSTER

def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error verificando salud de API: {e}")
        return None

def get_kmeans_features():
    try:
        response = requests.get(f"{API_URL}/kmeans/features", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('features_order', [])
        return []
    except Exception as e:
        print(f"Error obteniendo features KMeans: {e}")
        return []

def predict_catboost(data):
    try:
        response = requests.post(f"{API_URL}/predict/catboost", json=data, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error en predicción CatBoost: {e}")
        return None

def predict_kmeans(valores):
    try:
        response = requests.post(f"{API_URL}/predict/kmeans", json={"valores": valores}, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error en predicción KMeans: {e}")
        return None

def get_risk_level(prediccion):
    if prediccion < UMBRALES_RIESGO['bajo']:
        return 'Bajo', COLORS['secondary']
    elif prediccion < UMBRALES_RIESGO['medio']:
        return 'Medio', COLORS['warning']
    else:
        return 'Alto', COLORS['danger']

def get_vulnerability_level(cluster):
    nivel = UMBRALES_CLUSTER.get(cluster, 'Desconocido')
    color_map = {
        'Bajo': COLORS['secondary'],
        'Medio': COLORS['info'],
        'Alto': COLORS['warning'],
        'Crítico': COLORS['danger']
    }
    return nivel, color_map.get(nivel, COLORS['neutral'])

def create_gauge_chart(value, title, max_value=100):
    nivel, color = get_risk_level(value)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': COLORS['text'], 'family': 'Inter, sans-serif'}},
        number={'suffix': " /100k", 'font': {'size': 32, 'color': COLORS['text'], 'family': 'Inter, sans-serif'}},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': COLORS['border'], 'tickfont': {'size': 11, 'color': COLORS['neutral']}},
            'bar': {'color': color, 'thickness': 0.7},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': COLORS['border'],
            'steps': [
                {'range': [0, UMBRALES_RIESGO['bajo']], 'color': COLORS_ALPHA['secondary_10']},
                {'range': [UMBRALES_RIESGO['bajo'], UMBRALES_RIESGO['medio']], 'color': COLORS_ALPHA['warning_10']},
                {'range': [UMBRALES_RIESGO['medio'], max_value], 'color': COLORS_ALPHA['danger_10']}
            ],
            'threshold': {'line': {'color': color, 'width': 3}, 'thickness': 0.8, 'value': value}
        }
    ))
    
    fig.update_layout(
        height=320, margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)', font={'family': 'Inter, sans-serif'}
    )
    return fig