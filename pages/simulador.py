from dash import html, dcc
import dash_bootstrap_components as dbc
from config import COLORS, COLORS_ALPHA

def create_simulador_module():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2([html.I(className="bi bi-sliders me-3", style={'color': COLORS['primary']}), "Simulador de Escenarios"], style={'fontWeight': '700', 'color': COLORS['text'], 'marginBottom': '8px'}),
                    html.P("Evalúe el impacto de cambios en variables clave sobre el riesgo", style={'color': COLORS['text_muted'], 'fontSize': '15px', 'marginBottom': '0'})
                ])
            ])
        ], className="mb-4"),
        dbc.Alert([html.I(className="bi bi-info-circle-fill me-2"), html.Span("Primero ejecute una predicción base en el módulo de Predicción CatBoost. Los valores actuales se tomarán como línea base.")], id="simulador-info", color="info", className="mb-4", style={'borderRadius': '12px', 'border': 'none', 'fontSize': '14px'}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([html.H5([html.I(className="bi bi-sliders me-2", style={'color': COLORS['primary']}), "Ajustar Variables"], style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '8px'}), html.Small("Modifique los porcentajes para simular cambios", style={'color': COLORS['text_muted'], 'fontSize': '13px'})], className="mb-4"),
                        html.Div([
                            # PIB
                            html.Div([html.Label([html.I(className="bi bi-cash-coin me-2", style={'color': COLORS['warning'], 'fontSize': '18px'}), html.Span("PIB per cápita", style={'fontWeight': '500', 'fontSize': '14px'})], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px'}), html.Div([html.Span(id="sim-pib-value", style={'fontSize': '20px', 'fontWeight': '600', 'color': COLORS['primary']}), html.Span("% de cambio", style={'fontSize': '13px', 'color': COLORS['text_muted'], 'marginLeft': '8px'})], style={'marginBottom': '12px'}), dcc.Slider(id="sim-pib", min=-50, max=50, step=5, value=0, marks={-50: '-50%', -25: '-25%', 0: '0%', 25: '+25%', 50: '+50%'})], className="mb-4", style={'padding': '16px', 'backgroundColor': COLORS_ALPHA['warning_10'], 'borderRadius': '12px'}),
                            # Homicidio
                            html.Div([html.Label([html.I(className="bi bi-exclamation-triangle me-2", style={'color': COLORS['danger'], 'fontSize': '18px'}), html.Span("Tasa de homicidio", style={'fontWeight': '500', 'fontSize': '14px'})], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px'}), html.Div([html.Span(id="sim-homicidio-value", style={'fontSize': '20px', 'fontWeight': '600', 'color': COLORS['primary']}), html.Span("% de cambio", style={'fontSize': '13px', 'color': COLORS['text_muted'], 'marginLeft': '8px'})], style={'marginBottom': '12px'}), dcc.Slider(id="sim-homicidio", min=-50, max=50, step=5, value=0, marks={-50: '-50%', -25: '-25%', 0: '0%', 25: '+25%', 50: '+50%'})], className="mb-4", style={'padding': '16px', 'backgroundColor': COLORS_ALPHA['danger_10'], 'borderRadius': '12px'}),
                            # Servicios
                            html.Div([html.Label([html.I(className="bi bi-building me-2", style={'color': COLORS['secondary'], 'fontSize': '18px'}), html.Span("Cobertura de servicios", style={'fontWeight': '500', 'fontSize': '14px'})], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px'}), html.Div([html.Span(id="sim-servicios-value", style={'fontSize': '20px', 'fontWeight': '600', 'color': COLORS['primary']}), html.Span("% de cambio", style={'fontSize': '13px', 'color': COLORS['text_muted'], 'marginLeft': '8px'})], style={'marginBottom': '12px'}), dcc.Slider(id="sim-servicios", min=-20, max=20, step=2, value=0, marks={-20: '-20%', -10: '-10%', 0: '0%', 10: '+10%', 20: '+20%'})], className="mb-4", style={'padding': '16px', 'backgroundColor': COLORS_ALPHA['secondary_10'], 'borderRadius': '12px'}),
                            # IPM
                            html.Div([html.Label([html.I(className="bi bi-graph-down me-2", style={'color': COLORS['info'], 'fontSize': '18px'}), html.Span("Índice de Pobreza (IPM)", style={'fontWeight': '500', 'fontSize': '14px'})], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px'}), html.Div([html.Span(id="sim-ipm-value", style={'fontSize': '20px', 'fontWeight': '600', 'color': COLORS['primary']}), html.Span("% de cambio", style={'fontSize': '13px', 'color': COLORS['text_muted'], 'marginLeft': '8px'})], style={'marginBottom': '12px'}), dcc.Slider(id="sim-ipm", min=-30, max=30, step=5, value=0, marks={-30: '-30%', -15: '-15%', 0: '0%', 15: '+15%', 30: '+30%'})], className="mb-4", style={'padding': '16px', 'backgroundColor': COLORS_ALPHA['primary_10'], 'borderRadius': '12px'})
                        ]),
                        html.Hr(style={'margin': '24px 0', 'borderColor': COLORS['border']}),
                        dbc.Row([dbc.Col([dbc.Button([html.I(className="bi bi-arrow-clockwise me-2"), "Restablecer"], id="btn-reset-simulador", color="light", className="w-100", outline=True, style={'fontWeight': '500', 'padding': '12px'})], md=6), dbc.Col([dbc.Button([html.I(className="bi bi-play-circle-fill me-2"), "Simular"], id="btn-simular", color="primary", className="w-100", style={'fontWeight': '600', 'padding': '12px'})], md=6)])
                    ], style={'padding': '28px'})
                ], className="shadow-sm", style={'borderRadius': '16px'})
            ], md=4),
            dbc.Col([html.Div(id="simulador-results")], md=8)
        ])
    ], fluid=True, style={'maxWidth': '1600px'})
