import os
import requests
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

COLORS = {
    'primary': '#4f46e5',
    'secondary': '#06b6d4',
    'success': '#10b981',
    'danger': '#ef4444',
    'warning': '#f59e0b',
    'bg_gradient_start': '#4f46e5',
    'bg_gradient_end': '#7c3aed',
    'card': '#ffffff',
    'text_dark': '#1f2937',
    'text_muted': '#6b7280',
    'border': '#e5e7eb'
}

UMBRALES_RIESGO = {'bajo': 15, 'medio': 30, 'alto': float('inf')}

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

def predict_catboost(data):
    try:
        response = requests.post(f"{API_URL}/predict/catboost", json=data, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_risk_level(prediccion):
    if prediccion < UMBRALES_RIESGO['bajo']:
        return 'Bajo', COLORS['success'], '🟢'
    elif prediccion < UMBRALES_RIESGO['medio']:
        return 'Medio', COLORS['warning'], '🟡'
    else:
        return 'Alto', COLORS['danger'], '🔴'

def create_gauge_chart(value, title):
    nivel, color, _ = get_risk_level(value)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 22, 'color': COLORS['text_dark'], 'family': 'Inter'}},
        number={'suffix': " /100k", 'font': {'size': 48, 'family': 'Inter', 'color': color}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': COLORS['border']},
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 15], 'color': 'rgba(16, 185, 129, 0.15)'},
                {'range': [15, 30], 'color': 'rgba(245, 158, 11, 0.15)'},
                {'range': [30, 100], 'color': 'rgba(239, 68, 68, 0.15)'}
            ],
            'threshold': {
                'line': {'color': color, 'width': 6},
                'thickness': 0.85,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=30, r=30, t=80, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, -apple-system, sans-serif'}
    )
    
    return fig

