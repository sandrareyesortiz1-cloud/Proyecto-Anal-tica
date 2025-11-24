from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from config import COLORS
from components import create_navbar, create_sidebar, create_content_area
from callbacks import register_callbacks
import os

# ============================================================
# INICIALIZACIÓN DE LA APLICACIÓN
# ============================================================
app = Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css",
    ],
    suppress_callback_exceptions=True,
    title="Dashboard NNA",
    update_title="Cargando...",
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"
        },
        {
            "name": "description",
            "content": "Dashboard avanzado para predicción y análisis de datos de NNA"
        },
        {
            "name": "theme-color",
            "content": "#007AFF"
        },
        {
            "name": "apple-mobile-web-app-capable",
            "content": "yes"
        },
        {
            "name": "apple-mobile-web-app-status-bar-style",
            "content": "default"
        }
    ]
)

server = app.server

# ============================================================
# CONFIGURACIÓN DE STORES - Estado Global de la Aplicación
# ============================================================
app_stores = html.Div([
    # Store de salud de la API
    dcc.Store(id='api-health-store', storage_type='session'),
    
    # Store de características K-Means
    dcc.Store(id='kmeans-features-store', storage_type='session'),
    
    # Store del módulo activo
    dcc.Store(id='active-module-store', data='prediccion', storage_type='session'),
    
    # Store de resultados de predicción
    dcc.Store(id='prediction-result-store', storage_type='memory'),
    
    # Store de resultados de clustering
    dcc.Store(id='cluster-result-store', storage_type='memory'),
    
    # Store de configuración de usuario
    dcc.Store(
        id='user-config-store',
        data={
            'theme': 'light',
            'animations': True,
            'notifications': True,
            'sidebarCollapsed': False
        },
        storage_type='local'
    ),
    
    # Store de historial de navegación
    dcc.Store(id='navigation-history-store', data=[], storage_type='session'),
    
    # Store para controlar el sidebar mobile
    dcc.Store(id='sidebar-state-store', data={'isOpen': False}, storage_type='memory'),
    
    # Interval para health check
    dcc.Interval(id='health-check-interval', interval=30000, n_intervals=0),
    
    # Interval para auto-refresh de datos
    dcc.Interval(id='data-refresh-interval', interval=300000, n_intervals=0, disabled=True),
    
    # Location para routing
    dcc.Location(id='url', refresh=False)
], style={'display': 'none'})

# ============================================================
# LOADING OVERLAY - Pantalla de carga inicial
# ============================================================
loading_overlay = html.Div(
    id='loading-overlay',
    children=[
        html.Div([
            # Logo o icono animado
            html.Div([
                html.I(className="bi bi-graph-up-arrow", style={
                    'fontSize': '48px',
                    'color': 'white',
                    'marginBottom': '20px',
                    'animation': 'pulse 1.5s ease-in-out infinite'
                })
            ]),
            # Spinner
            dbc.Spinner(
                color="light",
                type="border",
                size="lg",
                spinner_class_name="mb-3"
            ),
            # Textos
            html.H4("Dashboard NNA", className="text-white fw-bold mb-2"),
            html.P("Inicializando componentes...", className="text-white-50 mb-0", style={'fontSize': '14px'})
        ], style={
            'textAlign': 'center',
            'animation': 'fadeIn 0.5s ease-out'
        })
    ],
    style={
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'width': '100%',
        'height': '100%',
        'background': 'linear-gradient(135deg, #007AFF 0%, #0051D5 100%)',
        'backdropFilter': 'blur(20px)',
        'zIndex': 9999,
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'opacity': 1,
        'transition': 'opacity 0.5s ease-out',
        'animation': 'fadeOut 0.5s ease-out 1.5s forwards'
    }
)

# ============================================================
# TOAST CONTAINER - Sistema de notificaciones
# ============================================================
toast_container = html.Div(
    id='toast-container',
    children=[],
    style={
        'position': 'fixed',
        'top': '80px',
        'right': '20px',
        'zIndex': 9998,
        'maxWidth': '400px',
        'display': 'flex',
        'flexDirection': 'column',
        'gap': '10px'
    }
)

