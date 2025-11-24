import os
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc
from datetime import datetime
import json

# ============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================================================

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Paleta de colores moderna y profesional
COLORS = {
    'primary': '#3b82f6',      # Blue-500
    'secondary': '#10b981',    # Green-500
    'danger': '#ef4444',       # Red-500
    'warning': '#f59e0b',      # Amber-500
    'info': '#06b6d4',         # Cyan-500
    'neutral': '#64748b',      # Slate-500
    'bg': '#f8fafc',           # Slate-50
    'card': '#ffffff',
    'border': '#e2e8f0',       # Slate-200
    'text': '#1e293b',         # Slate-800
    'text_muted': '#94a3b8'    # Slate-400
}

# Colores con transparencia (formato RGBA)
COLORS_ALPHA = {
    'primary_10': 'rgba(59, 130, 246, 0.1)',
    'secondary_10': 'rgba(16, 185, 129, 0.1)',
    'danger_10': 'rgba(239, 68, 68, 0.1)',
    'warning_10': 'rgba(245, 158, 11, 0.1)',
}

# Umbrales configurables
UMBRALES_RIESGO = {
    'bajo': 15,
    'medio': 30,
    'alto': float('inf')
}

UMBRALES_CLUSTER = {
    0: 'Bajo',
    1: 'Medio',
    2: 'Alto',
    3: 'Crítico'
}

# Opciones para formularios
SEXO_OPTIONS = ['F', 'M']
GRUPO_EDAD_OPTIONS = ['0-4', '5-9', '10-14', '15-17']
CICLO_VITAL_OPTIONS = ['primera_infancia', 'infancia', 'adolescencia']
ESCOLARIDAD_OPTIONS = ['sin_escolaridad', 'primaria_incompleta', 'primaria_completa', 
                       'secundaria_incompleta', 'secundaria_completa', 'tecnico', 'universitario']
DEPARTAMENTOS = ['Amazonas', 'Antioquia', 'Arauca', 'Atlántico', 'Bolívar', 'Boyacá', 
                 'Caldas', 'Caquetá', 'Casanare', 'Cauca', 'Cesar', 'Chocó', 'Córdoba',
                 'Cundinamarca', 'Guainía', 'Guaviare', 'Huila', 'La Guajira', 'Magdalena',
                 'Meta', 'Nariño', 'Norte de Santander', 'Putumayo', 'Quindío', 'Risaralda',
                 'San Andrés y Providencia', 'Santander', 'Sucre', 'Tolima', 'Valle del Cauca',
                 'Vaupés', 'Vichada']

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def check_api_health():
    """Verificar estado de la API"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error verificando salud de API: {e}")
        return None

def get_kmeans_features():
    """Obtener orden de features para KMeans"""
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
    """Realizar predicción con CatBoost"""
    try:
        response = requests.post(f"{API_URL}/predict/catboost", json=data, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error en predicción CatBoost: {e}")
        return None

def predict_kmeans(valores):
    """Asignar cluster con KMeans"""
    try:
        response = requests.post(f"{API_URL}/predict/kmeans", json={"valores": valores}, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error en predicción KMeans: {e}")
        return None

def get_risk_level(prediccion):
    """Determinar nivel de riesgo según umbral"""
    if prediccion < UMBRALES_RIESGO['bajo']:
        return 'Bajo', COLORS['secondary']
    elif prediccion < UMBRALES_RIESGO['medio']:
        return 'Medio', COLORS['warning']
    else:
        return 'Alto', COLORS['danger']

def get_vulnerability_level(cluster):
    """Mapear cluster a nivel de vulnerabilidad"""
    nivel = UMBRALES_CLUSTER.get(cluster, 'Desconocido')
    color_map = {
        'Bajo': COLORS['secondary'],
        'Medio': COLORS['info'],
        'Alto': COLORS['warning'],
        'Crítico': COLORS['danger']
    }
    return nivel, color_map.get(nivel, COLORS['neutral'])

def create_gauge_chart(value, title, max_value=100):
    """Crear gráfico tipo velocímetro - CORREGIDO"""
    nivel, color = get_risk_level(value)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': title, 
            'font': {'size': 16, 'color': COLORS['text'], 'family': 'Inter, sans-serif'}
        },
        number={
            'suffix': " /100k", 
            'font': {'size': 32, 'color': COLORS['text'], 'family': 'Inter, sans-serif'}
        },
        gauge={
            'axis': {
                'range': [None, max_value], 
                'tickwidth': 1, 
                'tickcolor': COLORS['border'],
                'tickfont': {'size': 11, 'color': COLORS['neutral']}
            },
            'bar': {'color': color, 'thickness': 0.7},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': COLORS['border'],
            'steps': [
                {
                    'range': [0, UMBRALES_RIESGO['bajo']], 
                    'color': COLORS_ALPHA['secondary_10']
                },
                {
                    'range': [UMBRALES_RIESGO['bajo'], UMBRALES_RIESGO['medio']], 
                    'color': COLORS_ALPHA['warning_10']
                },
                {
                    'range': [UMBRALES_RIESGO['medio'], max_value], 
                    'color': COLORS_ALPHA['danger_10']
                }
            ],
            'threshold': {
                'line': {'color': color, 'width': 3},
                'thickness': 0.8,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif'}
    )
    
    return fig

# ============================================================================
# ESTILOS CSS PERSONALIZADOS
# ============================================================================

CUSTOM_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    body {
        background-color: #f8fafc;
        overflow-x: hidden;
    }
    
    .card {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border: none !important;
        border-radius: 12px !important;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.08) !important;
    }
    
    .btn {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        border: none;
    }
    
    .btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .form-control, .form-select {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        transition: border-color 0.2s ease;
    }
    
    .form-control:focus, .form-select:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .navbar {
        backdrop-filter: blur(10px);
        background-color: rgba(59, 130, 246, 0.95) !important;
    }
    
    .sidebar-button {
        border-radius: 10px;
        transition: all 0.2s ease;
        font-weight: 500;
        border: none;
        background: white;
        color: #475569;
    }
    
    .sidebar-button:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        transform: translateX(4px);
    }
    
    .sidebar-button.active {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
    }
    
    .stat-card {
        border-left: 4px solid;
        border-radius: 12px;
    }
    
    .badge {
        font-weight: 500;
        padding: 6px 12px;
        border-radius: 6px;
    }
    
    /* Animaciones */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.4s ease;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Dropdown mejorado */
    .Select-control {
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* Inputs mejorados */
    input[type="number"]::-webkit-inner-spin-button,
    input[type="number"]::-webkit-outer-spin-button {
        opacity: 1;
    }
</style>
"""

# ============================================================================
# INICIALIZACIÓN DE LA APP
# ============================================================================

app = Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css"
    ],
    suppress_callback_exceptions=True,
    title="Dashboard NNA - Prevención Violencia",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ]
)

server = app.server

# ============================================================================
# LAYOUT - ESTRUCTURA PRINCIPAL
# ============================================================================

def create_navbar():
    """Crear barra de navegación superior"""
    return dbc.Navbar(
        dbc.Container([
            html.Div([
                html.I(className="bi bi-shield-fill me-2", 
                      style={'fontSize': '28px', 'color': 'white'}),
                html.Div([
                    html.Span("Dashboard Prevención Violencia NNA", 
                             style={'fontSize': '18px', 'fontWeight': '600', 
                                   'color': 'white', 'display': 'block'}),
                    html.Small("Sistema de Análisis Predictivo", 
                              style={'fontSize': '11px', 'color': 'rgba(255,255,255,0.8)'})
                ])
            ], style={'display': 'flex', 'alignItems': 'center'}),
            
            html.Div(id='api-status-badge', style={'marginLeft': 'auto'})
        ], fluid=True, style={'display': 'flex', 'alignItems': 'center'}),
        color=COLORS['primary'],
        dark=True,
        sticky='top',
        style={
            'boxShadow': '0 4px 12px rgba(0,0,0,0.1)',
            'padding': '12px 0',
            'zIndex': '1000'
        }
    )

def create_sidebar():
    """Crear menú lateral de navegación"""
    menu_items = [
        {'id': 'prediccion', 'icon': 'bi-graph-up-arrow', 'label': 'Predicción CatBoost'},
        {'id': 'clusters', 'icon': 'bi-diagram-3-fill', 'label': 'Análisis de Clusters'},
        {'id': 'alertas', 'icon': 'bi-exclamation-triangle-fill', 'label': 'Alertas Tempranas'},
        {'id': 'recomendaciones', 'icon': 'bi-lightbulb-fill', 'label': 'Recomendaciones'},
        {'id': 'simulador', 'icon': 'bi-sliders', 'label': 'Simulador de Escenarios'},
        {'id': 'informe', 'icon': 'bi-file-earmark-pdf-fill', 'label': 'Generar Informe'}
    ]
    
    items = []
    for item in menu_items:
        items.append(
            dbc.Button(
                [
                    html.I(className=f"{item['icon']} me-3", 
                          style={'fontSize': '18px'}),
                    html.Span(item['label'])
                ],
                id={'type': 'nav-button', 'index': item['id']},
                className='sidebar-button w-100 text-start mb-2',
                style={'padding': '14px 20px', 'fontSize': '14px'}
            )
        )
    
    return html.Div([
        html.Div([
            html.Div([
                html.I(className="bi bi-grid-3x3-gap-fill me-2", 
                      style={'color': COLORS['primary'], 'fontSize': '20px'}),
                html.H6("Módulos", className="mb-0 d-inline", 
                       style={'color': COLORS['text'], 'fontWeight': '600'})
            ], className="mb-4"),
            html.Div(items)
        ], style={'padding': '24px 16px'})
    ], style={
        'width': '280px',
        'backgroundColor': 'white',
        'borderRight': f'1px solid {COLORS["border"]}',
        'height': 'calc(100vh - 62px)',
        'position': 'fixed',
        'overflowY': 'auto',
        'top': '62px',
        'left': '0',
        'zIndex': '100',
        'boxShadow': '2px 0 8px rgba(0,0,0,0.03)'
    })