def create_bar_chart(prediccion):
    nivel, color, _ = get_risk_level(prediccion)
    
    fig = go.Figure(go.Bar(
        x=[prediccion],
        y=['Tasa Proyectada'],
        orientation='h',
        marker=dict(
            color=color,
            line=dict(color=color, width=2)
        ),
        text=[f"{prediccion:.2f}"],
        textposition='outside',
        textfont=dict(size=18, family='Inter', color=color)
    ))
    
    fig.add_shape(
        type="line", x0=15, x1=15, y0=-0.5, y1=0.5,
        line=dict(color=COLORS['success'], width=2, dash="dash")
    )
    fig.add_shape(
        type="line", x0=30, x1=30, y0=-0.5, y1=0.5,
        line=dict(color=COLORS['danger'], width=2, dash="dash")
    )
    
    fig.update_layout(
        title='Comparación con Umbrales de Riesgo',
        xaxis_title='Casos por 100,000 habitantes',
        height=200,
        margin=dict(l=150, r=50, t=50, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter'},
        showlegend=False,
        xaxis=dict(range=[0, max(100, prediccion * 1.2)])
    )
    
    return fig

# ============================================================================
# INICIALIZACIÓN
# ============================================================================

app = Dash(__name__, 
           external_stylesheets=[
               dbc.themes.BOOTSTRAP,
               'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
               'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css'
           ],
           suppress_callback_exceptions=True,
           title="Predicción Violencia NNA")

server = app.server

# ============================================================================
# LAYOUT
# ============================================================================

app.layout = html.Div([
    # Header con gradiente
    html.Div([
        dbc.Container([
            html.Div([
                html.Div([
                    html.I(className="bi bi-shield-shaded", 
                          style={'fontSize': '42px', 'marginRight': '20px', 'color': 'white'}),
                    html.Div([
                        html.H1("Predicción de Violencia Sexual NNA", 
                               style={'margin': '0', 'fontSize': '32px', 'fontWeight': '700', 'color': 'white'}),
                        html.P("Sistema de análisis predictivo basado en Machine Learning",
                              style={'margin': '5px 0 0 0', 'fontSize': '16px', 'color': 'rgba(255,255,255,0.9)'})
                    ])
                ], style={'display': 'flex', 'alignItems': 'center'}),
                
                html.Div([
                    html.Div([
                        html.I(className="bi bi-calendar3", style={'marginRight': '8px'}),
                        datetime.now().strftime("%d/%m/%Y")
                    ], style={'fontSize': '14px', 'color': 'rgba(255,255,255,0.9)'})
                ])
            ], style={
                'display': 'flex', 
                'justifyContent': 'space-between', 
                'alignItems': 'center',
                'padding': '32px 0'
            })
        ], fluid=True)
    ], style={
        'background': f'linear-gradient(135deg, {COLORS["bg_gradient_start"]} 0%, {COLORS["bg_gradient_end"]} 100%)',
        'boxShadow': '0 4px 20px rgba(0,0,0,0.1)'
    }),
    
    # Contenido principal
    dbc.Container([
        dbc.Row([
            # Panel de entrada (izquierda)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-pencil-square", 
                                  style={'fontSize': '24px', 'color': COLORS['primary'], 'marginRight': '12px'}),
                            html.H4("Datos del Municipio", 
                                   style={'margin': '0', 'color': COLORS['text_dark'], 'fontWeight': '600'})
                        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '24px'}),
                        
                        # Demografía
                        html.Div([
                            html.H6("📊 Demografía", 
                                   style={'color': COLORS['primary'], 'fontWeight': '600', 'marginBottom': '16px'}),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Población menor de edad", className="fw-500"),
                                    dbc.Input(id="poblacion_menores", type="number", value=12345, 
                                             className="form-control-lg")
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("% Población urbana", className="fw-500"),
                                    dbc.Input(id="porc_poblacion_urbana", type="number", value=78.5, 
                                             step=0.1, min=0, max=100, className="form-control-lg")
                                ], md=6)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("% Población rural", className="fw-500"),
                                    dbc.Input(id="porc_poblacion_rural", type="number", value=21.5,
                                             step=0.1, min=0, max=100, className="form-control-lg")
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("IPM (0-1)", className="fw-500"),
                                    dbc.Input(id="ipm", type="number", value=0.23, 
                                             step=0.01, min=0, max=1, className="form-control-lg")
                                ], md=6)
                            ])
                        ], style={'marginBottom': '28px'}),
                        
                        html.Hr(style={'borderColor': COLORS['border'], 'margin': '28px 0'}),
                        
                        # Servicios
                        html.Div([
                            html.H6("🏘️ Cobertura Servicios (%)", 
                                   style={'color': COLORS['primary'], 'fontWeight': '600', 'marginBottom': '16px'}),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Acueducto", className="fw-500"),
                                    dbc.Input(id="cobertura_acueducto", type="number", value=92,
                                             step=0.1, min=0, max=100, className="form-control-lg")
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Alcantarillado", className="fw-500"),
                                    dbc.Input(id="cobertura_alcantarillado", type="number", value=88,
                                             step=0.1, min=0, max=100, className="form-control-lg")
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Energía", className="fw-500"),
                                    dbc.Input(id="cobertura_energia", type="number", value=98,
                                             step=0.1, min=0, max=100, className="form-control-lg")
                                ], md=4)
                            ])
                        ], style={'marginBottom': '28px'}),
                        
                        html.Hr(style={'borderColor': COLORS['border'], 'margin': '28px 0'}),
                        
                        # Económico
                        html.Div([
                            html.H6("💰 Indicadores Económicos y Seguridad", 
                                   style={'color': COLORS['primary'], 'fontWeight': '600', 'marginBottom': '16px'}),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("PIB per cápita (COP)", className="fw-500"),
                                    dbc.Input(id="pib_per_capita", type="number", value=17168300,
                                             step=10000, className="form-control-lg")
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Tasa homicidio", className="fw-500"),
                                    dbc.Input(id="tasa_homicidio", type="number", value=12.3,
                                             step=0.1, className="form-control-lg")
                                ], md=6)
                            ])
                        ], style={'marginBottom': '28px'}),
                        
                        html.Hr(style={'borderColor': COLORS['border'], 'margin': '28px 0'}),
                        
                        # Perfil víctima
                        html.Div([
                            html.H6("👤 Perfil de Víctima", 
                                   style={'color': COLORS['primary'], 'fontWeight': '600', 'marginBottom': '16px'}),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Sexo", className="fw-500"),
                                    dcc.Dropdown(
                                        id="sexo_victima",
                                        options=[{'label': s, 'value': s} for s in SEXO_OPTIONS],
                                        value='F',
                                        clearable=False,
                                        style={'fontSize': '16px'}
                                    )
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Grupo edad", className="fw-500"),
                                    dcc.Dropdown(
                                        id="grupo_edad_victima",
                                        options=[{'label': g, 'value': g} for g in GRUPO_EDAD_OPTIONS],
                                        value='10-14',
                                        clearable=False,
                                        style={'fontSize': '16px'}
                                    )
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Ciclo vital", className="fw-500"),
                                    dcc.Dropdown(
                                        id="ciclo_vital",
                                        options=[{'label': c.replace('_', ' ').title(), 'value': c} 
                                                for c in CICLO_VITAL_OPTIONS],
                                        value='adolescencia',
                                        clearable=False,
                                        style={'fontSize': '16px'}
                                    )
                                ], md=4)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Escolaridad", className="fw-500"),
                                    dcc.Dropdown(
                                        id="escolaridad",
                                        options=[{'label': e.replace('_', ' ').title(), 'value': e} 
                                                for e in ESCOLARIDAD_OPTIONS],
                                        value='secundaria_incompleta',
                                        clearable=False,
                                        style={'fontSize': '16px'}
                                    )
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Departamento", className="fw-500"),
                                    dcc.Dropdown(
                                        id="depto_hecho_dane",
                                        options=[{'label': d, 'value': d} for d in DEPARTAMENTOS],
                                        value='Bolívar',
                                        clearable=False,
                                        searchable=True,
                                        style={'fontSize': '16px'}
                                    )
                                ], md=6)
                            ])
                        ]),
                        
                        html.Div([
                            dbc.Button(
                                [html.I(className="bi bi-graph-up-arrow me-2"), 
                                 "CALCULAR PREDICCIÓN"],
                                id="btn-predict",
                                size="lg",
                                className="w-100",
                                style={
                                    'background': f'linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["bg_gradient_end"]} 100%)',
                                    'border': 'none',
                                    'borderRadius': '12px',
                                    'padding': '16px',
                                    'fontSize': '18px',
                                    'fontWeight': '600',
                                    'boxShadow': '0 4px 12px rgba(79, 70, 229, 0.3)',
                                    'transition': 'all 0.3s ease'
                                }
                            ),
                            html.Div(id="prediction-loading", className="text-center mt-3")
                        ], style={'marginTop': '32px'})
                    ])
                ], className="shadow-lg", style={
                    'borderRadius': '16px',
                    'border': 'none',
                    'height': '100%'
                })
            ], lg=5),
            
            # Panel de resultados (derecha)
            dbc.Col([
                html.Div(id="prediction-results", children=[
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="bi bi-lightbulb", 
                                      style={'fontSize': '64px', 'color': COLORS['border'], 'marginBottom': '24px'}),
                                html.H4("Esperando predicción...", 
                                       style={'color': COLORS['text_muted'], 'fontWeight': '500'}),
                                html.P("Complete el formulario y presione 'Calcular Predicción'",
                                      style={'color': COLORS['text_muted'], 'marginTop': '12px'})
                            ], style={'textAlign': 'center', 'padding': '60px 20px'})
                        ])
                    ], className="shadow-lg", style={
                        'borderRadius': '16px',
                        'border': 'none',
                        'height': '100%',
                        'minHeight': '600px'
                    })
                ])
            ], lg=7)
        ], className="g-4")
    ], fluid=True, style={'padding': '32px', 'backgroundColor': '#f9fafb'})
], style={'fontFamily': 'Inter, -apple-system, sans-serif', 'backgroundColor': '#f9fafb'})

