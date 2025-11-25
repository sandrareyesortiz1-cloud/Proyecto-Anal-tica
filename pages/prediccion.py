from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from config import COLORS, SEXO_OPTIONS, GRUPO_EDAD_OPTIONS, CICLO_VITAL_OPTIONS, ESCOLARIDAD_OPTIONS, DEPARTAMENTOS

def create_prediction_module():
    """Crear interfaz del módulo de predicción con validaciones"""
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
                                    dbc.Label([
                                        "Población Menores ",
                                        html.Span("*", style={'color': COLORS['danger']})
                                    ], html_for="poblacion_menores",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="poblacion_menores", type="number", 
                                             placeholder="Ej: 12345",
                                             min=0, step=1,
                                             style={'fontSize': '14px'}),
                                    dbc.FormFeedback(id="feedback-poblacion_menores", type="invalid")
                                ], md=6, className="mb-3"),
                                dbc.Col([
                                    dbc.Label([
                                        "% Población Urbana ",
                                        html.Span("*", style={'color': COLORS['danger']})
                                    ], html_for="porc_poblacion_urbana",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="porc_poblacion_urbana", type="number", 
                                             placeholder="Ej: 78.5",
                                             min=0, max=100, step=0.1,
                                             style={'fontSize': '14px'}),
                                    dbc.FormFeedback(id="feedback-porc_poblacion_urbana", type="invalid")
                                ], md=6, className="mb-3")
                            ]),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label([
                                        "% Población Rural ",
                                        html.Span("*", style={'color': COLORS['danger']})
                                    ], html_for="porc_poblacion_rural",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="porc_poblacion_rural", type="number", 
                                             placeholder="Calculado automáticamente",
                                             disabled=True,
                                             style={'fontSize': '14px', 'backgroundColor': '#f8f9fa'}),
                                    dbc.FormText("Se calcula automáticamente (100 - % urbana)")
                                ], md=6, className="mb-3"),
                                dbc.Col([
                                    dbc.Label([
                                        "IPM (Índice Pobreza Multidimensional) ",
                                        html.Span("*", style={'color': COLORS['danger']})
                                    ], html_for="ipm",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="ipm", type="number", 
                                             placeholder="Ej: 0.23",
                                             min=0, max=1, step=0.01,
                                             style={'fontSize': '14px'}),
                                    dbc.FormFeedback(id="feedback-ipm", type="invalid"),
                                    dbc.FormText("Valor entre 0 y 1")
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
                                    dbc.Label([
                                        "Acueducto ",
                                        html.Span("*", style={'color': COLORS['danger']})
                                    ], html_for="cobertura_acueducto",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="cobertura_acueducto", type="number", 
                                             placeholder="Ej: 92",
                                             min=0, max=100, step=0.1,
                                             style={'fontSize': '14px'}),
                                    dbc.FormFeedback(id="feedback-cobertura_acueducto", type="invalid")
                                ], md=4, className="mb-3"),
                                dbc.Col([
                                    dbc.Label([
                                        "Alcantarillado ",
                                        html.Span("*", style={'color': COLORS['danger']})
                                    ], html_for="cobertura_alcantarillado",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="cobertura_alcantarillado", type="number", 
                                             placeholder="Ej: 88",
                                             min=0, max=100, step=0.1,
                                             style={'fontSize': '14px'}),
                                    dbc.FormFeedback(id="feedback-cobertura_alcantarillado", type="invalid")
                                ], md=4, className="mb-3"),
                                dbc.Col([
                                    dbc.Label([
                                        "Energía ",
                                        html.Span("*", style={'color': COLORS['danger']})
                                    ], html_for="cobertura_energia",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="cobertura_energia", type="number", 
                                             placeholder="Ej: 98",
                                             min=0, max=100, step=0.1,
                                             style={'fontSize': '14px'}),
                                    dbc.FormFeedback(id="feedback-cobertura_energia", type="invalid")
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
                                    dbc.Label([
                                        "PIB per cápita (COP) ",
                                        html.Span("*", style={'color': COLORS['danger']})
                                    ], html_for="pib_per_capita",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="pib_per_capita", type="number", 
                                             placeholder="Ej: 17168300",
                                             min=0, step=1000,
                                             style={'fontSize': '14px'}),
                                    dbc.FormFeedback(id="feedback-pib_per_capita", type="invalid"),
                                    dbc.FormText("Valor en pesos colombianos")
                                ], md=6, className="mb-3"),
                                dbc.Col([
                                    dbc.Label([
                                        "Tasa Homicidio (por 100k hab) ",
                                        html.Span("*", style={'color': COLORS['danger']})
                                    ], html_for="tasa_homicidio",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dbc.Input(id="tasa_homicidio", type="number", 
                                             placeholder="Ej: 12.3",
                                             min=0, step=0.1,
                                             style={'fontSize': '14px'}),
                                    dbc.FormFeedback(id="feedback-tasa_homicidio", type="invalid")
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
                                    dbc.Label([
                                        "Sexo ",
                                        html.Span("*", style={'color': COLORS['danger']})
                                    ], html_for="sexo_victima",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dcc.Dropdown(
                                        id="sexo_victima",
                                        options=[{'label': s, 'value': s} for s in SEXO_OPTIONS],
                                        placeholder="Seleccione...",
                                        clearable=False,
                                        style={'fontSize': '14px'}
                                    )
                                ], md=4, className="mb-3"),
                                dbc.Col([
                                    dbc.Label([
                                        "Grupo de Edad ",
                                        html.Span("*", style={'color': COLORS['danger']})
                                    ], html_for="grupo_edad_victima",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dcc.Dropdown(
                                        id="grupo_edad_victima",
                                        options=[{'label': g, 'value': g} for g in GRUPO_EDAD_OPTIONS],
                                        placeholder="Seleccione...",
                                        clearable=False,
                                        style={'fontSize': '14px'}
                                    )
                                ], md=4, className="mb-3"),
                                dbc.Col([
                                    dbc.Label([
                                        "Ciclo Vital ",
                                        html.Span("*", style={'color': COLORS['danger']})
                                    ], html_for="ciclo_vital",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dcc.Dropdown(
                                        id="ciclo_vital",
                                        options=[{'label': c.replace('_', ' ').title(), 'value': c} 
                                                for c in CICLO_VITAL_OPTIONS],
                                        placeholder="Seleccione...",
                                        clearable=False,
                                        style={'fontSize': '14px'}
                                    )
                                ], md=4, className="mb-3")
                            ]),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label([
                                        "Escolaridad ",
                                        html.Span("*", style={'color': COLORS['danger']})
                                    ], html_for="escolaridad",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dcc.Dropdown(
                                        id="escolaridad",
                                        options=[{'label': e.replace('_', ' ').title(), 'value': e} 
                                                for e in ESCOLARIDAD_OPTIONS],
                                        placeholder="Seleccione...",
                                        clearable=False,
                                        style={'fontSize': '14px'}
                                    )
                                ], md=6, className="mb-3"),
                                dbc.Col([
                                    dbc.Label([
                                        "Departamento ",
                                        html.Span("*", style={'color': COLORS['danger']})
                                    ], html_for="depto_hecho_dane",
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral']}),
                                    dcc.Dropdown(
                                        id="depto_hecho_dane",
                                        options=[{'label': d, 'value': d} for d in DEPARTAMENTOS],
                                        placeholder="Seleccione...",
                                        clearable=False,
                                        searchable=True,
                                        style={'fontSize': '14px'}
                                    )
                                ], md=6, className="mb-3")
                            ])
                        ]),
                        
                        # Alerta de validación general
                        html.Div(id="validation-alert", className="mt-3"),
                        
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