def create_content_area():
    """Área principal de contenido dinámico"""
    return html.Div(
        id='main-content',
        className='fade-in',
        style={
            'marginLeft': '280px',
            'marginTop': '62px',
            'padding': '32px',
            'backgroundColor': COLORS['bg'],
            'minHeight': 'calc(100vh - 62px)'
        }
    )

# Layout principal
app.layout = html.Div([
    # Inyectar estilos personalizados
    html.Div(html.Iframe(srcDoc=CUSTOM_STYLE, style={'display': 'none'})),
    
    # Stores
    dcc.Store(id='api-health-store'),
    dcc.Store(id='kmeans-features-store'),
    dcc.Store(id='active-module-store', data='prediccion'),
    dcc.Store(id='prediction-result-store'),
    dcc.Store(id='cluster-result-store'),
    dcc.Interval(id='health-check-interval', interval=30000, n_intervals=0),
    
    create_navbar(),
    create_sidebar(),
    create_content_area()
], style={'backgroundColor': COLORS['bg'], 'minHeight': '100vh'})

# ============================================================================
# MÓDULO: PREDICCIÓN CATBOOST
# ============================================================================

def create_prediction_module():
    """Crear interfaz del módulo de predicción"""
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2([
                        html.I(className="bi bi-graph-up-arrow me-3", 
                              style={'color': COLORS['primary']}),
                        "Predicción de Riesgo"
                    ], style={'fontWeight': '700', 'color': COLORS['text'], 
                             'marginBottom': '8px'}),
                    html.P("Modelo CatBoost para estimación de tasa de violencia sexual en NNA",
                          style={'color': COLORS['text_muted'], 'fontSize': '15px', 
                                'marginBottom': '0'})
                ])
            ])
        ], className="mb-4"),
        
        dbc.Row([
            # Formulario
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        # Sección 1: Demográficos
                        html.Div([
                            html.H6([
                                html.I(className="bi bi-people-fill me-2", 
                                      style={'color': COLORS['primary']}),
                                "Datos Demográficos"
                            ], style={'color': COLORS['text'], 'fontWeight': '600', 
                                     'marginBottom': '20px'}),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Población Menores", html_for="poblacion_menores",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="poblacion_menores", type="number", 
                                             value=12345, step=1,
                                             style={'fontSize': '14px'})
                                ], md=6, className="mb-3"),
                                dbc.Col([
                                    dbc.Label("% Población Urbana", html_for="porc_poblacion_urbana",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="porc_poblacion_urbana", type="number", 
                                             value=78.5, step=0.1, min=0, max=100,
                                             style={'fontSize': '14px'})
                                ], md=6, className="mb-3")
                            ]),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("% Población Rural", html_for="porc_poblacion_rural",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="porc_poblacion_rural", type="number", 
                                             value=21.5, step=0.1, min=0, max=100,
                                             style={'fontSize': '14px'})
                                ], md=6, className="mb-3"),
                                dbc.Col([
                                    dbc.Label("IPM", html_for="ipm",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="ipm", type="number", 
                                             value=0.23, step=0.01, min=0, max=1,
                                             style={'fontSize': '14px'})
                                ], md=6, className="mb-3")
                            ])
                        ]),
                        
                        html.Hr(style={'margin': '24px 0', 'borderColor': COLORS['border']}),
                        
                        # Sección 2: Infraestructura
                        html.Div([
                            html.H6([
                                html.I(className="bi bi-building me-2", 
                                      style={'color': COLORS['info']}),
                                "Cobertura de Servicios (%)"
                            ], style={'color': COLORS['text'], 'fontWeight': '600', 
                                     'marginBottom': '20px'}),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Acueducto", html_for="cobertura_acueducto",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="cobertura_acueducto", type="number", 
                                             value=92, step=0.1, min=0, max=100,
                                             style={'fontSize': '14px'})
                                ], md=4, className="mb-3"),
                                dbc.Col([
                                    dbc.Label("Alcantarillado", html_for="cobertura_alcantarillado",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="cobertura_alcantarillado", type="number", 
                                             value=88, step=0.1, min=0, max=100,
                                             style={'fontSize': '14px'})
                                ], md=4, className="mb-3"),
                                dbc.Col([
                                    dbc.Label("Energía", html_for="cobertura_energia",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="cobertura_energia", type="number", 
                                             value=98, step=0.1, min=0, max=100,
                                             style={'fontSize': '14px'})
                                ], md=4, className="mb-3")
                            ])
                        ]),
                        
                        html.Hr(style={'margin': '24px 0', 'borderColor': COLORS['border']}),
                        
                        # Sección 3: Económicos
                        html.Div([
                            html.H6([
                                html.I(className="bi bi-cash-stack me-2", 
                                      style={'color': COLORS['warning']}),
                                "Indicadores Económicos y Seguridad"
                            ], style={'color': COLORS['text'], 'fontWeight': '600', 
                                     'marginBottom': '20px'}),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("PIB per cápita", html_for="pib_per_capita",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="pib_per_capita", type="number", 
                                             value=17168300, step=1000,
                                             style={'fontSize': '14px'})
                                ], md=6, className="mb-3"),
                                dbc.Col([
                                    dbc.Label("Tasa Homicidio", html_for="tasa_homicidio",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="tasa_homicidio", type="number", 
                                             value=12.3, step=0.1,
                                             style={'fontSize': '14px'})
                                ], md=6, className="mb-3")
                            ])
                        ]),
                        
                        html.Hr(style={'margin': '24px 0', 'borderColor': COLORS['border']}),
                        
                        # Sección 4: Perfil Víctima
                        html.Div([
                            html.H6([
                                html.I(className="bi bi-person-badge me-2", 
                                      style={'color': COLORS['danger']}),
                                "Perfil de Víctima"
                            ], style={'color': COLORS['text'], 'fontWeight': '600', 
                                     'marginBottom': '20px'}),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Sexo", html_for="sexo_victima",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dcc.Dropdown(
                                        id="sexo_victima",
                                        options=[{'label': s, 'value': s} for s in SEXO_OPTIONS],
                                        value='F',
                                        clearable=False,
                                        style={'fontSize': '14px'}
                                    )
                                ], md=4, className="mb-3"),
                                dbc.Col([
                                    dbc.Label("Grupo de Edad", html_for="grupo_edad_victima",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dcc.Dropdown(
                                        id="grupo_edad_victima",
                                        options=[{'label': g, 'value': g} for g in GRUPO_EDAD_OPTIONS],
                                        value='10-14',
                                        clearable=False,
                                        style={'fontSize': '14px'}
                                    )
                                ], md=4, className="mb-3"),
                                dbc.Col([
                                    dbc.Label("Ciclo Vital", html_for="ciclo_vital",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dcc.Dropdown(
                                        id="ciclo_vital",
                                        options=[{'label': c.replace('_', ' ').title(), 'value': c} 
                                                for c in CICLO_VITAL_OPTIONS],
                                        value='adolescencia',
                                        clearable=False,
                                        style={'fontSize': '14px'}
                                    )
                                ], md=4, className="mb-3")
                            ]),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Escolaridad", html_for="escolaridad",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dcc.Dropdown(
                                        id="escolaridad",
                                        options=[{'label': e.replace('_', ' ').title(), 'value': e} 
                                                for e in ESCOLARIDAD_OPTIONS],
                                        value='secundaria_incompleta',
                                        clearable=False,
                                        style={'fontSize': '14px'}
                                    )
                                ], md=6, className="mb-3"),
                                dbc.Col([
                                    dbc.Label("Departamento", html_for="depto_hecho_dane",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dcc.Dropdown(
                                        id="depto_hecho_dane",
                                        options=[{'label': d, 'value': d} for d in DEPARTAMENTOS],
                                        value='Bolívar',
                                        clearable=False,
                                        searchable=True,
                                        style={'fontSize': '14px'}
                                    )
                                ], md=6, className="mb-3")
                            ])
                        ]),
                        
                        # Botón de cálculo
                        dbc.Button(
                            [
                                html.I(className="bi bi-calculator me-2"),
                                "Calcular Predicción"
                            ],
                            id="btn-predict",
                            color="primary",
                            size="lg",
                            className="w-100 mt-4",
                            style={'fontWeight': '600', 'padding': '14px'}
                        ),
                        
                        html.Div(id="prediction-loading", className="text-center mt-3")
                        ], style={'padding': '28px'})
                ], className="shadow-sm", style={'borderRadius': '16px'})
            ], md=5),
            
            # Resultados
            dbc.Col([
                html.Div(id="prediction-results")
            ], md=7)
        ])
    ], fluid=True, style={'maxWidth': '1600px'})



# ============================================================================
# MÓDULO: CLUSTERS Y ANÁLISIS KMEANS
# ============================================================================

