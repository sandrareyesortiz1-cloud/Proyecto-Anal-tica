from dash import html, dcc
import dash_bootstrap_components as dbc
from config import COLORS

def create_navbar():
    """
    Navbar responsive con toggle button para mobile
    """
    return html.Div([
        dbc.Navbar(
            dbc.Container([
                # Toggle button para mobile
                html.Button(
                    html.I(className="bi bi-list"),
                    id='sidebar-toggle-btn',
                    n_clicks=0,
                    style={
                        'border': 'none',
                        'background': 'transparent',
                        'color': 'white',
                        'fontSize': '28px',
                        'cursor': 'pointer',
                        'padding': '0',
                        'marginRight': '16px',
                        'display': 'none',
                        'lineHeight': '1'
                    },
                    className='sidebar-toggle-mobile'
                ),
                
                # Logo y título
                html.Div([
                    html.I(
                        className="bi bi-shield-fill", 
                        style={
                            'fontSize': '32px', 
                            'color': 'white',
                            'marginRight': '12px'
                        }
                    ),
                    html.Div([
                        html.Div(
                            "Prevención Violencia NNA", 
                            style={
                                'fontSize': '19px', 
                                'fontWeight': '700', 
                                'color': 'white', 
                                'letterSpacing': '-0.02em',
                                'lineHeight': '1.2',
                                'marginBottom': '2px'
                            }
                        ),
                        html.Div(
                            "Sistema de Análisis Predictivo", 
                            style={
                                'fontSize': '12px', 
                                'color': 'rgba(255,255,255,0.9)',
                                'fontWeight': '500',
                                'letterSpacing': '0.01em'
                            },
                            className='navbar-subtitle'
                        )
                    ])
                ], style={
                    'display': 'flex', 
                    'alignItems': 'center'
                }),
                
                # Badge de estado de API
                html.Div(id='api-status-badge', style={'marginLeft': 'auto'})
                
            ], fluid=True),
            
            color='primary',
            dark=True,
            sticky='top',
            style={
                'background': 'linear-gradient(135deg, #007AFF 0%, #0051D5 100%)',
                'boxShadow': '0 2px 12px rgba(0, 0, 0, 0.1)',
                'padding': '14px 0',
                'height': '70px',
                'zIndex': '1030'
            }
        )
    ])

def create_sidebar():
    """
    Sidebar responsive con overlay para mobile
    """
    menu_items = [
        {'id': 'prediccion', 'icon': 'bi-graph-up-arrow', 'label': 'Predicción CatBoost'},
        {'id': 'clusters', 'icon': 'bi-diagram-3-fill', 'label': 'Análisis de Clusters'},
        {'id': 'alertas', 'icon': 'bi-exclamation-triangle-fill', 'label': 'Alertas Tempranas'},
        {'id': 'recomendaciones', 'icon': 'bi-lightbulb-fill', 'label': 'Recomendaciones'},
        {'id': 'simulador', 'icon': 'bi-sliders', 'label': 'Simulador de Escenarios'},
        {'id': 'informe', 'icon': 'bi-file-earmark-pdf-fill', 'label': 'Generar Informe'}
    ]
    
    buttons = []
    for item in menu_items:
        buttons.append(
            dbc.Button(
                [
                    html.I(className=f"{item['icon']} me-3", style={'fontSize': '18px'}), 
                    html.Span(item['label'])
                ],
                id={'type': 'nav-button', 'index': item['id']},
                className='sidebar-button w-100 text-start',
                n_clicks=0,
                style={
                    'marginBottom': '6px',
                    'border': 'none'
                }
            )
        )
    
    return html.Div([
        html.Div([
            # Header con título y botón de cierre
            html.Div([
                html.Div([
                    html.I(
                        className="bi bi-grid-3x3-gap-fill", 
                        style={'color': '#007AFF', 'fontSize': '20px', 'marginRight': '8px'}
                    ),
                    html.H6(
                        "Módulos", 
                        style={
                            'margin': '0',
                            'color': '#1D1D1F', 
                            'fontWeight': '700',
                            'fontSize': '16px',
                            'display': 'inline-block'
                        }
                    )
                ], style={'display': 'flex', 'alignItems': 'center'}),
                
                # Botón de cierre (solo mobile)
                html.Button(
                    html.I(className="bi bi-x-lg"),
                    id='sidebar-close-btn',
                    n_clicks=0,
                    style={
                        'border': 'none',
                        'background': 'transparent',
                        'color': '#86868B',
                        'fontSize': '20px',
                        'cursor': 'pointer',
                        'padding': '4px',
                        'display': 'none'
                    },
                    className='sidebar-close-mobile'
                )
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'marginBottom': '24px'
            }),
            
            # Menú de navegación
            html.Div(buttons)
            
        ], style={'padding': '24px 16px'})
    ], 
    id='sidebar',
    style={
        'width': '260px',
        'background': 'rgba(255, 255, 255, 0.98)',
        'borderRight': '0.5px solid rgba(0, 0, 0, 0.08)',
        'height': 'calc(100vh - 70px)',
        'position': 'fixed',
        'overflowY': 'auto',
        'top': '70px',
        'left': '0',
        'zIndex': '1020',
        'boxShadow': '2px 0 12px rgba(0, 0, 0, 0.04)',
        'transition': 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
    })

def create_content_area():
    """
    Área de contenido principal - NO USAR, se maneja en app.py
    """
    return html.Div(
        id='main-content-legacy',
        children=[],
        style={'display': 'none'}
    )