def register_validation_callbacks(app):
    """Registrar callbacks para validaciones del formulario"""
    
    # Callback para calcular automáticamente población rural
    @app.callback(
        Output("porc_poblacion_rural", "value"),
        Input("porc_poblacion_urbana", "value"),
        prevent_initial_call=True
    )
    def calcular_poblacion_rural(urbana):
        if urbana is not None and 0 <= urbana <= 100:
            return round(100 - urbana, 1)
        return None
    
    # Callback para validar todos los campos al hacer clic en predecir
    @app.callback(
        [
            Output("poblacion_menores", "invalid"),
            Output("feedback-poblacion_menores", "children"),
            Output("porc_poblacion_urbana", "invalid"),
            Output("feedback-porc_poblacion_urbana", "children"),
            Output("ipm", "invalid"),
            Output("feedback-ipm", "children"),
            Output("cobertura_acueducto", "invalid"),
            Output("feedback-cobertura_acueducto", "children"),
            Output("cobertura_alcantarillado", "invalid"),
            Output("feedback-cobertura_alcantarillado", "children"),
            Output("cobertura_energia", "invalid"),
            Output("feedback-cobertura_energia", "children"),
            Output("pib_per_capita", "invalid"),
            Output("feedback-pib_per_capita", "children"),
            Output("tasa_homicidio", "invalid"),
            Output("feedback-tasa_homicidio", "children"),
            Output("validation-alert", "children"),
        ],
        Input("btn-predict", "n_clicks"),
        [
            State("poblacion_menores", "value"),
            State("porc_poblacion_urbana", "value"),
            State("ipm", "value"),
            State("cobertura_acueducto", "value"),
            State("cobertura_alcantarillado", "value"),
            State("cobertura_energia", "value"),
            State("pib_per_capita", "value"),
            State("tasa_homicidio", "value"),
            State("sexo_victima", "value"),
            State("grupo_edad_victima", "value"),
            State("ciclo_vital", "value"),
            State("escolaridad", "value"),
            State("depto_hecho_dane", "value"),
        ],
        prevent_initial_call=True
    )
    def validar_formulario(n_clicks, pob_menores, porc_urb, ipm, cob_acue, 
                          cob_alcan, cob_ener, pib, tasa_hom,
                          sexo, grupo_edad, ciclo, escolaridad, depto):
        
        errores = []
        validaciones = []
        
        # Validar población menores
        if pob_menores is None or pob_menores == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("Población menores")
        elif pob_menores < 0:
            validaciones.extend([True, "No puede ser negativo"])
            errores.append("Población menores")
        elif pob_menores > 10000000:
            validaciones.extend([True, "Valor poco realista (máx: 10 millones)"])
            errores.append("Población menores")
        else:
            validaciones.extend([False, ""])
        
        # Validar % población urbana
        if porc_urb is None or porc_urb == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("% Población urbana")
        elif porc_urb < 0:
            validaciones.extend([True, "No puede ser negativo"])
            errores.append("% Población urbana")
        elif porc_urb > 100:
            validaciones.extend([True, "No puede ser mayor a 100%"])
            errores.append("% Población urbana")
        else:
            validaciones.extend([False, ""])
        
        # Validar IPM
        if ipm is None or ipm == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("IPM")
        elif ipm < 0:
            validaciones.extend([True, "No puede ser negativo"])
            errores.append("IPM")
        elif ipm > 1:
            validaciones.extend([True, "Debe estar entre 0 y 1"])
            errores.append("IPM")
        else:
            validaciones.extend([False, ""])
        
        # Validar cobertura acueducto
        if cob_acue is None or cob_acue == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("Cobertura acueducto")
        elif cob_acue < 0 or cob_acue > 100:
            validaciones.extend([True, "Debe estar entre 0 y 100%"])
            errores.append("Cobertura acueducto")
        else:
            validaciones.extend([False, ""])
        
        # Validar cobertura alcantarillado
        if cob_alcan is None or cob_alcan == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("Cobertura alcantarillado")
        elif cob_alcan < 0 or cob_alcan > 100:
            validaciones.extend([True, "Debe estar entre 0 y 100%"])
            errores.append("Cobertura alcantarillado")
        else:
            validaciones.extend([False, ""])
        
        # Validar cobertura energía
        if cob_ener is None or cob_ener == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("Cobertura energía")
        elif cob_ener < 0 or cob_ener > 100:
            validaciones.extend([True, "Debe estar entre 0 y 100%"])
            errores.append("Cobertura energía")
        else:
            validaciones.extend([False, ""])
        
        # Validar PIB per cápita
        if pib is None or pib == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("PIB per cápita")
        elif pib < 0:
            validaciones.extend([True, "No puede ser negativo"])
            errores.append("PIB per cápita")
        elif pib > 1000000000:
            validaciones.extend([True, "Valor poco realista (máx: 1,000 millones)"])
            errores.append("PIB per cápita")
        else:
            validaciones.extend([False, ""])
        
        # Validar tasa homicidio
        if tasa_hom is None or tasa_hom == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("Tasa homicidio")
        elif tasa_hom < 0:
            validaciones.extend([True, "No puede ser negativo"])
            errores.append("Tasa homicidio")
        elif tasa_hom > 500:
            validaciones.extend([True, "Valor poco realista (máx: 500 por 100k)"])
            errores.append("Tasa homicidio")
        else:
            validaciones.extend([False, ""])
        
        # Validar campos categóricos
        if not sexo:
            errores.append("Sexo")
        if not grupo_edad:
            errores.append("Grupo de edad")
        if not ciclo:
            errores.append("Ciclo vital")
        if not escolaridad:
            errores.append("Escolaridad")
        if not depto:
            errores.append("Departamento")
        
        # Crear alerta general si hay errores
        if errores:
            alert = dbc.Alert([
                html.H6([
                    html.I(className="bi bi-exclamation-triangle-fill me-2"),
                    "Por favor corrija los siguientes campos:"
                ], className="alert-heading mb-2"),
                html.Ul([html.Li(error) for error in errores], className="mb-0")
            ], color="danger", className="mt-3")
            validaciones.append(alert)
        else:
            validaciones.append(None)
        
        return validaciones