def create_clusters_module():
    """Crear interfaz del módulo de clusters con diseño moderno"""
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2([
                        html.I(className="bi bi-diagram-3-fill me-3", 
                              style={'color': COLORS['primary']}),
                        "Análisis de Clusters"
                    ], style={'fontWeight': '700', 'color': COLORS['text'], 
                             'marginBottom': '8px'}),
                    html.P("Modelo KMeans para clasificación de vulnerabilidad municipal",
                          style={'color': COLORS['text_muted'], 'fontSize': '15px', 
                                'marginBottom': '0'})
                ])
            ])
        ], className="mb-4"),
        
        # Alert informativo
        dbc.Alert([
            html.I(className="bi bi-info-circle-fill me-2"),
            html.Span("Ingrese los 6 valores en el orden correcto para asignar el cluster de vulnerabilidad del municipio")
        ], color="info", className="mb-4", 
           style={'borderRadius': '12px', 'border': 'none', 'fontSize': '14px'}),
        
        dbc.Row([
            # Panel de entrada
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        # Header del formulario
                        html.Div([
                            html.H5([
                                html.I(className="bi bi-pencil-square me-2", 
                                      style={'color': COLORS['primary']}),
                                "Ingresar Valores"
                            ], style={'color': COLORS['text'], 'fontWeight': '600', 
                                     'marginBottom': '8px'}),
                            html.Small(id="kmeans-features-info", 
                                      style={'color': COLORS['text_muted'], 'fontSize': '13px'})
                        ], className="mb-4"),
                        
                        # Container dinámico para inputs
                        html.Div(id="kmeans-inputs-container"),
                        
                        # Botón de cálculo
                        dbc.Button(
                            [
                                html.I(className="bi bi-diagram-3-fill me-2"),
                                "Asignar Cluster"
                            ],
                            id="btn-kmeans",
                            color="primary",
                            size="lg",
                            className="w-100 mt-4",
                            style={'fontWeight': '600', 'padding': '14px'}
                        ),
                        
                        html.Div(id="kmeans-loading", className="text-center mt-3")
                    ], style={'padding': '28px'})
                ], className="shadow-sm mb-4", style={'borderRadius': '16px'}),
                
                # Card de resultado
                html.Div(id="kmeans-result-card")
            ], md=4),
            
            # Visualización
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="bi bi-graph-up me-2", 
                                  style={'color': COLORS['info']}),
                            "Visualización de Clusters"
                        ], style={'color': COLORS['text'], 'fontWeight': '600', 
                                 'marginBottom': '20px'}),
                        
                        dcc.Graph(
                            id="cluster-scatter", 
                            config={'displayModeBar': False},
                            style={'height': '500px'}
                        )
                    ], style={'padding': '28px'})
                ], className="shadow-sm", style={'borderRadius': '16px'})
            ], md=8)
        ])
    ], fluid=True, style={'maxWidth': '1600px'})



# ============================================================================
# MÓDULO: ALERTAS TEMPRANAS
# ============================================================================

def create_alertas_module():
    """Crear interfaz del módulo de alertas tempranas con diseño moderno"""
    
    # Datos de ejemplo para demostración
    alertas_data = pd.DataFrame({
        'Municipio': ['Cartagena', 'Barranquilla', 'Santa Marta', 'Magangué', 'Turbaco',
                      'Soledad', 'Malambo', 'Ciénaga', 'Sabanalarga', 'Baranoa'],
        'Departamento': ['Bolívar', 'Atlántico', 'Magdalena', 'Bolívar', 'Bolívar',
                        'Atlántico', 'Atlántico', 'Magdalena', 'Atlántico', 'Atlántico'],
        'Tasa_Proyectada': [45.2, 38.7, 32.1, 51.3, 28.4, 41.8, 35.2, 29.7, 33.5, 27.8],
        'Cluster': [2, 2, 1, 3, 1, 2, 2, 1, 2, 1],
        'Nivel_Alerta': ['Alto', 'Alto', 'Medio', 'Crítico', 'Medio', 
                         'Alto', 'Alto', 'Medio', 'Alto', 'Medio'],
        'Poblacion_Menores': [185430, 234567, 98234, 45678, 23456,
                              156789, 87654, 56789, 34567, 28901]
    })
    
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2([
                        html.I(className="bi bi-exclamation-triangle-fill me-3", 
                              style={'color': COLORS['danger']}),
                        "Alertas Tempranas"
                    ], style={'fontWeight': '700', 'color': COLORS['text'], 
                             'marginBottom': '8px'}),
                    html.P("Identificación de municipios que requieren atención prioritaria",
                          style={'color': COLORS['text_muted'], 'fontSize': '15px', 
                                'marginBottom': '0'})
                ])
            ])
        ], className="mb-4"),
        
        # Tarjetas de resumen estadístico
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-exclamation-octagon-fill", 
                                  style={'fontSize': '32px', 'color': COLORS['danger']}),
                            html.H3("24", className="mb-0 mt-2", 
                                   style={'color': COLORS['danger'], 'fontWeight': '700', 
                                         'fontSize': '36px'}),
                            html.P("Municipios Críticos", className="mb-0 mt-1",
                                  style={'color': COLORS['text_muted'], 'fontSize': '13px', 
                                        'fontWeight': '500'})
                        ], className="text-center")
                    ], style={'padding': '24px'})
                ], className="shadow-sm stat-card", 
                   style={'borderRadius': '16px', 'borderLeftColor': COLORS['danger'], 
                         'borderLeftWidth': '4px'})
            ], md=3, className="mb-3"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-exclamation-triangle-fill", 
                                  style={'fontSize': '32px', 'color': COLORS['warning']}),
                            html.H3("48", className="mb-0 mt-2", 
                                   style={'color': COLORS['warning'], 'fontWeight': '700', 
                                         'fontSize': '36px'}),
                            html.P("Alerta Alta", className="mb-0 mt-1",
                                  style={'color': COLORS['text_muted'], 'fontSize': '13px', 
                                        'fontWeight': '500'})
                        ], className="text-center")
                    ], style={'padding': '24px'})
                ], className="shadow-sm stat-card", 
                   style={'borderRadius': '16px', 'borderLeftColor': COLORS['warning'], 
                         'borderLeftWidth': '4px'})
            ], md=3, className="mb-3"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-exclamation-circle-fill", 
                                  style={'fontSize': '32px', 'color': COLORS['info']}),
                            html.H3("87", className="mb-0 mt-2", 
                                   style={'color': COLORS['info'], 'fontWeight': '700', 
                                         'fontSize': '36px'}),
                            html.P("Alerta Media", className="mb-0 mt-1",
                                  style={'color': COLORS['text_muted'], 'fontSize': '13px', 
                                        'fontWeight': '500'})
                        ], className="text-center")
                    ], style={'padding': '24px'})
                ], className="shadow-sm stat-card", 
                   style={'borderRadius': '16px', 'borderLeftColor': COLORS['info'], 
                         'borderLeftWidth': '4px'})
            ], md=3, className="mb-3"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-check-circle-fill", 
                                  style={'fontSize': '32px', 'color': COLORS['secondary']}),
                            html.H3("163", className="mb-0 mt-2", 
                                   style={'color': COLORS['secondary'], 'fontWeight': '700', 
                                         'fontSize': '36px'}),
                            html.P("Bajo Riesgo", className="mb-0 mt-1",
                                  style={'color': COLORS['text_muted'], 'fontSize': '13px', 
                                        'fontWeight': '500'})
                        ], className="text-center")
                    ], style={'padding': '24px'})
                ], className="shadow-sm stat-card", 
                   style={'borderRadius': '16px', 'borderLeftColor': COLORS['secondary'], 
                         'borderLeftWidth': '4px'})
            ], md=3, className="mb-3")
        ], className="mb-4"),
        
        # Gráfico de barras con top municipios
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="bi bi-bar-chart-fill me-2", 
                                  style={'color': COLORS['danger']}),
                            "Top 10 Municipios con Mayor Riesgo"
                        ], style={'color': COLORS['text'], 'fontWeight': '600', 
                                 'marginBottom': '20px'}),
                        
                        dcc.Graph(
                            id="alertas-bar-chart",
                            config={'displayModeBar': False},
                            figure=create_alertas_bar_chart(alertas_data)
                        )
                    ], style={'padding': '28px'})
                ], className="shadow-sm", style={'borderRadius': '16px'})
            ], md=12, className="mb-4")
        ]),
        
        # Tabla de alertas con filtros
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        # Header con botón de exportar
                        html.Div([
                            html.H5([
                                html.I(className="bi bi-table me-2", 
                                      style={'color': COLORS['primary']}),
                                "Tabla de Alertas Municipales"
                            ], style={'color': COLORS['text'], 'fontWeight': '600', 
                                     'marginBottom': '0', 'flex': '1'}),
                            dbc.Button(
                                [html.I(className="bi bi-download me-2"), "Exportar CSV"],
                                id="btn-export-alertas",
                                color="success",
                                size="sm",
                                outline=True,
                                style={'fontWeight': '500'}
                            )
                        ], style={'display': 'flex', 'alignItems': 'center', 
                                 'marginBottom': '24px'}),
                        
                        # Filtros
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Filtrar por Departamento", 
                                         style={'fontSize': '13px', 'fontWeight': '500', 
                                               'color': COLORS['neutral']}),
                                dcc.Dropdown(
                                    id="filter-departamento",
                                    options=[{'label': 'Todos', 'value': 'all'}] + 
                                           [{'label': d, 'value': d} for d in DEPARTAMENTOS],
                                    value='all',
                                    clearable=False,
                                    style={'fontSize': '14px'}
                                )
                            ], md=4, className="mb-3"),
                            
                            dbc.Col([
                                dbc.Label("Filtrar por Nivel de Alerta", 
                                         style={'fontSize': '13px', 'fontWeight': '500', 
                                               'color': COLORS['neutral']}),
                                dcc.Dropdown(
                                    id="filter-nivel",
                                    options=[
                                        {'label': 'Todos', 'value': 'all'},
                                        {'label': 'Crítico', 'value': 'Crítico'},
                                        {'label': 'Alto', 'value': 'Alto'},
                                        {'label': 'Medio', 'value': 'Medio'},
                                        {'label': 'Bajo', 'value': 'Bajo'}
                                    ],
                                    value='all',
                                    clearable=False,
                                    style={'fontSize': '14px'}
                                )
                            ], md=4, className="mb-3"),
                            
                            dbc.Col([
                                dbc.Label("Ordenar por", 
                                         style={'fontSize': '13px', 'fontWeight': '500', 
                                               'color': COLORS['neutral']}),
                                dcc.Dropdown(
                                    id="sort-column",
                                    options=[
                                        {'label': 'Tasa Proyectada (Mayor a Menor)', 'value': 'tasa_desc'},
                                        {'label': 'Tasa Proyectada (Menor a Mayor)', 'value': 'tasa_asc'},
                                        {'label': 'Municipio (A-Z)', 'value': 'municipio_asc'},
                                        {'label': 'Población Menores', 'value': 'poblacion_desc'}
                                    ],
                                    value='tasa_desc',
                                    clearable=False,
                                    style={'fontSize': '14px'}
                                )
                            ], md=4, className="mb-3")
                        ]),
                        
                        # Tabla
                        html.Div(
                            id="alertas-table-container",
                            children=create_alertas_table(alertas_data),
                            style={'maxHeight': '500px', 'overflowY': 'auto', 
                                  'marginTop': '20px'}
                        )
                    ], style={'padding': '28px'})
                ], className="shadow-sm", style={'borderRadius': '16px'})
            ])
        ])
    ], fluid=True, style={'maxWidth': '1600px'})