# ============================================================
# MODAL GLOBAL - Confirmaciones y diálogos
# ============================================================
global_modal = dbc.Modal(
    [
        dbc.ModalHeader(
            dbc.ModalTitle(id='global-modal-title', children="Confirmación"),
            close_button=True
        ),
        dbc.ModalBody(id='global-modal-body', children=""),
        dbc.ModalFooter([
            dbc.Button(
                "Cancelar",
                id="global-modal-cancel",
                color="light",
                className="me-2",
                n_clicks=0
            ),
            dbc.Button(
                "Confirmar",
                id="global-modal-confirm",
                color="primary",
                n_clicks=0
            )
        ])
    ],
    id='global-modal',
    is_open=False,
    centered=True,
    backdrop='static',
    className='modal-premium'
)

# ============================================================
# SIDEBAR MOBILE OVERLAY - Backdrop para cerrar sidebar
# ============================================================
sidebar_overlay = html.Div(
    id='sidebar-overlay',
    style={
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'width': '100%',
        'height': '100%',
        'backgroundColor': 'rgba(0, 0, 0, 0.5)',
        'backdropFilter': 'blur(4px)',
        'zIndex': 1019,
        'display': 'none',
        'opacity': 0,
        'transition': 'opacity 0.3s ease'
    }
)

# ============================================================
# CONTENIDO POR DEFECTO - Página de bienvenida
# ============================================================
welcome_content = html.Div([
    # Hero section
    html.Div([
        html.Div([
            html.I(className="bi bi-graph-up-arrow", style={
                'fontSize': '64px',
                'color': 'var(--apple-blue)',
                'marginBottom': '20px',
                'display': 'block'
            }),
            html.H1("Bienvenido al Dashboard NNA", className="fw-bold mb-3", style={
                'fontSize': '42px',
                'letterSpacing': '-0.04em',
                'color': 'var(--apple-gray-5)'
            }),
            html.P("Sistema inteligente de predicción y análisis de datos", className="text-muted mb-4", style={
                'fontSize': '18px',
                'maxWidth': '600px',
                'margin': '0 auto'
            }),
            html.Div([
                dbc.Button(
                    [html.I(className="bi bi-rocket-takeoff me-2"), "Comenzar Análisis"],
                    color="primary",
                    size="lg",
                    className="me-3",
                    id="welcome-start-btn"
                ),
                dbc.Button(
                    [html.I(className="bi bi-book me-2"), "Ver Documentación"],
                    color="light",
                    size="lg",
                    outline=True,
                    id="welcome-docs-btn"
                )
            ], className="d-flex justify-content-center gap-3 flex-wrap")
        ], className="text-center mb-5")
    ], className="py-5"),
    
    # Cards de características
    html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-stars", style={
                                'fontSize': '32px',
                                'color': 'var(--apple-blue)'
                            })
                        ], className="mb-3"),
                        html.H4("Predicción Avanzada", className="fw-bold mb-2"),
                        html.P("Utiliza algoritmos de machine learning para predecir resultados con alta precisión.", 
                               className="text-muted mb-0")
                    ])
                ], className="h-100 hover-lift")
            ], xs=12, md=6, lg=4, className="mb-4"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-diagram-3", style={
                                'fontSize': '32px',
                                'color': '#34C759'
                            })
                        ], className="mb-3"),
                        html.H4("Clustering Inteligente", className="fw-bold mb-2"),
                        html.P("Agrupa datos similares automáticamente y descubre patrones ocultos en la información.", 
                               className="text-muted mb-0")
                    ])
                ], className="h-100 hover-lift")
            ], xs=12, md=6, lg=4, className="mb-4"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-bar-chart-line", style={
                                'fontSize': '32px',
                                'color': '#FF9500'
                            })
                        ], className="mb-3"),
                        html.H4("Visualización Premium", className="fw-bold mb-2"),
                        html.P("Gráficos interactivos y dashboards personalizables para análisis profundo.", 
                               className="text-muted mb-0")
                    ])
                ], className="h-100 hover-lift")
            ], xs=12, md=6, lg=4, className="mb-4"),
        ])
    ], className="container-fluid px-4"),
    
    # Stats rápidas
    html.Div([
        html.H3("Estado del Sistema", className="fw-bold mb-4 text-center"),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="bi bi-cpu", style={'fontSize': '24px', 'color': 'var(--apple-blue)'})
                    ], className="stat-card-icon"),
                    html.Div("API", className="stat-card-label"),
                    html.Div([
                        dbc.Spinner(size="sm", color="success", spinner_class_name="me-2"),
                        html.Span("Conectado", style={'fontSize': '14px', 'color': '#34C759', 'fontWeight': '600'})
                    ], className="d-flex align-items-center justify-content-center mt-2")
                ], className="stat-card text-center", style={'borderLeftColor': 'var(--apple-blue)'})
            ], xs=12, sm=6, lg=3, className="mb-3"),
            
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="bi bi-layers", style={'fontSize': '24px', 'color': '#34C759'})
                    ], className="stat-card-icon"),
                    html.Div("Modelos", className="stat-card-label"),
                    html.Div("2 Activos", className="stat-card-value", style={'fontSize': '20px'})
                ], className="stat-card text-center", style={'borderLeftColor': '#34C759'})
            ], xs=12, sm=6, lg=3, className="mb-3"),
            
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="bi bi-clock-history", style={'fontSize': '24px', 'color': '#FF9500'})
                    ], className="stat-card-icon"),
                    html.Div("Última Act.", className="stat-card-label"),
                    html.Div("Ahora", className="stat-card-value", style={'fontSize': '20px'})
                ], className="stat-card text-center", style={'borderLeftColor': '#FF9500'})
            ], xs=12, sm=6, lg=3, className="mb-3"),
            
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="bi bi-shield-check", style={'fontSize': '24px', 'color': '#5AC8FA'})
                    ], className="stat-card-icon"),
                    html.Div("Seguridad", className="stat-card-label"),
                    html.Div("100%", className="stat-card-value", style={'fontSize': '20px'})
                ], className="stat-card text-center", style={'borderLeftColor': '#5AC8FA'})
            ], xs=12, sm=6, lg=3, className="mb-3"),
        ])
    ], className="container-fluid px-4 mt-5")
], className="fade-in", style={'padding': '40px 20px'})

