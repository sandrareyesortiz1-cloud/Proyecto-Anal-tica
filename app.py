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
        'clusters': html.Div("Módulo de Clusters - En construcción"),
        'alertas': html.Div("Módulo de Alertas - En construcción"),
        'recomendaciones': html.Div("Módulo de Recomendaciones - En construcción"),
        'simulador': html.Div("Módulo de Simulador - En construcción"),
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
# EJECUTAR LA APLICACIÓN
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8050)