def create_alertas_bar_chart(data):
    """Crear gráfico de barras para alertas"""
    # Ordenar por tasa proyectada
    data_sorted = data.nlargest(10, 'Tasa_Proyectada')
    
    # Asignar colores según nivel
    colors_map = {
        'Crítico': COLORS['danger'],
        'Alto': COLORS['warning'],
        'Medio': COLORS['info'],
        'Bajo': COLORS['secondary']
    }
    bar_colors = [colors_map.get(nivel, COLORS['neutral']) for nivel in data_sorted['Nivel_Alerta']]
    
    fig = go.Figure(data=[
        go.Bar(
            x=data_sorted['Tasa_Proyectada'],
            y=data_sorted['Municipio'] + ' - ' + data_sorted['Departamento'],
            orientation='h',
            marker=dict(
                color=bar_colors,
                line=dict(color='white', width=1)
            ),
            text=data_sorted['Tasa_Proyectada'].round(1),
            textposition='auto',
            texttemplate='%{text} /100k',
            hovertemplate='<b>%{y}</b><br>Tasa: %{x:.2f} por 100k hab.<br>Nivel: %{customdata}<extra></extra>',
            customdata=data_sorted['Nivel_Alerta']
        )
    ])
    
    fig.update_layout(
        xaxis_title='Tasa Proyectada por 100,000 habitantes',
        yaxis_title='',
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif', 'color': COLORS['neutral']},
        height=400,
        margin=dict(l=20, r=20, t=20, b=40),
        xaxis=dict(
            gridcolor=COLORS['border'],
            showgrid=True
        ),
        yaxis=dict(
            autorange='reversed'
        )
    )
    
    return fig


def create_alertas_table(data):
    """Crear tabla HTML personalizada para alertas"""
    
    # Mapeo de colores para badges
    badge_colors = {
        'Crítico': ('danger', 'bi-exclamation-octagon-fill'),
        'Alto': ('warning', 'bi-exclamation-triangle-fill'),
        'Medio': ('info', 'bi-exclamation-circle-fill'),
        'Bajo': ('success', 'bi-check-circle-fill')
    }
    
    # Crear filas de la tabla
    rows = []
    for idx, row in data.iterrows():
        badge_color, badge_icon = badge_colors.get(row['Nivel_Alerta'], ('secondary', 'bi-circle'))
        
        rows.append(
            html.Tr([
                html.Td(row['Municipio'], 
                       style={'fontWeight': '500', 'color': COLORS['text'], 
                             'fontSize': '14px'}),
                html.Td(row['Departamento'], 
                       style={'color': COLORS['neutral'], 'fontSize': '14px'}),
                html.Td(f"{row['Tasa_Proyectada']:.1f}", 
                       style={'fontWeight': '600', 'color': COLORS['text'], 
                             'fontSize': '14px'}),
                html.Td(f"Cluster {row['Cluster']}", 
                       style={'color': COLORS['neutral'], 'fontSize': '14px'}),
                html.Td(
                    dbc.Badge([
                        html.I(className=f"{badge_icon} me-1"),
                        row['Nivel_Alerta']
                    ], color=badge_color, pill=True,
                       style={'fontSize': '12px', 'fontWeight': '500', 'padding': '6px 12px'}),
                    style={'textAlign': 'center'}
                ),
                html.Td(f"{row['Poblacion_Menores']:,}", 
                       style={'color': COLORS['neutral'], 'fontSize': '14px'}),
                html.Td(
                    dbc.Button(
                        html.I(className="bi bi-eye"),
                        id={'type': 'view-detail', 'index': idx},
                        color="primary",
                        size="sm",
                        outline=True,
                        style={'padding': '4px 12px'}
                    ),
                    style={'textAlign': 'center'}
                )
            ], style={'borderBottom': f'1px solid {COLORS["border"]}'})
        )
    
    table = html.Table([
        html.Thead(
            html.Tr([
                html.Th("Municipio", style={'fontWeight': '600', 'fontSize': '13px', 
                                           'color': COLORS['text'], 'padding': '12px',
                                           'borderBottom': f'2px solid {COLORS["border"]}'}),
                html.Th("Departamento", style={'fontWeight': '600', 'fontSize': '13px', 
                                               'color': COLORS['text'], 'padding': '12px',
                                               'borderBottom': f'2px solid {COLORS["border"]}'}),
                html.Th("Tasa /100k", style={'fontWeight': '600', 'fontSize': '13px', 
                                             'color': COLORS['text'], 'padding': '12px',
                                             'borderBottom': f'2px solid {COLORS["border"]}'}),
                html.Th("Cluster", style={'fontWeight': '600', 'fontSize': '13px', 
                                         'color': COLORS['text'], 'padding': '12px',
                                         'borderBottom': f'2px solid {COLORS["border"]}'}),
                html.Th("Nivel Alerta", style={'fontWeight': '600', 'fontSize': '13px', 
                                               'color': COLORS['text'], 'padding': '12px',
                                               'textAlign': 'center',
                                               'borderBottom': f'2px solid {COLORS["border"]}'}),
                html.Th("Población <18", style={'fontWeight': '600', 'fontSize': '13px', 
                                                'color': COLORS['text'], 'padding': '12px',
                                                'borderBottom': f'2px solid {COLORS["border"]}'}),
                html.Th("Acciones", style={'fontWeight': '600', 'fontSize': '13px', 
                                          'color': COLORS['text'], 'padding': '12px',
                                          'textAlign': 'center',
                                          'borderBottom': f'2px solid {COLORS["border"]}'})
            ])
        ),
        html.Tbody(rows)
    ], style={'width': '100%', 'borderCollapse': 'collapse'}, className="table-hover")
    
    return table

# ============================================================================
# MÓDULO: SIMULADOR DE ESCENARIOS
# ============================================================================