# ============================================================
# LAYOUT PRINCIPAL - Estructura de la Aplicación
# ============================================================
# ============================================================
# LAYOUT PRINCIPAL - Estructura de la Aplicación
# ============================================================
app.layout = html.Div([
    # Stores y componentes ocultos
    app_stores,
    
    # Loading overlay
    loading_overlay,
    
    # Sidebar overlay (backdrop mobile) - CORREGIDO
    html.Div(
        id='sidebar-overlay',
        n_clicks=0,
        style={
            'display': 'none'
        }
    ),
    
    # Toast container
    toast_container,
    
    # Modal global
    global_modal,
    
    # Barra de navegación superior
    create_navbar(),
    
    # Sidebar navegación
    create_sidebar(),
    
    # Container principal de contenido
    html.Div([
        # Contenido dinámico
        html.Div(
            id='main-content',
            children=welcome_content,
            style={
                'padding': '20px',
                'minHeight': '100vh'
            }
        )
    ], id='main-content-wrapper', style={
        'marginLeft': '260px',
        'marginTop': '70px',
        'width': 'calc(100% - 260px)',
        'minHeight': 'calc(100vh - 70px)',
        'transition': 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        'backgroundColor': '#F5F5F7'
    })
    
], style={
    'backgroundColor': '#F5F5F7',
    'minHeight': '100vh',
    'position': 'relative'
}, id='app-container')

# ============================================================
# REGISTRO DE CALLBACKS
# ============================================================
register_callbacks(app)

# ============================================================
# CONFIGURACIÓN DEL SERVIDOR
# ============================================================
if __name__ == '__main__':
    # Configuración desde variables de entorno
    DEBUG_MODE = os.getenv('DASH_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('DASH_HOST', '127.0.0.1')
    PORT = int(os.getenv('DASH_PORT', '8050'))
    
    print("\n" + "=" * 60)
    print("🚀 INICIANDO DASHBOARD NNA")
    print("=" * 60)
    print(f"📍 Host:        {HOST}")
    print(f"🔌 Puerto:      {PORT}")
    print(f"🐛 Debug:       {DEBUG_MODE}")
    print(f"🌐 URL Local:   http://{HOST}:{PORT}")
    print(f"📱 URL Red:     http://localhost:{PORT}")
    print("=" * 60)
    print("✅ Aplicación lista. Abre el navegador en la URL indicada.")
    print("=" * 60 + "\n")
    
    app.run(
        debug=DEBUG_MODE,
        host=HOST,
        port=PORT,
        dev_tools_hot_reload=DEBUG_MODE,
        dev_tools_ui=DEBUG_MODE,
        dev_tools_props_check=DEBUG_MODE
    )