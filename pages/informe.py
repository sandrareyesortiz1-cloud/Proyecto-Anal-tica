from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
from config import COLORS

def create_informe_module():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2([html.I(className="bi bi-file-earmark-pdf-fill me-3", style={'color': COLORS['primary']}), "Generar Informe"], style={'fontWeight': '700', 'color': COLORS['text'], 'marginBottom': '8px'}),
                    html.P("Consolidado completo de análisis y recomendaciones", style={'color': COLORS['text_muted'], 'fontSize': '15px', 'marginBottom': '0'})
                ])
            ])
        ], className="mb-4"),
        dbc.Alert([html.I(className="bi bi-info-circle-fill me-2"), html.Span("El informe incluirá todos los análisis realizados en la sesión actual.")], color="info", className="mb-4", style={'borderRadius': '12px', 'border': 'none', 'fontSize': '14px'}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([html.I(className="bi bi-gear-fill me-2", style={'color': COLORS['primary']}), "Configuración"], style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '24px'}),
                        html.Div([html.Label("Título", style={'fontSize': '13px'}), dbc.Input(id="informe-titulo", value="Informe de Análisis Predictivo - Violencia Sexual NNA")], className="mb-4"),
                        html.Div([html.Label("Municipio", style={'fontSize': '13px'}), dbc.Input(id="informe-municipio", placeholder="Ej: Cartagena, Bolívar")], className="mb-4"),
                        html.Div([html.Label("Responsable", style={'fontSize': '13px'}), dbc.Input(id="informe-responsable", placeholder="Nombre del analista")], className="mb-4"),
                        dbc.Button([html.I(className="bi bi-file-earmark-arrow-down me-2"), "Generar Informe"], id="btn-generar-informe", color="success", size="lg", className="w-100", style={'fontWeight': '600', 'padding': '14px'}),
                        html.Div(id="informe-loading", className="text-center mt-3")
                    ], style={'padding': '28px'})
                ], className="shadow-sm", style={'borderRadius': '16px'})
            ], md=5),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([html.I(className="bi bi-eye me-2", style={'color': COLORS['primary']}), "Vista Previa"], style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '20px'}),
                        html.Div([
                            html.Div([
                                html.I(className="bi bi-file-earmark-text", style={'fontSize': '48px', 'color': COLORS['border']}),
                                html.P("El informe incluirá:", className="mt-3 mb-2", style={'fontSize': '14px', 'fontWeight': '600'}),
                                html.Ul([html.Li("Resumen ejecutivo"), html.Li("Gráficos y visualizaciones"), html.Li("Recomendaciones")], style={'paddingLeft': '20px'}),
                                html.Hr(),
                                html.Small([html.I(className="bi bi-clock me-1"), f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"], style={'color': COLORS['text_muted'], 'fontSize': '12px'})
                            ], className="text-center")
                        ])
                    ], style={'padding': '28px'})
                ], className="shadow-sm", style={'borderRadius': '16px'})
            ], md=7)
        ]),
        html.Div(id="informe-resultado", className="mt-4")
    ], fluid=True, style={'maxWidth': '1600px'})