def create_simulador_module():
    """Crear interfaz del módulo simulador con diseño moderno"""
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2([
                        html.I(className="bi bi-sliders me-3", 
                              style={'color': COLORS['primary']}),
                        "Simulador de Escenarios"
                    ], style={'fontWeight': '700', 'color': COLORS['text'], 
                             'marginBottom': '8px'}),
                    html.P("Evalúe el impacto de cambios en variables clave sobre el riesgo",
                          style={'color': COLORS['text_muted'], 'fontSize': '15px', 
                                'marginBottom': '0'})
                ])
            ])
        ], className="mb-4"),
        
        # Alert informativo
        dbc.Alert([
            html.I(className="bi bi-info-circle-fill me-2"),
            html.Span("Primero ejecute una predicción base en el módulo de Predicción CatBoost. Los valores actuales se tomarán como línea base.")
        ], id="simulador-info", color="info", className="mb-4", 
           style={'borderRadius': '12px', 'border': 'none', 'fontSize': '14px'}),
        
        dbc.Row([
            # Panel de controles
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        # Header del panel
                        html.Div([
                            html.H5([
                                html.I(className="bi bi-sliders me-2", 
                                      style={'color': COLORS['primary']}),
                                "Ajustar Variables"
                            ], style={'color': COLORS['text'], 'fontWeight': '600', 
                                     'marginBottom': '8px'}),
                            html.Small("Modifique los porcentajes para simular cambios", 
                                      style={'color': COLORS['text_muted'], 'fontSize': '13px'})
                        ], className="mb-4"),
                        
                        # Controles de simulación
                        html.Div([
                            # PIB per cápita
                            html.Div([
                                html.Label([
                                    html.I(className="bi bi-cash-coin me-2", 
                                          style={'color': COLORS['warning'], 'fontSize': '18px'}),
                                    html.Span("PIB per cápita", 
                                             style={'fontWeight': '500', 'fontSize': '14px'})
                                ], style={'display': 'flex', 'alignItems': 'center', 
                                         'marginBottom': '8px'}),
                                html.Div([
                                    html.Span(id="sim-pib-value", 
                                             style={'fontSize': '20px', 'fontWeight': '600', 
                                                   'color': COLORS['primary']}),
                                    html.Span("% de cambio", 
                                             style={'fontSize': '13px', 'color': COLORS['text_muted'], 
                                                   'marginLeft': '8px'})
                                ], style={'marginBottom': '12px'}),
                                dcc.Slider(
                                    id="sim-pib",
                                    min=-50,
                                    max=50,
                                    step=5,
                                    value=0,
                                    marks={
                                        -50: {'label': '-50%', 'style': {'fontSize': '11px'}},
                                        -25: {'label': '-25%', 'style': {'fontSize': '11px'}},
                                        0: {'label': '0%', 'style': {'fontSize': '11px', 'fontWeight': '600'}},
                                        25: {'label': '+25%', 'style': {'fontSize': '11px'}},
                                        50: {'label': '+50%', 'style': {'fontSize': '11px'}}
                                    },
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], className="mb-4", style={'padding': '16px', 'backgroundColor': COLORS_ALPHA['warning_10'], 
                                                       'borderRadius': '12px'}),
                            
                            # Tasa de homicidio
                            html.Div([
                                html.Label([
                                    html.I(className="bi bi-exclamation-triangle me-2", 
                                          style={'color': COLORS['danger'], 'fontSize': '18px'}),
                                    html.Span("Tasa de homicidio", 
                                             style={'fontWeight': '500', 'fontSize': '14px'})
                                ], style={'display': 'flex', 'alignItems': 'center', 
                                         'marginBottom': '8px'}),
                                html.Div([
                                    html.Span(id="sim-homicidio-value", 
                                             style={'fontSize': '20px', 'fontWeight': '600', 
                                                   'color': COLORS['primary']}),
                                    html.Span("% de cambio", 
                                             style={'fontSize': '13px', 'color': COLORS['text_muted'], 
                                                   'marginLeft': '8px'})
                                ], style={'marginBottom': '12px'}),
                                dcc.Slider(
                                    id="sim-homicidio",
                                    min=-50,
                                    max=50,
                                    step=5,
                                    value=0,
                                    marks={
                                        -50: {'label': '-50%', 'style': {'fontSize': '11px'}},
                                        -25: {'label': '-25%', 'style': {'fontSize': '11px'}},
                                        0: {'label': '0%', 'style': {'fontSize': '11px', 'fontWeight': '600'}},
                                        25: {'label': '+25%', 'style': {'fontSize': '11px'}},
                                        50: {'label': '+50%', 'style': {'fontSize': '11px'}}
                                    },
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], className="mb-4", style={'padding': '16px', 'backgroundColor': COLORS_ALPHA['danger_10'], 
                                                       'borderRadius': '12px'}),
                            
                            # Cobertura de servicios
                            html.Div([
                                html.Label([
                                    html.I(className="bi bi-building me-2", 
                                          style={'color': COLORS['secondary'], 'fontSize': '18px'}),
                                    html.Span("Cobertura de servicios", 
                                             style={'fontWeight': '500', 'fontSize': '14px'})
                                ], style={'display': 'flex', 'alignItems': 'center', 
                                         'marginBottom': '8px'}),
                                html.Div([
                                    html.Span(id="sim-servicios-value", 
                                             style={'fontSize': '20px', 'fontWeight': '600', 
                                                   'color': COLORS['primary']}),
                                    html.Span("% de cambio", 
                                             style={'fontSize': '13px', 'color': COLORS['text_muted'], 
                                                   'marginLeft': '8px'})
                                ], style={'marginBottom': '12px'}),
                                dcc.Slider(
                                    id="sim-servicios",
                                    min=-20,
                                    max=20,
                                    step=2,
                                    value=0,
                                    marks={
                                        -20: {'label': '-20%', 'style': {'fontSize': '11px'}},
                                        -10: {'label': '-10%', 'style': {'fontSize': '11px'}},
                                        0: {'label': '0%', 'style': {'fontSize': '11px', 'fontWeight': '600'}},
                                        10: {'label': '+10%', 'style': {'fontSize': '11px'}},
                                        20: {'label': '+20%', 'style': {'fontSize': '11px'}}
                                    },
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], className="mb-4", style={'padding': '16px', 'backgroundColor': COLORS_ALPHA['secondary_10'], 
                                                       'borderRadius': '12px'}),
                            
                            # IPM
                            html.Div([
                                html.Label([
                                    html.I(className="bi bi-graph-down me-2", 
                                          style={'color': COLORS['info'], 'fontSize': '18px'}),
                                    html.Span("Índice de Pobreza Multidimensional", 
                                             style={'fontWeight': '500', 'fontSize': '14px'})
                                ], style={'display': 'flex', 'alignItems': 'center', 
                                         'marginBottom': '8px'}),
                                html.Div([
                                    html.Span(id="sim-ipm-value", 
                                             style={'fontSize': '20px', 'fontWeight': '600', 
                                                   'color': COLORS['primary']}),
                                    html.Span("% de cambio", 
                                             style={'fontSize': '13px', 'color': COLORS['text_muted'], 
                                                   'marginLeft': '8px'})
                                ], style={'marginBottom': '12px'}),
                                dcc.Slider(
                                    id="sim-ipm",
                                    min=-30,
                                    max=30,
                                    step=5,
                                    value=0,
                                    marks={
                                        -30: {'label': '-30%', 'style': {'fontSize': '11px'}},
                                        -15: {'label': '-15%', 'style': {'fontSize': '11px'}},
                                        0: {'label': '0%', 'style': {'fontSize': '11px', 'fontWeight': '600'}},
                                        15: {'label': '+15%', 'style': {'fontSize': '11px'}},
                                        30: {'label': '+30%', 'style': {'fontSize': '11px'}}
                                    },
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], className="mb-4", style={'padding': '16px', 'backgroundColor': COLORS_ALPHA['primary_10'], 
                                                       'borderRadius': '12px'})
                        ]),
                        
                        html.Hr(style={'margin': '24px 0', 'borderColor': COLORS['border']}),
                        
                        # Botones de acción
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    [html.I(className="bi bi-arrow-clockwise me-2"), "Restablecer"],
                                    id="btn-reset-simulador",
                                    color="light",
                                    className="w-100",
                                    outline=True,
                                    style={'fontWeight': '500', 'padding': '12px'}
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Button(
                                    [html.I(className="bi bi-play-circle-fill me-2"), "Simular"],
                                    id="btn-simular",
                                    color="primary",
                                    className="w-100",
                                    style={'fontWeight': '600', 'padding': '12px'}
                                )
                            ], md=6)
                        ])
                    ], style={'padding': '28px'})
                ], className="shadow-sm", style={'borderRadius': '16px'})
            ], md=4),
            
            # Panel de resultados
            dbc.Col([
                html.Div(id="simulador-results")
            ], md=8)
        ])
    ], fluid=True, style={'maxWidth': '1600px'})

# ============================================================================
# CALLBACKS (Mismos callbacks anteriores, solo actualizar create_gauge_chart)
# ============================================================================

# ... [TODOS LOS CALLBACKS ANTERIORES SE MANTIENEN IGUALES] ...

# Callback: Verificar salud de la API
@app.callback(
    [Output('api-health-store', 'data'),
     Output('api-status-badge', 'children')],
    Input('health-check-interval', 'n_intervals')
)
def update_api_health(n):
    health = check_api_health()
    
    if health and health.get('estado') == 'API funcionando correctamente':
        badge = dbc.Badge(
            [html.I(className="bi bi-check-circle-fill me-2"), "API Conectada"],
            color="success",
            pill=True,
            className="px-3 py-2",
            style={'fontSize': '13px', 'fontWeight': '500'}
        )
        return health, badge
    else:
        badge = dbc.Badge(
            [html.I(className="bi bi-exclamation-circle-fill me-2"), "API Desconectada"],
            color="danger",
            pill=True,
            className="px-3 py-2",
            style={'fontSize': '13px', 'fontWeight': '500'}
        )
        return None, badge

# [RESTO DE CALLBACKS SE MANTIENEN IGUAL...]
# Callback: Obtener features de KMeans
@app.callback(
    Output('kmeans-features-store', 'data'),
    Input('active-module-store', 'data')
)
def load_kmeans_features(active_module):
    if active_module == 'clusters':
        features = get_kmeans_features()
        return features
    return []

# Callback: Navegación entre módulos
@app.callback(
    [Output('active-module-store', 'data'),
     Output('main-content', 'children')],
    Input({'type': 'nav-button', 'index': ALL}, 'n_clicks'),
    State('active-module-store', 'data'),
    prevent_initial_call=True
)
def navigate_modules(n_clicks, current_module):
    if not any(n_clicks):
        return current_module, create_prediction_module()
    
    ctx = callback_context
    if not ctx.triggered:
        return current_module, create_prediction_module()
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    module = eval(button_id)['index']
    
    module_map = {
        'prediccion': create_prediction_module(),
        'clusters': create_clusters_module(),
        'alertas': create_alertas_module(),
        'recomendaciones': html.Div("Módulo de Recomendaciones - En construcción"),
        'simulador': create_simulador_module(),
        'informe': html.Div("Módulo de Informe - En construcción")
    }
    
    return module, module_map.get(module, create_prediction_module())