# ============================================================================
# CALLBACK
# ============================================================================

@app.callback(
    [Output('prediction-results', 'children'),
     Output('prediction-loading', 'children')],
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
        return None, ""
    
    loading = dbc.Spinner(color="primary", size="lg")
    
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
        error = dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="bi bi-exclamation-triangle-fill", 
                          style={'fontSize': '48px', 'color': COLORS['danger'], 'marginBottom': '16px'}),
                    html.H4("Error de conexión", style={'color': COLORS['danger']}),
                    html.P("No se pudo conectar con la API. Verifique que el servidor esté ejecutándose.",
                          style={'color': COLORS['text_muted']})
                ], style={'textAlign': 'center', 'padding': '40px'})
            ])
        ], className="shadow-lg", style={'borderRadius': '16px', 'border': f'2px solid {COLORS["danger"]}'})
        return error, ""
    
    prediccion = result.get('prediccion', 0)
    nivel, color, emoji = get_risk_level(prediccion)
    
    gauge = create_gauge_chart(prediccion, "Tasa Proyectada")
    bar = create_bar_chart(prediccion)
    
    results = dbc.Card([
        dbc.CardBody([
            # Header de resultado
            html.Div([
                html.Div([
                    html.Span(emoji, style={'fontSize': '48px', 'marginRight': '16px'}),
                    html.Div([
                        html.H3("Resultado de Predicción", 
                               style={'margin': '0', 'color': COLORS['text_dark'], 'fontWeight': '600'}),
                        html.P(f"Análisis para {depto}", 
                              style={'margin': '4px 0 0 0', 'color': COLORS['text_muted']})
                    ])
                ], style={'display': 'flex', 'alignItems': 'center'}),
                
                html.Div([
                    dbc.Badge(f"Riesgo {nivel}", 
                             style={
                                 'backgroundColor': color,
                                 'fontSize': '18px',
                                 'padding': '10px 20px',
                                 'borderRadius': '8px'
                             })
                ])
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'marginBottom': '32px',
                'paddingBottom': '24px',
                'borderBottom': f'2px solid {COLORS["border"]}'
            }),
            
            # Gráfico gauge
            dcc.Graph(figure=gauge, config={'displayModeBar': False}, 
                     style={'marginBottom': '24px'}),
            
            # Gráfico barra
            dcc.Graph(figure=bar, config={'displayModeBar': False},
                     style={'marginBottom': '32px'}),
            
            # Interpretación
            html.Div([
                html.H5("📋 Interpretación del Resultado", 
                       style={'color': COLORS['primary'], 'fontWeight': '600', 'marginBottom': '16px'}),
                html.Div([
                    html.P([
                        html.Strong("Tasa proyectada: "),
                        f"{prediccion:.2f} casos por cada 100,000 habitantes"
                    ], style={'fontSize': '16px', 'marginBottom': '12px'}),
                    html.P([
                        html.Strong("Nivel de riesgo: "),
                        html.Span(nivel, style={'color': color, 'fontWeight': '600'})
                    ], style={'fontSize': '16px', 'marginBottom': '12px'}),
                    html.P([
                        html.Strong("Recomendación: "),
                        "Este municipio requiere atención inmediata y programas de prevención." 
                        if nivel == "Alto" else 
                        "Se sugiere monitoreo continuo y fortalecimiento de programas preventivos."
                        if nivel == "Medio" else
                        "Mantener las estrategias actuales de prevención."
                    ], style={'fontSize': '16px'})
                ], style={
                    'backgroundColor': 'rgba(79, 70, 229, 0.05)',
                    'padding': '20px',
                    'borderRadius': '12px',
                    'border': f'1px solid {COLORS["border"]}'
                })
            ], style={'marginBottom': '32px'}),
            
            # Variables de impacto
            html.Div([
                html.H5("🎯 Variables de Mayor Impacto", 
                       style={'color': COLORS['primary'], 'fontWeight': '600', 'marginBottom': '16px'}),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.I(className="bi bi-bar-chart-fill", 
                                  style={'fontSize': '24px', 'color': COLORS['danger'], 'marginBottom': '8px'}),
                            html.Div("Tasa de homicidio", 
                                    style={'fontSize': '14px', 'fontWeight': '600', 'color': COLORS['text_dark']}),
                            html.Small("Impacto Alto", style={'color': COLORS['danger']})
                        ], style={
                            'textAlign': 'center',
                            'padding': '20px',
                            'backgroundColor': 'rgba(239, 68, 68, 0.05)',
                            'borderRadius': '12px',
                            'border': f'1px solid rgba(239, 68, 68, 0.2)'
                        })
                    ], md=3)
                ], className="g-3")
            ])
        ])
    ], className="shadow-lg", style={
        'borderRadius': '16px',
        'border': 'none',
        'height': '100%'
    })
    
    return results, ""

