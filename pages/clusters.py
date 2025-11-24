from dash import html, dcc
import dash_bootstrap_components as dbc
from config import COLORS

def create_clusters_module():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2([html.I(className="bi bi-diagram-3-fill me-3", style={'color': COLORS['primary']}), "Análisis de Clusters"], style={'fontWeight': '700', 'color': COLORS['text'], 'marginBottom': '8px'}),
                    html.P("Modelo KMeans para clasificación de vulnerabilidad municipal", style={'color': COLORS['text_muted'], 'fontSize': '15px', 'marginBottom': '0'})
                ])
            ])
        ], className="mb-4"),
        dbc.Alert([html.I(className="bi bi-info-circle-fill me-2"), html.Span("Ingrese los 6 valores en el orden correcto para asignar el cluster de vulnerabilidad del municipio")], color="info", className="mb-4", style={'borderRadius': '12px', 'border': 'none', 'fontSize': '14px'}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([html.H5([html.I(className="bi bi-pencil-square me-2", style={'color': COLORS['primary']}), "Ingresar Valores"], style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '8px'}), html.Small(id="kmeans-features-info", style={'color': COLORS['text_muted'], 'fontSize': '13px'})], className="mb-4"),
                        html.Div(id="kmeans-inputs-container"),
                        dbc.Button([html.I(className="bi bi-diagram-3-fill me-2"), "Asignar Cluster"], id="btn-kmeans", color="primary", size="lg", className="w-100 mt-4", style={'fontWeight': '600', 'padding': '14px'}),
                        html.Div(id="kmeans-loading", className="text-center mt-3")
                    ], style={'padding': '28px'})
                ], className="shadow-sm mb-4", style={'borderRadius': '16px'}),
                html.Div(id="kmeans-result-card")
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([html.I(className="bi bi-graph-up me-2", style={'color': COLORS['info']}), "Visualización de Clusters"], style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '20px'}),
                        dcc.Graph(id="cluster-scatter", config={'displayModeBar': False}, style={'height': '500px'})
                    ], style={'padding': '28px'})
                ], className="shadow-sm", style={'borderRadius': '16px'})
            ], md=8)
        ])
    ], fluid=True, style={'maxWidth': '1600px'})