# Callback: Predicción CatBoost
@app.callback(
    [Output('prediction-results', 'children'),
     Output('prediction-loading', 'children'),
     Output('prediction-result-store', 'data')],
    Input('btn-predict', 'n_clicks'),
    [State('poblacion_menores', 'value'),
     State('porc_poblacion_urbana', 'value'),
     State('porc_poblacion_rural', 'value'),
     State('ipm', 'value'),
     State('cobertura_acueducto', 'value'),
     State('cobertura_alcantarillado', 'value'),
     State('cobertura_energia', 'value'),
     State('pib_per_capita', 'value'),
     State('tasa_homicidio', 'value'),
     State('sexo_victima', 'value'),
     State('grupo_edad_victima', 'value'),
     State('ciclo_vital', 'value'),
     State('escolaridad', 'value'),
     State('depto_hecho_dane', 'value')],
    prevent_initial_call=True
)
def make_prediction(n_clicks, pob_menores, porc_urb, porc_rur, ipm, cob_acue, 
                   cob_alc, cob_ener, pib, tasa_hom, sexo, grupo_edad, 
                   ciclo, escol, depto):
    if n_clicks is None:
        return None, "", None
    
    loading = dbc.Spinner(color="primary", size="sm")
    
    data = {
        "poblacion_menores": float(pob_menores),
        "porc_poblacion_urbana": float(porc_urb),
        "porc_poblacion_rural": float(porc_rur),
        "ipm": float(ipm),
        "cobertura_acueducto": float(cob_acue),
        "cobertura_alcantarillado": float(cob_alc),
        "cobertura_energia": float(cob_ener),
        "pib_per_capita": float(pib),
        "tasa_homicidio": float(tasa_hom),
        "sexo_victima": sexo,
        "grupo_edad_victima": grupo_edad,
        "ciclo_vital": ciclo,
        "escolaridad": escol,
        "depto_hecho_dane": depto
    }
    
    result = predict_catboost(data)
    
    if result is None:
        error_msg = dbc.Alert(
            [html.I(className="bi bi-exclamation-triangle-fill me-2"),
             "Error al conectar con la API. Verifique la conexión."],
            color="danger",
            dismissable=True,
            className="fade-in"
        )
        return error_msg, "", None
    
    prediccion = result.get('prediccion', 0)
    nivel, color = get_risk_level(prediccion)
    
    gauge = create_gauge_chart(prediccion, "Tasa Proyectada por 100,000 hab.")
    
    results = html.Div([
        dbc.Card([
            dbc.CardBody([
                html.H5([
                    html.I(className="bi bi-check-circle-fill me-2", 
                          style={'color': COLORS['secondary']}),
                    "Resultados de la Predicción"
                ], style={'color': COLORS['text'], 'fontWeight': '600', 
                         'marginBottom': '24px'}),
                
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(figure=gauge, config={'displayModeBar': False})
                    ], md=6),
                    dbc.Col([
                        html.Div([
                            html.H6("Nivel de Riesgo Estimado", 
                                   style={'color': COLORS['text_muted'], 
                                         'fontSize': '14px', 'marginBottom': '12px'}),
                            dbc.Badge(
                                [html.I(className="bi bi-shield-fill me-2"), nivel],
                                color=color.replace('#', ''),
                                style={'fontSize': '20px', 'padding': '12px 24px', 
                                      'fontWeight': '600'}
                            ),
                            
                            html.Hr(style={'margin': '24px 0'}),
                            
                            html.Div([
                                html.H6("Interpretación", 
                                       style={'color': COLORS['text'], 
                                             'fontWeight': '600', 'marginBottom': '12px'}),
                                html.P(
                                    f"La tasa proyectada es de {prediccion:.2f} casos por cada 100,000 habitantes menores de edad.",
                                    style={'fontSize': '14px', 'color': COLORS['neutral'], 
                                          'lineHeight': '1.6'}
                                ),
                                html.P(
                                    f"Este municipio se clasifica en nivel de riesgo {nivel.lower()}.",
                                    style={'fontSize': '14px', 'color': COLORS['neutral'], 
                                          'lineHeight': '1.6', 'marginBottom': '0'}
                                )
                            ])
                        ], style={'marginTop': '16px'})
                    ], md=6)
                ]),
                
                html.Hr(style={'margin': '32px 0', 'borderColor': COLORS['border']}),
                
                html.Div([
                    html.H6([
                        html.I(className="bi bi-bar-chart-fill me-2"),
                        "Variables de Mayor Impacto"
                    ], style={'color': COLORS['text'], 'fontWeight': '600', 
                             'marginBottom': '16px'}),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.I(className="bi bi-exclamation-octagon-fill", 
                                          style={'fontSize': '24px', 'color': COLORS['danger']}),
                                    html.H6("Tasa de Homicidio", className="mt-2 mb-1",
                                           style={'fontSize': '14px', 'fontWeight': '600'}),
                                    dbc.Badge("Impacto Alto", color="danger", 
                                             style={'fontSize': '11px'})
                                ], className="text-center py-3")
                            ], className="stat-card", 
                               style={'borderLeftColor': COLORS['danger']})
                        ], md=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.I(className="bi bi-graph-down", 
                                          style={'fontSize': '24px', 'color': COLORS['warning']}),
                                    html.H6("IPM", className="mt-2 mb-1",
                                           style={'fontSize': '14px', 'fontWeight': '600'}),
                                    dbc.Badge("Impacto Alto", color="warning", 
                                             style={'fontSize': '11px'})
                                ], className="text-center py-3")
                            ], className="stat-card", 
                               style={'borderLeftColor': COLORS['warning']})
                        ], md=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.I(className="bi bi-cash-stack", 
                                          style={'fontSize': '24px', 'color': COLORS['info']}),
                                    html.H6("PIB per cápita", className="mt-2 mb-1",
                                           style={'fontSize': '14px', 'fontWeight': '600'}),
                                    dbc.Badge("Impacto Medio", color="info", 
                                             style={'fontSize': '11px'})
                                ], className="text-center py-3")
                            ], className="stat-card", 
                               style={'borderLeftColor': COLORS['info']})
                        ], md=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.I(className="bi bi-building", 
                                          style={'fontSize': '24px', 'color': COLORS['secondary']}),
                                    html.H6("Cobertura Servicios", className="mt-2 mb-1",
                                           style={'fontSize': '14px', 'fontWeight': '600'}),
                                    dbc.Badge("Impacto Medio", color="success", 
                                             style={'fontSize': '11px'})
                                ], className="text-center py-3")
                            ], className="stat-card", 
                               style={'borderLeftColor': COLORS['secondary']})
                        ], md=3)
                    ])
                ])
            ], style={'padding': '32px'})
        ], className="shadow-sm fade-in", style={'borderRadius': '16px'})
    ])
    
    return results, "", result

# ============================================================================
# CALLBACKS PARA CLUSTERS
# ============================================================================

# Callback: Generar inputs dinámicos para KMeans
@app.callback(
    [Output('kmeans-inputs-container', 'children'),
     Output('kmeans-features-info', 'children')],
    Input('kmeans-features-store', 'data')
)
def create_kmeans_inputs(features):
    if not features:
        return html.Div([
            dbc.Spinner(color="primary", size="sm"),
            html.Span(" Cargando features...", className="ms-2 text-muted")
        ], className="text-center py-4"), ""
    
    # Valores por defecto para demostración
    default_values = [28.07, 64.79, 17168300, 649.0, 15.52, 19.37]
    
    # Iconos para cada feature
    feature_icons = {
        0: "bi bi-speedometer2",
        1: "bi bi-people",
        2: "bi bi-cash-coin",
        3: "bi bi-house",
        4: "bi bi-graph-down",
        5: "bi bi-exclamation-triangle"
    }
    
    inputs = []
    for i, feature in enumerate(features):
        icon = feature_icons.get(i, "bi bi-circle")
        
        inputs.append(
            html.Div([
                dbc.Label([
                    html.I(className=f"{icon} me-2", 
                          style={'color': COLORS['primary'], 'fontSize': '16px'}),
                    html.Span(f"{feature.replace('_', ' ').title()}", 
                             style={'fontWeight': '500'})
                ], style={'fontSize': '13px', 'color': COLORS['neutral'], 
                         'marginBottom': '8px'}),
                dbc.Input(
                    id={'type': 'kmeans-input', 'index': i},
                    type="number",
                    value=default_values[i] if i < len(default_values) else 0,
                    step="any",
                    style={'fontSize': '14px'}
                )
            ], className="mb-3")
        )
    
    info_text = f"✓ {len(features)} valores requeridos"
    
    return html.Div(inputs), info_text


