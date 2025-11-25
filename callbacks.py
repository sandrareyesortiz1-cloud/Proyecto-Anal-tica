from dash import Input, Output, State, callback_context, ALL, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from config import COLORS, DEPARTAMENTOS
from utils import (
    check_api_health, predict_catboost, get_risk_level, create_gauge_chart, 
    get_kmeans_features, predict_kmeans, get_vulnerability_level
)
from pages.prediccion import create_prediction_module
from pages.clusters import create_clusters_module
from pages.alertas import create_alertas_module, create_alertas_table
from pages.simulador import create_simulador_module
from pages.informe import create_informe_module
from pages.recomendaciones import create_recomendaciones_module

def register_callbacks(app):
    from dash import Input, Output, State, callback_context, html
import dash

# ... tus otros imports ...

def register_callbacks(app):
    """
    Registra todos los callbacks de la aplicación
    """
    
    # Callback para toggle del sidebar en mobile
    @app.callback(
        [
            Output('sidebar', 'className'),
            Output('sidebar-overlay', 'className')
        ],
        [
            Input('sidebar-toggle-btn', 'n_clicks'),
            Input('sidebar-close-btn', 'n_clicks'),
            Input('sidebar-overlay', 'n_clicks'),
            Input({'type': 'nav-button', 'index': dash.dependencies.ALL}, 'n_clicks')
        ],
        [
            State('sidebar', 'className')
        ],
        prevent_initial_call=True
    )
    def toggle_sidebar(toggle_clicks, close_clicks, overlay_clicks, nav_clicks, current_class):
        """
        Controla apertura/cierre del sidebar en mobile
        """
        ctx = callback_context
        
        if not ctx.triggered:
            return dash.no_update, dash.no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Si se clickeó un botón de navegación, cerrar sidebar en mobile
        if 'nav-button' in trigger_id:
            return '', ''  # Cerrar sidebar
        
        # Toggle del sidebar
        if trigger_id in ['sidebar-toggle-btn', 'sidebar-close-btn', 'sidebar-overlay']:
            if current_class and 'open' in current_class:
                return '', ''  # Cerrar
            else:
                return 'open', 'show'  # Abrir
        
        return dash.no_update, dash.no_update
    
    
    # ========================================================================
    # HEALTH CHECK
    # ========================================================================
    @app.callback(
        [Output('api-health-store', 'data'), Output('api-status-badge', 'children')],
        Input('health-check-interval', 'n_intervals')
    )
    def update_api_health(n):
        """Verificar estado de conexión con la API"""
        health = check_api_health()
        if health and health.get('estado') == 'API funcionando correctamente':
            badge = dbc.Badge(
                [html.I(className="bi bi-check-circle-fill me-2"), "API Conectada"], 
                color="success", pill=True, className="px-3 py-2", 
                style={'fontSize': '13px', 'fontWeight': '500'}
            )
            return health, badge
        
        badge = dbc.Badge(
            [html.I(className="bi bi-exclamation-circle-fill me-2"), "API Desconectada"], 
            color="danger", pill=True, className="px-3 py-2", 
            style={'fontSize': '13px', 'fontWeight': '500'}
        )
        return None, badge
    # ========================================================================
    # VALIDACIONES FORMULARIO DE PREDICCIÓN
    # ========================================================================
    
    # Callback para calcular automáticamente población rural
    @app.callback(
        Output("porc_poblacion_rural", "value"),
        Input("porc_poblacion_urbana", "value"),
        prevent_initial_call=True
    )
    def calcular_poblacion_rural(urbana):
        """Calcular automáticamente población rural basada en urbana"""
        if urbana is not None and 0 <= urbana <= 100:
            return round(100 - urbana, 1)
        return None
    
    # Callback para validar todos los campos antes de predecir
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
        """Validar todos los campos del formulario antes de realizar predicción"""
        
        errores = []
        validaciones = []
        
        # Validar población menores
        if pob_menores is None or pob_menores == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("Población menores")
        elif pob_menores < 0:
            validaciones.extend([True, "No puede ser negativo"])
            errores.append("Población menores (valor negativo)")
        elif pob_menores > 10000000:
            validaciones.extend([True, "Valor poco realista (máx: 10 millones)"])
            errores.append("Población menores (valor muy alto)")
        else:
            validaciones.extend([False, ""])
        
        # Validar % población urbana
        if porc_urb is None or porc_urb == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("% Población urbana")
        elif porc_urb < 0:
            validaciones.extend([True, "No puede ser negativo"])
            errores.append("% Población urbana (valor negativo)")
        elif porc_urb > 100:
            validaciones.extend([True, "No puede ser mayor a 100%"])
            errores.append("% Población urbana (mayor a 100%)")
        else:
            validaciones.extend([False, ""])
        
        # Validar IPM
        if ipm is None or ipm == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("IPM")
        elif ipm < 0:
            validaciones.extend([True, "No puede ser negativo"])
            errores.append("IPM (valor negativo)")
        elif ipm > 1:
            validaciones.extend([True, "Debe estar entre 0 y 1"])
            errores.append("IPM (debe estar entre 0 y 1)")
        else:
            validaciones.extend([False, ""])
        
        # Validar cobertura acueducto
        if cob_acue is None or cob_acue == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("Cobertura acueducto")
        elif cob_acue < 0 or cob_acue > 100:
            validaciones.extend([True, "Debe estar entre 0 y 100%"])
            errores.append("Cobertura acueducto (fuera de rango)")
        else:
            validaciones.extend([False, ""])
        
        # Validar cobertura alcantarillado
        if cob_alcan is None or cob_alcan == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("Cobertura alcantarillado")
        elif cob_alcan < 0 or cob_alcan > 100:
            validaciones.extend([True, "Debe estar entre 0 y 100%"])
            errores.append("Cobertura alcantarillado (fuera de rango)")
        else:
            validaciones.extend([False, ""])
        
        # Validar cobertura energía
        if cob_ener is None or cob_ener == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("Cobertura energía")
        elif cob_ener < 0 or cob_ener > 100:
            validaciones.extend([True, "Debe estar entre 0 y 100%"])
            errores.append("Cobertura energía (fuera de rango)")
        else:
            validaciones.extend([False, ""])
        
        # Validar PIB per cápita
        if pib is None or pib == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("PIB per cápita")
        elif pib < 0:
            validaciones.extend([True, "No puede ser negativo"])
            errores.append("PIB per cápita (valor negativo)")
        elif pib > 1000000000:
            validaciones.extend([True, "Valor poco realista (máx: 1,000 millones)"])
            errores.append("PIB per cápita (valor muy alto)")
        else:
            validaciones.extend([False, ""])
        
        # Validar tasa homicidio
        if tasa_hom is None or tasa_hom == "":
            validaciones.extend([True, "Este campo es requerido"])
            errores.append("Tasa homicidio")
        elif tasa_hom < 0:
            validaciones.extend([True, "No puede ser negativo"])
            errores.append("Tasa homicidio (valor negativo)")
        elif tasa_hom > 500:
            validaciones.extend([True, "Valor poco realista (máx: 500 por 100k)"])
            errores.append("Tasa homicidio (valor muy alto)")
        else:
            validaciones.extend([False, ""])
        
        # Validar campos categóricos
        if not sexo:
            errores.append("Sexo de la víctima")
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
                ], className="alert-heading mb-2", style={'fontSize': '14px'}),
                html.Ul([html.Li(error, style={'fontSize': '13px'}) for error in errores], 
                       className="mb-0")
            ], color="danger", className="mt-3", style={'borderRadius': '12px'})
            validaciones.append(alert)
        else:
            validaciones.append(None)
        
        return validaciones

    # ========================================================================
    # NAVEGACIÓN ENTRE MÓDULOS
    # ========================================================================
    @app.callback(
        [Output('active-module-store', 'data'), Output('main-content', 'children')],
        Input({'type': 'nav-button', 'index': ALL}, 'n_clicks'),
        State('active-module-store', 'data'),
        prevent_initial_call=True
    )
    def navigate_modules(n_clicks, current_module):
        """Manejar navegación entre módulos del dashboard"""
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
            'recomendaciones': create_recomendaciones_module(),
            'simulador': create_simulador_module(),
            'informe': create_informe_module()
        }
        
        return module, module_map.get(module, create_prediction_module())

    # ========================================================================
    # PREDICCIÓN CATBOOST - COMPLETO
    # ========================================================================
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
    def make_prediction(n_clicks, pob, urb, rur, ipm, acue, alc, ener, pib, hom, 
                   sexo, edad, ciclo, escol, depto):

        
        if n_clicks is None: 
            return None, "", None
        
        # VALIDACIÓN PREVIA - Si algún campo es None o inválido, no hacer predicción
        campos_requeridos = [pob, urb, rur, ipm, acue, alc, ener, pib, hom, 
                            sexo, edad, ciclo, escol, depto]
        
        if any(campo is None or campo == "" for campo in campos_requeridos):
            return dbc.Alert([
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                "Por favor complete todos los campos requeridos antes de calcular la predicción."
            ], color="warning", dismissable=True, className="fade-in",
            style={'borderRadius': '12px', 'fontSize': '14px'}), "", None
        
        # Preparar datos para la API       # Preparar datos para la API
            data = {
                "poblacion_menores": float(pob), 
                "porc_poblacion_urbana": float(urb), 
                "porc_poblacion_rural": float(rur), 
                "ipm": float(ipm), 
                "cobertura_acueducto": float(acue), 
                "cobertura_alcantarillado": float(alc), 
                "cobertura_energia": float(ener), 
                "pib_per_capita": float(pib), 
                "tasa_homicidio": float(hom), 
                "sexo_victima": sexo, 
                "grupo_edad_victima": edad, 
                "ciclo_vital": ciclo, 
                "escolaridad": escol, 
                "depto_hecho_dane": depto
            }
            
            # Llamar a la API
            result = predict_catboost(data)
            
            if result is None: 
                return dbc.Alert([
                    html.I(className="bi bi-exclamation-triangle-fill me-2"),
                    "Error al conectar con la API. Verifique la conexión."
                ], color="danger", dismissable=True, className="fade-in"), "", None
            
            # Extraer predicción
            prediccion = result.get('prediccion', 0)
            nivel, color = get_risk_level(prediccion)
            
            # Crear gráfico gauge
            gauge = create_gauge_chart(prediccion, "Tasa Proyectada por 100,000 hab.")
            
            # Construir resultado completo con toda la información
            results = html.Div([
                dbc.Card([
                    dbc.CardBody([
                        # Título
                        html.H5([
                            html.I(className="bi bi-check-circle-fill me-2", 
                                style={'color': COLORS['secondary']}),
                            "Resultados de la Predicción"
                        ], style={'color': COLORS['text'], 'fontWeight': '600', 
                                'marginBottom': '24px'}),
                        
                        # Sección principal: Gauge + Badge
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
                                    
                                    # Interpretación
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
                        
                        # Variables de Mayor Impacto
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
                                    style={'borderLeftColor': COLORS['danger'], 
                                            'borderLeftWidth': '4px'})
                                ], md=3, className="mb-3"),
                                
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
                                    style={'borderLeftColor': COLORS['warning'], 
                                            'borderLeftWidth': '4px'})
                                ], md=3, className="mb-3"),
                                
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
                                    style={'borderLeftColor': COLORS['info'], 
                                            'borderLeftWidth': '4px'})
                                ], md=3, className="mb-3"),
                                
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
                                    style={'borderLeftColor': COLORS['secondary'], 
                                            'borderLeftWidth': '4px'})
                                ], md=3, className="mb-3")
                            ])
                        ]),
                        
                        html.Hr(style={'margin': '32px 0', 'borderColor': COLORS['border']}),
                        
                        # Información adicional
                        html.Div([
                            html.H6([
                                html.I(className="bi bi-info-circle-fill me-2"),
                                "Información del Análisis"
                            ], style={'color': COLORS['text'], 'fontWeight': '600', 
                                    'marginBottom': '16px'}),
                            
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.Small("Departamento:", 
                                                style={'color': COLORS['text_muted'], 
                                                        'fontSize': '12px', 'display': 'block'}),
                                        html.P(depto, 
                                            style={'fontSize': '14px', 'fontWeight': '600', 
                                                    'color': COLORS['text'], 'marginBottom': '0'})
                                    ])
                                ], md=3),
                                
                                dbc.Col([
                                    html.Div([
                                        html.Small("Perfil de Víctima:", 
                                                style={'color': COLORS['text_muted'], 
                                                        'fontSize': '12px', 'display': 'block'}),
                                        html.P(f"{sexo} - {edad}", 
                                            style={'fontSize': '14px', 'fontWeight': '600', 
                                                    'color': COLORS['text'], 'marginBottom': '0'})
                                    ])
                                ], md=3),
                                
                                dbc.Col([
                                    html.Div([
                                        html.Small("Población Menores:", 
                                                style={'color': COLORS['text_muted'], 
                                                        'fontSize': '12px', 'display': 'block'}),
                                        html.P(f"{int(pob):,}", 
                                            style={'fontSize': '14px', 'fontWeight': '600', 
                                                    'color': COLORS['text'], 'marginBottom': '0'})
                                    ])
                                ], md=3),
                                
                                dbc.Col([
                                    html.Div([
                                        html.Small("Nivel de Riesgo:", 
                                                style={'color': COLORS['text_muted'], 
                                                        'fontSize': '12px', 'display': 'block'}),
                                        html.P(nivel, 
                                            style={'fontSize': '14px', 'fontWeight': '600', 
                                                    'color': color, 'marginBottom': '0'})
                                    ])
                                ], md=3)
                            ])
                        ])
                        
                    ], style={'padding': '32px'})
                ], className="shadow-sm fade-in", style={'borderRadius': '16px'})
            ])
            
            return results, "", result

    # ========================================================================
    # CLUSTERS - KMEANS
    # ========================================================================
    @app.callback(
        Output('kmeans-features-store', 'data'), 
        Input('active-module-store', 'data')
    )
    def load_kmeans_features(active_module):
        """Cargar features del modelo KMeans cuando se activa el módulo"""
        return get_kmeans_features() if active_module == 'clusters' else []

    @app.callback(
        [Output('kmeans-inputs-container', 'children'), 
         Output('kmeans-features-info', 'children')], 
        Input('kmeans-features-store', 'data')
    )
    def create_kmeans_inputs(features):
        """Generar inputs dinámicos para KMeans basados en features"""
        if not features: 
            return html.Div([
                dbc.Spinner(color="primary", size="sm"), 
                html.Span(" Cargando features...", className="ms-2")
            ], className="text-center py-4"), ""
        
        default_values = [28.07, 64.79, 17168300, 649.0, 15.52, 19.37]
        feature_icons = {
            0: "bi bi-speedometer2",
            1: "bi bi-people",
            2: "bi bi-cash-coin",
            3: "bi bi-house",
            4: "bi bi-graph-down",
            5: "bi bi-exclamation-triangle"
        }
        
        inputs = []
        for i, f in enumerate(features):
            icon = feature_icons.get(i, "bi bi-circle")
            inputs.append(
                html.Div([
                    dbc.Label([
                        html.I(className=f"{icon} me-2", 
                              style={'color': COLORS['primary'], 'fontSize': '16px'}),
                        html.Span(f"{f.replace('_', ' ').title()}", 
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
        
        return html.Div(inputs), f"✓ {len(features)} valores requeridos"

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
        """Realizar predicción con KMeans y visualizar clusters"""
        
        # Figura vacía por defecto
        empty_fig = go.Figure()
        empty_fig.update_layout(
            xaxis={'visible': False}, 
            yaxis={'visible': False}, 
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500,
            annotations=[{
                'text': 'Presione "Asignar Cluster" para ver la visualización',
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 14, 'color': COLORS['text_muted']}
            }]
        )
        
        # Validación
        if not input_values or len(input_values) != 6: 
            return dbc.Alert([
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                f"Error: Se requieren exactamente 6 valores (recibidos: {len(input_values) if input_values else 0})"
            ], color="danger", className="fade-in", 
               style={'borderRadius': '12px', 'fontSize': '14px'}), empty_fig, "", None
        
        # Predicción
        result = predict_kmeans([float(v) for v in input_values])
        
        if result is None: 
            return dbc.Alert([
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                "Error al conectar con la API. Verifique la conexión."
            ], color="danger", className="fade-in",
               style={'borderRadius': '12px', 'fontSize': '14px'}), empty_fig, "", None
        
        cluster = result.get('cluster_asignado', 0)
        nivel, color = get_vulnerability_level(cluster)
        
        # Card de resultado
        result_card = dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="bi bi-bullseye", 
                          style={'fontSize': '48px', 'color': color, 'marginBottom': '16px'})
                ], className="text-center"),
                html.H2(f"Cluster {cluster}", 
                       style={'color': color, 'fontWeight': '700', 
                             'textAlign': 'center', 'marginBottom': '12px'}),
                html.Div([
                    dbc.Badge([
                        html.I(className="bi bi-shield-fill-exclamation me-2"),
                        f"Vulnerabilidad: {nivel}"
                    ], color=color.replace('#', ''),
                       style={'fontSize': '16px', 'padding': '10px 20px', 'fontWeight': '600'})
                ], className="text-center mb-3"),
                
                html.Hr(style={'margin': '20px 0', 'borderColor': COLORS['border']}),
                
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
                ])
            ], style={'padding': '28px'})
        ], className="shadow-sm fade-in", style={'borderRadius': '16px'})
        
        # Scatter Plot mejorado
        cluster_colors = {
            0: COLORS['secondary'],
            1: COLORS['info'],
            2: COLORS['warning'],
            3: COLORS['danger']
        }
        
        fig = go.Figure()
        
        # Punto del usuario
        fig.add_trace(go.Scatter(
            x=[input_values[0]], 
            y=[input_values[1]], 
            mode='markers', 
            marker=dict(size=20, color=color, symbol='star', 
                       line=dict(width=2, color='white')),
            name='Tu Municipio',
            hovertemplate='<b>Tu Municipio</b><br>PC1: %{x:.2f}<br>PC2: %{y:.2f}<extra></extra>'
        ))
        
        # Puntos de referencia de otros clusters
        ref_points = {
            0: ([15, 20, 18], [50, 55, 52]),
            1: ([25, 30, 27], [60, 65, 62]),
            2: ([35, 40, 37], [70, 75, 72]),
            3: ([45, 50, 47], [80, 85, 82])
        }
        
        for clust, (x_vals, y_vals) in ref_points.items():
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='markers',
                marker=dict(size=10, color=cluster_colors.get(clust, COLORS['neutral']), 
                           opacity=0.6),
                name=f'Cluster {clust}',
                hovertemplate=f'<b>Cluster {clust}</b><br>PC1: %{{x:.2f}}<br>PC2: %{{y:.2f}}<extra></extra>'
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

    # ========================================================================
    # ALERTAS
    # ========================================================================
    @app.callback(
        Output('alertas-table-container', 'children'), 
        [Input('filter-departamento', 'value'), 
         Input('filter-nivel', 'value'), 
         Input('sort-column', 'value')]
    )
    def update_alertas_table(depto_filter, nivel_filter, sort_option):
        """Filtrar y ordenar tabla de alertas"""
        
        # Datos de ejemplo (en producción vendrían de la API)
        data = pd.DataFrame({
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
        if depto_filter != 'all': 
            data = data[data['Departamento'] == depto_filter]
        if nivel_filter != 'all': 
            data = data[data['Nivel_Alerta'] == nivel_filter]
        
        # Aplicar ordenamiento
        if sort_option == 'tasa_desc': 
            data = data.sort_values('Tasa_Proyectada', ascending=False)
        elif sort_option == 'tasa_asc':
            data = data.sort_values('Tasa_Proyectada', ascending=True)
        elif sort_option == 'municipio_asc':
            data = data.sort_values('Municipio', ascending=True)
        elif sort_option == 'poblacion_desc':
            data = data.sort_values('Poblacion_Menores', ascending=False)
        
        # Mensaje si no hay resultados
        if data.empty:
            return dbc.Alert([
                html.I(className="bi bi-info-circle me-2"),
                "No se encontraron municipios con los filtros seleccionados"
            ], color="info", style={'borderRadius': '12px', 'fontSize': '14px'})
        
        return create_alertas_table(data)

    @app.callback(
        Output('btn-export-alertas', 'children'), 
        Input('btn-export-alertas', 'n_clicks'), 
        prevent_initial_call=True
    )
    def export_alertas(n): 
        """Simular exportación de alertas"""
        return [html.I(className="bi bi-check-circle me-2"), "¡Exportado!"]

    @app.callback(
        [Output('modal-detalle-alerta', 'is_open'), 
         Output('modal-detalle-alerta-content', 'children')], 
        Input({'type': 'view-detail', 'index': ALL}, 'n_clicks'), 
        State('modal-detalle-alerta', 'is_open'), 
        prevent_initial_call=True
    )
    def toggle_modal(n, is_open):
        """Mostrar/ocultar modal de detalle de alerta"""
        if any(n):
            idx = eval(callback_context.triggered[0]['prop_id'].split('.')[0])['index']
            return not is_open, dbc.ModalBody([
                html.H5("Detalle del Municipio", className="mb-3"),
                html.P(f"Información detallada del municipio con índice {idx}")
            ])
        return is_open, html.Div()

    # ========================================================================
    # SIMULADOR
    # ========================================================================
    @app.callback(
        [Output(f'sim-{x}-value', 'children') for x in ['pib', 'homicidio', 'servicios', 'ipm']], 
        [Input(f'sim-{x}', 'value') for x in ['pib', 'homicidio', 'servicios', 'ipm']]
    )
    def update_sliders(pib, hom, serv, ipm): 
        """Actualizar valores mostrados en sliders del simulador"""
        return [f"{x:+d}" if x !=0 else "0" for x in [pib, hom, serv, ipm]]

    @app.callback(
        [Output(f'sim-{x}', 'value') for x in ['pib', 'homicidio', 'servicios', 'ipm']], 
        Input('btn-reset-simulador', 'n_clicks'), 
        prevent_initial_call=True
    )
    def reset_simulador(n): 
        """Restablecer sliders del simulador a cero"""
        return 0, 0, 0, 0

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
    def run_simulation(n, pib_c, hom_c, serv_c, ipm_c, base_pred):
        """Ejecutar simulación de escenarios"""
        
        if not base_pred: 
            return dbc.Alert([
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                "Primero debe ejecutar una predicción base en el módulo de Predicción CatBoost"
            ], color="warning", className="fade-in",
               style={'borderRadius': '12px', 'fontSize': '14px'})
        
        base = base_pred.get('prediccion', 0)
        
        # Calcular impactos
        impacto = (pib_c/100 * -0.15) + (hom_c/100 * 0.35) + (serv_c/100 * -0.10) + (ipm_c/100 * 0.25)
        simulado = base * (1 + impacto)
        diferencia = simulado - base
        porcentaje_cambio = (diferencia / base) * 100
        
        # Determinar colores
        nivel_base, color_base = get_risk_level(base)
        nivel_simulado, color_simulado = get_risk_level(simulado)
        
        # Gráfico de comparación
        fig = go.Figure(data=[
            go.Bar(name='Base', x=['Tasa'], y=[base], 
                  marker_color=color_base, text=[f'{base:.1f}'], textposition='auto'),
            go.Bar(name='Simulado', x=['Tasa'], y=[simulado], 
                  marker_color=color_simulado, text=[f'{simulado:.1f}'], textposition='auto')
        ])
        
        fig.update_layout(
            height=350, 
            plot_bgcolor='rgba(248, 250, 252, 0.5)',
            paper_bgcolor='rgba(0,0,0,0)',
            barmode='group',
            yaxis_title='Tasa por 100,000 habitantes',
            font={'family': 'Inter, sans-serif', 'color': COLORS['neutral']},
            showlegend=True,
            xaxis=dict(showticklabels=False),
            yaxis=dict(gridcolor=COLORS['border'], showgrid=True)
        )
        
        return html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.H5([
                        html.I(className="bi bi-calculator-fill me-2", 
                              style={'color': COLORS['primary']}),
                        "Resultados de la Simulación"
                    ], style={'color': COLORS['text'], 'fontWeight': '600', 
                             'marginBottom': '24px'}),
                    
                    # Métricas
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.Small("Base", style={'color': COLORS['text_muted'], 'fontSize': '12px'}),
                                html.H3(f"{base:.1f}", style={'color': color_base, 'fontWeight': '700'}),
                                dbc.Badge(nivel_base, color=color_base.replace('#', ''), style={'fontSize': '11px'})
                            ], className="text-center")
                        ], md=4),
                        dbc.Col([
                            html.Div([
                                html.Small("Cambio", style={'color': COLORS['text_muted'], 'fontSize': '12px'}),
                                html.H3(f"{diferencia:+.1f}", 
                                       style={'color': COLORS['danger'] if diferencia > 0 else COLORS['secondary'], 
                                             'fontWeight': '700'}),
                                html.Span(f"({porcentaje_cambio:+.1f}%)", 
                                         style={'fontSize': '14px', 'color': COLORS['neutral']})
                            ], className="text-center")
                        ], md=4),
                        dbc.Col([
                            html.Div([
                                html.Small("Simulado", style={'color': COLORS['text_muted'], 'fontSize': '12px'}),
                                html.H3(f"{simulado:.1f}", style={'color': color_simulado, 'fontWeight': '700'}),
                                dbc.Badge(nivel_simulado, color=color_simulado.replace('#', ''), style={'fontSize': '11px'})
                            ], className="text-center")
                        ], md=4)
                    ], className="mb-4"),
                    
                    dcc.Graph(figure=fig, config={'displayModeBar': False})
                ], style={'padding': '28px'})
            ], className="shadow-sm fade-in", style={'borderRadius': '16px'})
        ])
    # ========================================================================
    # RECOMENDACIONES
    # ========================================================================
    @app.callback(
        Output('recomendaciones-container', 'children'),
        Input('btn-generar-recomendaciones', 'n_clicks'),
        [State('nivel-detalle-recomendaciones', 'value'),
         State('prioridad-enfoque', 'value'),
         State('prediction-result-store', 'data')],
        prevent_initial_call=True
    )
    def generar_recomendaciones(n_clicks, nivel_detalle, prioridad, prediction_data):
        """Generar recomendaciones basadas en la predicción actual"""
        
        if not prediction_data:
            return dbc.Alert([
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                "Para generar recomendaciones, primero debe realizar una predicción en el módulo de Predicción CatBoost."
            ], color="warning", className="fade-in",
               style={'borderRadius': '12px', 'fontSize': '14px'})
        
        # Extraer datos de la predicción
        tasa_proyectada = prediction_data.get('prediccion', 0)
        nivel_riesgo, _ = get_risk_level(tasa_proyectada)
        
        # Importar la función auxiliar
        from pages.recomendaciones import create_recomendaciones_content
        
        # Generar contenido
        content = create_recomendaciones_content(
            nivel_riesgo=nivel_riesgo,
            tasa_proyectada=tasa_proyectada,
            nivel_detalle=nivel_detalle,
            prioridad=prioridad
        )
        
        return content
    
    @app.callback(
        Output('btn-download-recomendaciones', 'children'),
        Input('btn-download-recomendaciones', 'n_clicks'),
        prevent_initial_call=True
    )
    def download_recomendaciones(n):
        """Simular descarga de recomendaciones en PDF"""
        if n:
            return [
                html.I(className="bi bi-check-circle-fill me-2"),
                "PDF Generado - Descargando..."
            ]
        return [
            html.I(className="bi bi-file-pdf me-2"),
            "Descargar Recomendaciones en PDF"
        ]

