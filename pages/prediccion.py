from dash import html, dcc
import dash_bootstrap_components as dbc
from config import COLORS, SEXO_OPTIONS, GRUPO_EDAD_OPTIONS, CICLO_VITAL_OPTIONS, ESCOLARIDAD_OPTIONS, DEPARTAMENTOS

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