# Callback: Predicción KMeans y visualización
@app.callback(
    [Output('kmeans-result-card', 'children'),
     Output('cluster-scatter', 'figure'),
     Output('kmeans-loading', 'children'),
     Output('cluster-result-store', 'data')],
    Input('btn-kmeans', 'n_clicks'),
    State({'type': 'kmeans-input', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def make_kmeans_prediction(n_clicks, input_values):
    if n_clicks is None:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            xaxis={'visible': False},
            yaxis={'visible': False},
            annotations=[{
                'text': 'Presione "Asignar Cluster" para ver la visualización',
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 14, 'color': COLORS['text_muted']}
            }],
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        return None, empty_fig, "", None
    
    # Validación de inputs
    if not input_values or len(input_values) != 6:
        error = dbc.Alert([
            html.I(className="bi bi-exclamation-triangle-fill me-2"),
            f"Error: Se requieren exactamente 6 valores (recibidos: {len(input_values)})"
        ], color="danger", className="fade-in",
           style={'borderRadius': '12px', 'fontSize': '14px'})
        
        empty_fig = go.Figure()
        empty_fig.update_layout(
            xaxis={'visible': False},
            yaxis={'visible': False},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        return error, empty_fig, "", None
    
    # Mostrar loading
    loading = dbc.Spinner(color="primary", size="sm")
    
    try:
        # Realizar predicción
        valores = [float(v) for v in input_values]
        result = predict_kmeans(valores)
        
        if result is None:
            error = dbc.Alert([
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                "Error al conectar con la API. Verifique la conexión."
            ], color="danger", className="fade-in",
               style={'borderRadius': '12px', 'fontSize': '14px'})
            
            empty_fig = go.Figure()
            empty_fig.update_layout(
                xaxis={'visible': False},
                yaxis={'visible': False},
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=500
            )
            return error, empty_fig, "", None
        
        cluster = result.get('cluster_asignado', 0)
        nivel, color = get_vulnerability_level(cluster)
        
        # Crear tarjeta de resultado
        result_card = dbc.Card([
            dbc.CardBody([
                html.Div([
                    # Icono y cluster
                    html.Div([
                        html.I(className="bi bi-bullseye", 
                              style={'fontSize': '48px', 'color': color, 
                                    'marginBottom': '16px'})
                    ], className="text-center"),
                    
                    # Número de cluster
                    html.H2(f"Cluster {cluster}", 
                           style={'color': color, 'fontWeight': '700', 
                                 'textAlign': 'center', 'marginBottom': '12px'}),
                    
                    # Badge de vulnerabilidad
                    html.Div([
                        dbc.Badge([
                            html.I(className="bi bi-shield-fill-exclamation me-2"),
                            f"Vulnerabilidad: {nivel}"
                        ], color=color.replace('#', ''),
                           style={'fontSize': '16px', 'padding': '10px 20px', 
                                 'fontWeight': '600'})
                    ], className="text-center mb-3"),
                    
                    html.Hr(style={'margin': '20px 0', 'borderColor': COLORS['border']}),
                    
                    # Descripción
                    html.Div([
                        html.H6("Interpretación", 
                               style={'color': COLORS['text'], 'fontWeight': '600', 
                                     'marginBottom': '12px', 'fontSize': '14px'}),
                        html.P(f"Este perfil ha sido clasificado en el cluster {cluster}.",
                              style={'fontSize': '13px', 'color': COLORS['neutral'], 
                                    'lineHeight': '1.6', 'marginBottom': '8px'}),
                        html.P(f"Nivel de vulnerabilidad: {nivel}",
                              style={'fontSize': '13px', 'color': COLORS['neutral'], 
                                    'lineHeight': '1.6', 'marginBottom': '0'})
                    ]),
                    
                    html.Hr(style={'margin': '20px 0', 'borderColor': COLORS['border']}),
                    
                    # Características del cluster
                    html.Div([
                        html.H6("Características", 
                               style={'color': COLORS['text'], 'fontWeight': '600', 
                                     'marginBottom': '12px', 'fontSize': '14px'}),
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.I(className="bi bi-check-circle-fill me-2", 
                                      style={'color': COLORS['secondary']}),
                                "Perfil sociodemográfico evaluado"
                            ], style={'fontSize': '13px', 'border': 'none', 
                                     'padding': '8px 0', 'backgroundColor': 'transparent'}),
                            dbc.ListGroupItem([
                                html.I(className="bi bi-check-circle-fill me-2", 
                                      style={'color': COLORS['secondary']}),
                                "Variables económicas analizadas"
                            ], style={'fontSize': '13px', 'border': 'none', 
                                     'padding': '8px 0', 'backgroundColor': 'transparent'}),
                            dbc.ListGroupItem([
                                html.I(className="bi bi-check-circle-fill me-2", 
                                      style={'color': COLORS['secondary']}),
                                "Indicadores de riesgo calculados"
                            ], style={'fontSize': '13px', 'border': 'none', 
                                     'padding': '8px 0', 'backgroundColor': 'transparent'})
                        ], flush=True)
                    ])
                ])
            ], style={'padding': '28px'})
        ], className="shadow-sm fade-in", style={'borderRadius': '16px'})
        
        # Crear scatter plot mejorado
        scatter_data = pd.DataFrame({
            'x': [valores[0], 15, 25, 35, 45],
            'y': [valores[1], 50, 60, 70, 80],
            'cluster': [cluster, 0, 1, 2, 3],
            'label': ['Tu municipio', 'Cluster 0', 'Cluster 1', 'Cluster 2', 'Cluster 3'],
            'size': [20, 10, 10, 10, 10]
        })
        
        # Colores para cada cluster
        cluster_colors = {
            0: COLORS['secondary'],
            1: COLORS['info'],
            2: COLORS['warning'],
            3: COLORS['danger']
        }
        
        fig = go.Figure()
        
        # Agregar puntos por cluster
        for clust in scatter_data['cluster'].unique():
            cluster_df = scatter_data[scatter_data['cluster'] == clust]
            is_user = cluster_df['label'].str.contains('Tu municipio').any()
            
            fig.add_trace(go.Scatter(
                x=cluster_df['x'],
                y=cluster_df['y'],
                mode='markers',
                name=f'Cluster {clust}',
                marker=dict(
                    size=cluster_df['size'] * 2 if is_user else cluster_df['size'],
                    color=cluster_colors.get(clust, COLORS['neutral']),
                    line=dict(width=2, color='white') if is_user else dict(width=0),
                    symbol='star' if is_user else 'circle'
                ),
                text=cluster_df['label'],
                hovertemplate='<b>%{text}</b><br>PC1: %{x:.2f}<br>PC2: %{y:.2f}<extra></extra>'
            ))
        
        fig.update_layout(
            title={
                'text': 'Análisis de Componentes Principales (PCA)',
                'font': {'size': 16, 'color': COLORS['text'], 'family': 'Inter, sans-serif'},
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title='Componente Principal 1',
            yaxis_title='Componente Principal 2',
            plot_bgcolor='rgba(248, 250, 252, 0.5)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif', 'color': COLORS['neutral']},
            height=500,
            hovermode='closest',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor=COLORS['border'],
                borderwidth=1
            ),
            xaxis=dict(
                gridcolor=COLORS['border'],
                showgrid=True,
                zeroline=True,
                zerolinecolor=COLORS['border']
            ),
            yaxis=dict(
                gridcolor=COLORS['border'],
                showgrid=True,
                zeroline=True,
                zerolinecolor=COLORS['border']
            )
        )
        
        return result_card, fig, "", result
        
    except ValueError as e:
        error = dbc.Alert([
            html.I(className="bi bi-exclamation-triangle-fill me-2"),
            f"Error en los valores ingresados: {str(e)}"
        ], color="danger", className="fade-in",
           style={'borderRadius': '12px', 'fontSize': '14px'})
        
        empty_fig = go.Figure()
        empty_fig.update_layout(
            xaxis={'visible': False},
            yaxis={'visible': False},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        return error, empty_fig, "", None
    

# ============================================================================
# CALLBACKS PARA ALERTAS
# ============================================================================

# Callback: Filtrar y ordenar tabla de alertas
@app.callback(
    Output('alertas-table-container', 'children'),
    [Input('filter-departamento', 'value'),
     Input('filter-nivel', 'value'),
     Input('sort-column', 'value')]
)
def update_alertas_table(depto_filter, nivel_filter, sort_option):
    # Datos de ejemplo (en producción, estos vendrían de la API)
    alertas_data = pd.DataFrame({
        'Municipio': ['Cartagena', 'Barranquilla', 'Santa Marta', 'Magangué', 'Turbaco',
                      'Soledad', 'Malambo', 'Ciénaga', 'Sabanalarga', 'Baranoa'],
        'Departamento': ['Bolívar', 'Atlántico', 'Magdalena', 'Bolívar', 'Bolívar',
                        'Atlántico', 'Atlántico', 'Magdalena', 'Atlántico', 'Atlántico'],
        'Tasa_Proyectada': [45.2, 38.7, 32.1, 51.3, 28.4, 41.8, 35.2, 29.7, 33.5, 27.8],
        'Cluster': [2, 2, 1, 3, 1, 2, 2, 1, 2, 1],
        'Nivel_Alerta': ['Alto', 'Alto', 'Medio', 'Crítico', 'Medio', 
                         'Alto', 'Alto', 'Medio', 'Alto', 'Medio'],
        'Poblacion_Menores': [185430, 234567, 98234, 45678, 23456,
                              156789, 87654, 56789, 34567, 28901]
    })
    
    # Aplicar filtros
    filtered_data = alertas_data.copy()
    
    if depto_filter != 'all':
        filtered_data = filtered_data[filtered_data['Departamento'] == depto_filter]
    
    if nivel_filter != 'all':
        filtered_data = filtered_data[filtered_data['Nivel_Alerta'] == nivel_filter]
    
    # Aplicar ordenamiento
    if sort_option == 'tasa_desc':
        filtered_data = filtered_data.sort_values('Tasa_Proyectada', ascending=False)
    elif sort_option == 'tasa_asc':
        filtered_data = filtered_data.sort_values('Tasa_Proyectada', ascending=True)
    elif sort_option == 'municipio_asc':
        filtered_data = filtered_data.sort_values('Municipio', ascending=True)
    elif sort_option == 'poblacion_desc':
        filtered_data = filtered_data.sort_values('Poblacion_Menores', ascending=False)
    
    # Mensaje si no hay resultados
    if filtered_data.empty:
        return dbc.Alert([
            html.I(className="bi bi-info-circle me-2"),
            "No se encontraron municipios con los filtros seleccionados"
        ], color="info", style={'borderRadius': '12px', 'fontSize': '14px'})
    
    return create_alertas_table(filtered_data)


# Callback: Exportar datos (simulado)
@app.callback(
    Output('btn-export-alertas', 'children'),
    Input('btn-export-alertas', 'n_clicks'),
    prevent_initial_call=True
)
def export_alertas(n_clicks):
    if n_clicks:
        # En producción, aquí se generaría y descargaría el CSV real
        return [
            html.I(className="bi bi-check-circle me-2"),
            "¡Exportado!"
        ]
    return [html.I(className="bi bi-download me-2"), "Exportar CSV"]


# Callback: Ver detalle de municipio (modal)
@app.callback(
    Output('modal-detalle-alerta', 'is_open'),
    Output('modal-detalle-alerta-content', 'children'),
    Input({'type': 'view-detail', 'index': ALL}, 'n_clicks'),
    State('modal-detalle-alerta', 'is_open'),
    prevent_initial_call=True
)
def toggle_modal_detalle(n_clicks, is_open):
    if any(n_clicks):
        ctx = callback_context
        if ctx.triggered:
            button_id = eval(ctx.triggered[0]['prop_id'].split('.')[0])
            idx = button_id['index']
            
            # Datos de ejemplo del municipio
            content = dbc.ModalBody([
                html.H5("Detalles del Municipio", className="mb-3"),
                html.P(f"Información detallada del municipio con índice {idx}"),
                # Aquí se agregarían más detalles en producción
            ])
            
            return not is_open, content
    
    return is_open, html.Div()


# Agregar modal al layout principal (debe incluirse en create_alertas_module)
def get_modal_detalle():
    """Modal para mostrar detalles de alertas"""
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle("Detalle de Alerta"),
                close_button=True
            ),
            html.Div(id='modal-detalle-alerta-content')
        ],
        id='modal-detalle-alerta',
        size='lg',
        is_open=False
    )


# ============================================================================
# CALLBACKS PARA SIMULADOR
# ============================================================================

# Callback: Actualizar valores mostrados en los sliders
@app.callback(
    [Output('sim-pib-value', 'children'),
     Output('sim-homicidio-value', 'children'),
     Output('sim-servicios-value', 'children'),
     Output('sim-ipm-value', 'children')],
    [Input('sim-pib', 'value'),
     Input('sim-homicidio', 'value'),
     Input('sim-servicios', 'value'),
     Input('sim-ipm', 'value')]
)
def update_slider_values(pib, homicidio, servicios, ipm):
    return (
        f"{pib:+d}" if pib != 0 else "0",
        f"{homicidio:+d}" if homicidio != 0 else "0",
        f"{servicios:+d}" if servicios != 0 else "0",
        f"{ipm:+d}" if ipm != 0 else "0"
    )


# Callback: Restablecer sliders
@app.callback(
    [Output('sim-pib', 'value'),
     Output('sim-homicidio', 'value'),
     Output('sim-servicios', 'value'),
     Output('sim-ipm', 'value')],
    Input('btn-reset-simulador', 'n_clicks'),
    prevent_initial_call=True
)
def reset_simulador(n_clicks):
    return 0, 0, 0, 0