# ============================================================================
# EJECUTAR LA APLICACIÓN
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8050),
dbc.Col([
    html.Div([
        html.I(className="bi bi-graph-up",
               style={'fontSize': '24px', 'color': COLORS['warning'], 'marginBottom': '8px'}),
        html.Div("IPM",
                 style={'fontSize': '14px', 'fontWeight': '600', 'color': COLORS['text_dark']}),
        html.Small("Impacto Alto", style={'color': COLORS['warning']})
    ], style={
        'textAlign': 'center',
        'padding': '20px',
        'backgroundColor': 'rgba(245, 158, 11, 0.05)',
        'borderRadius': '12px',
        'border': '1px solid rgba(245, 158, 11, 0.2)'
    })
], md=3),

dbc.Col([
    html.Div([
        html.I(className="bi bi-currency-dollar",
               style={'fontSize': '24px', 'color': COLORS['secondary'], 'marginBottom': '8px'}),
        html.Div("PIB per cápita",
                 style={'fontSize': '14px', 'fontWeight': '600', 'color': COLORS['text_dark']}),
        html.Small("Impacto Medio", style={'color': COLORS['secondary']})
    ], style={
        'textAlign': 'center',
        'padding': '20px',
        'backgroundColor': 'rgba(6, 182, 212, 0.05)',
        'borderRadius': '12px',
        'border': '1px solid rgba(6, 182, 212, 0.2)'
    })
], md=3),

dbc.Col([
    html.Div([
        html.I(className="bi bi-houses",
               style={'fontSize': '24px', 'color': COLORS['success'], 'marginBottom': '8px'}),
        html.Div("Servicios básicos",
                 style={'fontSize': '14px', 'fontWeight': '600', 'color': COLORS['text_dark']}),
        html.Small("Impacto Medio", style={'color': COLORS['success']})
    ], style={
        'textAlign': 'center',
        'padding': '20px',
        'backgroundColor': 'rgba(16, 185, 129, 0.05)',
        'borderRadius': '12px',
        'border': '1px solid rgba(16, 185, 129, 0.2)'
    })
], md=3)