# Callback: Ejecutar simulación
@app.callback(
    Output('simulador-results', 'children'),
    Input('btn-simular', 'n_clicks'),
    [State('sim-pib', 'value'),
     State('sim-homicidio', 'value'),
     State('sim-servicios', 'value'),
     State('sim-ipm', 'value'),
     State('prediction-result-store', 'data')],
    prevent_initial_call=True
)
def run_simulation(n_clicks, pib_change, hom_change, serv_change, ipm_change, base_prediction):
    if base_prediction is None:
        return dbc.Alert([
            html.I(className="bi bi-exclamation-triangle-fill me-2"),
            "Primero debe ejecutar una predicción base en el módulo de Predicción CatBoost"
        ], color="warning", className="fade-in",
           style={'borderRadius': '12px', 'fontSize': '14px'})
    
    # Obtener predicción base
    prediccion_base = base_prediction.get('prediccion', 0)
    
    # Calcular impactos (estos son estimaciones simplificadas)
    # En producción, estos coeficientes deberían venir del modelo o ser configurables
    impacto_pib = (pib_change / 100) * -0.15  # PIB más alto reduce riesgo
    impacto_homicidio = (hom_change / 100) * 0.35  # Homicidio más alto aumenta riesgo
    impacto_servicios = (serv_change / 100) * -0.10  # Más servicios reduce riesgo
    impacto_ipm = (ipm_change / 100) * 0.25  # IPM más alto aumenta riesgo
    
    impacto_total = impacto_pib + impacto_homicidio + impacto_servicios + impacto_ipm
    prediccion_simulada = prediccion_base * (1 + impacto_total)
    diferencia = prediccion_simulada - prediccion_base
    porcentaje_cambio = (diferencia / prediccion_base) * 100
    
    # Determinar niveles de riesgo
    nivel_base, color_base = get_risk_level(prediccion_base)
    nivel_simulado, color_simulado = get_risk_level(prediccion_simulada)
    cambio_nivel = nivel_base != nivel_simulado
    
    # Crear visualización de comparación
    fig_comparacion = go.Figure()
    
    # Barra de predicción base
    fig_comparacion.add_trace(go.Bar(
        name='Escenario Base',
        x=['Tasa Proyectada'],
        y=[prediccion_base],
        marker_color=color_base,
        text=[f'{prediccion_base:.1f}'],
        textposition='auto',
        hovertemplate='<b>Base</b><br>Tasa: %{y:.2f}<extra></extra>'
    ))
    
    # Barra de predicción simulada
    fig_comparacion.add_trace(go.Bar(
        name='Escenario Simulado',
        x=['Tasa Proyectada'],
        y=[prediccion_simulada],
        marker_color=color_simulado,
        text=[f'{prediccion_simulada:.1f}'],
        textposition='auto',
        hovertemplate='<b>Simulado</b><br>Tasa: %{y:.2f}<extra></extra>'
    ))
    
    fig_comparacion.update_layout(
        title={
            'text': 'Comparación de Escenarios',
            'font': {'size': 16, 'color': COLORS['text'], 'family': 'Inter, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        yaxis_title='Tasa por 100,000 habitantes',
        barmode='group',
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif', 'color': COLORS['neutral']},
        height=350,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(showticklabels=False),
        yaxis=dict(gridcolor=COLORS['border'], showgrid=True)
    )
    
    # Crear gráfico de impactos por variable
    variables = ['PIB', 'Homicidio', 'Servicios', 'IPM']
    impactos = [
        impacto_pib * prediccion_base,
        impacto_homicidio * prediccion_base,
        impacto_servicios * prediccion_base,
        impacto_ipm * prediccion_base
    ]
    colores_impacto = [
        COLORS['secondary'] if imp < 0 else COLORS['danger'] for imp in impactos
    ]
    
    fig_impactos = go.Figure(go.Bar(
        x=variables,
        y=impactos,
        marker_color=colores_impacto,
        text=[f'{imp:+.2f}' for imp in impactos],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Impacto: %{y:+.2f}<extra></extra>'
    ))
    
    fig_impactos.update_layout(
        title={
            'text': 'Impacto por Variable',
            'font': {'size': 16, 'color': COLORS['text'], 'family': 'Inter, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        yaxis_title='Cambio en Tasa',
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif', 'color': COLORS['neutral']},
        height=350,
        xaxis=dict(gridcolor=COLORS['border']),
        yaxis=dict(gridcolor=COLORS['border'], showgrid=True, zeroline=True, zerolinecolor=COLORS['border'])
    )
    
    # Construir resultado
    results = html.Div([
        # Tarjeta de resumen
        dbc.Card([
            dbc.CardBody([
                html.H5([
                    html.I(className="bi bi-calculator-fill me-2", 
                          style={'color': COLORS['primary']}),
                    "Resultados de la Simulación"
                ], style={'color': COLORS['text'], 'fontWeight': '600', 
                         'marginBottom': '24px'}),
                
                # Métricas principales
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Small("Escenario Base", 
                                              style={'color': COLORS['text_muted'], 
                                                    'fontSize': '12px', 'fontWeight': '500'}),
                                    html.H3(f"{prediccion_base:.1f}", 
                                           style={'color': color_base, 'fontWeight': '700', 
                                                 'marginTop': '8px', 'marginBottom': '4px'}),
                                    dbc.Badge(nivel_base, color=color_base.replace('#', ''),
                                             style={'fontSize': '11px'})
                                ], className="text-center")
                            ], style={'padding': '20px'})
                        ], className="stat-card h-100", 
                           style={'borderLeftColor': color_base, 'borderLeftWidth': '4px'})
                    ], md=4),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Small("Cambio Proyectado", 
                                              style={'color': COLORS['text_muted'], 
                                                    'fontSize': '12px', 'fontWeight': '500'}),
                                    html.H3(f"{diferencia:+.1f}", 
                                           style={'color': COLORS['danger'] if diferencia > 0 else COLORS['secondary'], 
                                                 'fontWeight': '700', 'marginTop': '8px', 'marginBottom': '4px'}),
                                    html.Span(f"({porcentaje_cambio:+.1f}%)", 
                                             style={'fontSize': '14px', 'color': COLORS['neutral']})
                                ], className="text-center")
                            ], style={'padding': '20px'})
                        ], className="stat-card h-100", 
                           style={'borderLeftColor': COLORS['info'], 'borderLeftWidth': '4px'})
                    ], md=4),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Small("Escenario Simulado", 
                                              style={'color': COLORS['text_muted'], 
                                                    'fontSize': '12px', 'fontWeight': '500'}),
                                    html.H3(f"{prediccion_simulada:.1f}", 
                                           style={'color': color_simulado, 'fontWeight': '700', 
                                                 'marginTop': '8px', 'marginBottom': '4px'}),
                                    dbc.Badge(nivel_simulado, color=color_simulado.replace('#', ''),
                                             style={'fontSize': '11px'})
                                ], className="text-center")
                            ], style={'padding': '20px'})
                        ], className="stat-card h-100", 
                           style={'borderLeftColor': color_simulado, 'borderLeftWidth': '4px'})
                    ], md=4)
                ], className="mb-4"),
                
                # Alerta de cambio de nivel
                dbc.Alert([
                    html.I(className="bi bi-exclamation-triangle-fill me-2"),
                    f"¡Atención! El nivel de riesgo cambiaría de {nivel_base} a {nivel_simulado}"
                ], color="warning", className="mb-0") if cambio_nivel else html.Div(),
                
            ], style={'padding': '28px'})
        ], className="shadow-sm fade-in mb-4", style={'borderRadius': '16px'}),
        
        # Gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_comparacion, config={'displayModeBar': False})
                    ], style={'padding': '20px'})
                ], className="shadow-sm", style={'borderRadius': '16px'})
            ], md=6, className="mb-4"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_impactos, config={'displayModeBar': False})
                    ], style={'padding': '20px'})
                ], className="shadow-sm", style={'borderRadius': '16px'})
            ], md=6, className="mb-4")
        ]),
        
        # Interpretación detallada
        dbc.Card([
            dbc.CardBody([
                html.H5([
                    html.I(className="bi bi-lightbulb-fill me-2", 
                          style={'color': COLORS['warning']}),
                    "Interpretación de Resultados"
                ], style={'color': COLORS['text'], 'fontWeight': '600', 
                         'marginBottom': '20px'}),
                
                html.Div([
                    html.P([
                        html.Strong("Escenario Base: "),
                        f"Con las condiciones actuales, la tasa proyectada es de {prediccion_base:.2f} casos por 100,000 habitantes."
                    ], style={'fontSize': '14px', 'color': COLORS['neutral'], 'lineHeight': '1.6'}),
                    
                    html.P([
                        html.Strong("Cambios Simulados: "),
                        f"Al aplicar los cambios propuestos, la tasa {'aumentaría' if diferencia > 0 else 'disminuiría'} ",
                        f"en {abs(diferencia):.2f} casos ({abs(porcentaje_cambio):.1f}%), ",
                        f"llegando a {prediccion_simulada:.2f} casos por 100,000 habitantes."
                    ], style={'fontSize': '14px', 'color': COLORS['neutral'], 'lineHeight': '1.6'}),
                    
                    html.P([
                        html.Strong("Variables más Influyentes: "),
                        f"Los cambios en {'tasa de homicidio' if abs(impacto_homicidio) == max(abs(impacto_pib), abs(impacto_homicidio), abs(impacto_servicios), abs(impacto_ipm)) else 'IPM' if abs(impacto_ipm) == max(abs(impacto_pib), abs(impacto_homicidio), abs(impacto_servicios), abs(impacto_ipm)) else 'PIB per cápita' if abs(impacto_pib) == max(abs(impacto_pib), abs(impacto_homicidio), abs(impacto_servicios), abs(impacto_ipm)) else 'cobertura de servicios'} ",
                        "tienen el mayor impacto en este escenario."
                    ], style={'fontSize': '14px', 'color': COLORS['neutral'], 'lineHeight': '1.6', 'marginBottom': '0'})
                ])
            ], style={'padding': '28px'})
        ], className="shadow-sm fade-in", style={'borderRadius': '16px'})
    ])
    
    return results

# ============================================================================
# EJECUTAR LA APLICACIÓN
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8050)
