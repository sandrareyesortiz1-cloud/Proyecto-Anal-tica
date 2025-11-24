from dash import html, dcc
import dash_bootstrap_components as dbc
from config import COLORS

def create_recomendaciones_module():
    """Crear interfaz del módulo de recomendaciones estratégicas"""
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2([
                        html.I(className="bi bi-lightbulb-fill me-3", 
                              style={'color': COLORS['warning']}),
                        "Recomendaciones Estratégicas"
                    ], style={'fontWeight': '700', 'color': COLORS['text'], 
                             'marginBottom': '8px'}),
                    html.P("Sistema inteligente de recomendaciones basado en análisis predictivo",
                          style={'color': COLORS['text_muted'], 'fontSize': '15px', 
                                'marginBottom': '0'})
                ])
            ])
        ], className="mb-4"),
        
        # Alert informativo
        dbc.Alert([
            html.I(className="bi bi-info-circle-fill me-2"),
            html.Span("Las recomendaciones se generan automáticamente basándose en la última predicción realizada. Ejecute una predicción primero para obtener sugerencias personalizadas.")
        ], id="recomendaciones-info-alert", color="info", className="mb-4", 
           style={'borderRadius': '12px', 'border': 'none', 'fontSize': '14px'}),
        
        # Selector de nivel de detalle
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H6([
                                html.I(className="bi bi-sliders me-2", 
                                      style={'color': COLORS['primary']}),
                                "Configuración de Recomendaciones"
                            ], style={'color': COLORS['text'], 'fontWeight': '600', 
                                     'marginBottom': '16px'}),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Nivel de Detalle", 
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral'], 'marginBottom': '8px'}),
                                    dcc.Dropdown(
                                        id="nivel-detalle-recomendaciones",
                                        options=[
                                            {'label': '📋 Resumen Ejecutivo', 'value': 'ejecutivo'},
                                            {'label': '📊 Análisis Detallado', 'value': 'detallado'},
                                            {'label': '🎯 Plan de Acción Completo', 'value': 'completo'}
                                        ],
                                        value='detallado',
                                        clearable=False,
                                        style={'fontSize': '14px'}
                                    )
                                ], md=6, className="mb-3"),
                                
                                dbc.Col([
                                    dbc.Label("Prioridad de Enfoque", 
                                             style={'fontSize': '13px', 'fontWeight': '500', 
                                                   'color': COLORS['neutral'], 'marginBottom': '8px'}),
                                    dcc.Dropdown(
                                        id="prioridad-enfoque",
                                        options=[
                                            {'label': '🚨 Prevención Inmediata', 'value': 'prevencion'},
                                            {'label': '🏥 Atención y Apoyo', 'value': 'atencion'},
                                            {'label': '📈 Fortalecimiento Institucional', 'value': 'institucional'},
                                            {'label': '🔄 Integral (Todas las áreas)', 'value': 'integral'}
                                        ],
                                        value='integral',
                                        clearable=False,
                                        style={'fontSize': '14px'}
                                    )
                                ], md=6, className="mb-3")
                            ]),
                            
                            dbc.Button(
                                [
                                    html.I(className="bi bi-stars me-2"),
                                    "Generar Recomendaciones"
                                ],
                                id="btn-generar-recomendaciones",
                                color="warning",
                                size="lg",
                                className="w-100 mt-3",
                                style={'fontWeight': '600', 'padding': '14px'}
                            )
                        ])
                    ], style={'padding': '24px'})
                ], className="shadow-sm", style={'borderRadius': '16px'})
            ])
        ], className="mb-4"),
        
        # Contenedor de recomendaciones
        html.Div(id="recomendaciones-container")
        
    ], fluid=True, style={'maxWidth': '1600px'})


def create_recomendaciones_content(nivel_riesgo, tasa_proyectada, nivel_detalle, prioridad, 
                                   departamento=None, ipm=None, tasa_homicidio=None):
    """
    Generar contenido de recomendaciones basado en el perfil de riesgo
    
    Args:
        nivel_riesgo: 'Bajo', 'Medio', 'Alto'
        tasa_proyectada: float
        nivel_detalle: 'ejecutivo', 'detallado', 'completo'
        prioridad: 'prevencion', 'atencion', 'institucional', 'integral'
        departamento: str (opcional)
        ipm: float (opcional)
        tasa_homicidio: float (opcional)
    """
    
    # Mapeo de colores por nivel
    color_map = {
        'Bajo': COLORS['secondary'],
        'Medio': COLORS['warning'],
        'Alto': COLORS['danger'],
        'Crítico': COLORS['danger']
    }
    
    color_nivel = color_map.get(nivel_riesgo, COLORS['neutral'])
    
    # Base de recomendaciones por nivel de riesgo
    recomendaciones_base = {
        'Bajo': {
            'titulo': 'Estrategia de Mantenimiento y Fortalecimiento',
            'descripcion': 'El municipio presenta indicadores favorables. Las acciones deben enfocarse en mantener y fortalecer los programas exitosos.',
            'acciones': [
                {
                    'categoria': 'Prevención',
                    'icon': 'bi-shield-check',
                    'color': COLORS['secondary'],
                    'items': [
                        'Mantener programas educativos en instituciones escolares',
                        'Fortalecer redes comunitarias de protección',
                        'Continuar campañas de sensibilización permanente',
                        'Implementar sistema de monitoreo continuo de indicadores'
                    ]
                },
                {
                    'categoria': 'Institucional',
                    'icon': 'bi-building',
                    'color': COLORS['info'],
                    'items': [
                        'Documentar buenas prácticas para replicar en otros municipios',
                        'Capacitar equipos en detección temprana',
                        'Crear protocolos de actuación preventiva',
                        'Establecer alianzas interinstitucionales sólidas'
                    ]
                }
            ]
        },
        'Medio': {
            'titulo': 'Estrategia de Refuerzo y Atención Prioritaria',
            'descripcion': 'El municipio requiere atención focalizada. Es necesario implementar acciones preventivas específicas y fortalecer la respuesta institucional.',
            'acciones': [
                {
                    'categoria': 'Prevención Reforzada',
                    'icon': 'bi-exclamation-triangle',
                    'color': COLORS['warning'],
                    'items': [
                        'Intensificar programas educativos en zonas de mayor vulnerabilidad',
                        'Implementar talleres de parentalidad positiva y crianza respetuosa',
                        'Crear espacios seguros y recreativos para NNA',
                        'Establecer líneas de reporte anónimo y seguro',
                        'Desarrollar campañas focalizadas en grupos de riesgo'
                    ]
                },
                {
                    'categoria': 'Atención y Servicios',
                    'icon': 'bi-heart-pulse',
                    'color': COLORS['danger'],
                    'items': [
                        'Fortalecer servicios de atención psicosocial',
                        'Ampliar horarios de atención en comisarías de familia',
                        'Capacitar personal de salud en detección de signos de alerta',
                        'Crear rutas de atención clara y accesible',
                        'Implementar seguimiento a casos identificados'
                    ]
                },
                {
                    'categoria': 'Fortalecimiento Institucional',
                    'icon': 'bi-gear',
                    'color': COLORS['info'],
                    'items': [
                        'Aumentar personal especializado en protección infantil',
                        'Mejorar coordinación entre instituciones (salud, educación, justicia)',
                        'Implementar sistema de información integrado',
                        'Realizar auditorías periódicas de protocolos'
                    ]
                }
            ]
        },
        'Alto': {
            'titulo': 'Estrategia de Intervención Urgente y Transformación',
            'descripcion': 'El municipio presenta nivel de riesgo alto. Se requiere intervención inmediata, coordinada y con asignación prioritaria de recursos.',
            'acciones': [
                {
                    'categoria': 'Acción Inmediata (0-3 meses)',
                    'icon': 'bi-exclamation-octagon-fill',
                    'color': COLORS['danger'],
                    'items': [
                        'DECLARAR ALERTA MUNICIPAL - Activar comité de emergencia',
                        'Asignar presupuesto de emergencia para protección de NNA',
                        'Reforzar inmediatamente personal en comisarías y defensoría',
                        'Implementar operativos de identificación de casos en zonas críticas',
                        'Crear centro temporal de atención y protección 24/7',
                        'Establecer mesa permanente de coordinación interinstitucional'
                    ]
                },
                {
                    'categoria': 'Prevención Intensiva (3-12 meses)',
                    'icon': 'bi-shield-fill-exclamation',
                    'color': COLORS['warning'],
                    'items': [
                        'Desplegar brigadas móviles de prevención en sectores de alto riesgo',
                        'Implementar programa integral de educación sexual y prevención',
                        'Crear red de líderes comunitarios capacitados en protección',
                        'Establecer sistema de alerta temprana con indicadores específicos',
                        'Realizar jornadas masivas de sensibilización casa a casa',
                        'Implementar programa de mentoría para familias vulnerables'
                    ]
                },
                {
                    'categoria': 'Atención Especializada',
                    'icon': 'bi-hospital',
                    'color': COLORS['primary'],
                    'items': [
                        'Crear unidad especializada de atención a víctimas (médica, psicológica, legal)',
                        'Implementar modelo de atención integral con enfoque de trauma',
                        'Establecer casas de acogida temporal para casos de emergencia',
                        'Contratar equipo multidisciplinario especializado',
                        'Implementar programa de seguimiento post-atención a largo plazo',
                        'Crear protocolo de atención diferencial por edad y género'
                    ]
                },
                {
                    'categoria': 'Transformación Estructural (12+ meses)',
                    'icon': 'bi-building-gear',
                    'color': COLORS['info'],
                    'items': [
                        'Reestructurar sistema municipal de protección infantil',
                        'Implementar observatorio municipal de violencia contra NNA',
                        'Crear política pública específica con metas medibles',
                        'Establecer sistema de monitoreo y evaluación permanente',
                        'Gestionar recursos nacionales e internacionales',
                        'Desarrollar plan de sostenibilidad financiera a mediano plazo'
                    ]
                }
            ]
        }
    }
    
    # Obtener recomendaciones base
    recs_base = recomendaciones_base.get(nivel_riesgo, recomendaciones_base['Medio'])
    
    # Recomendaciones adicionales basadas en variables específicas
    recomendaciones_adicionales = []
    
    if ipm and ipm > 0.3:
        recomendaciones_adicionales.append({
            'titulo': 'Alto Índice de Pobreza Multidimensional',
            'icon': 'bi-graph-down',
            'color': COLORS['danger'],
            'items': [
                'Priorizar programas de transferencias condicionadas a familias vulnerables',
                'Ampliar cobertura de programas de alimentación escolar',
                'Implementar subsidios para servicios básicos en zonas críticas',
                'Crear programas de generación de ingresos para madres cabeza de familia'
            ]
        })
    
    if tasa_homicidio and tasa_homicidio > 15:
        recomendaciones_adicionales.append({
            'titulo': 'Alta Tasa de Homicidios - Inseguridad',
            'icon': 'bi-exclamation-diamond',
            'color': COLORS['danger'],
            'items': [
                'Coordinar con policía para aumentar patrullaje en zonas escolares',
                'Implementar rutas seguras para NNA (escuela-hogar)',
                'Crear espacios comunitarios protegidos para actividades recreativas',
                'Establecer programa de desarme y convivencia ciudadana',
                'Iluminar vías y espacios públicos frecuentados por menores'
            ]
        })
    
    # Construir el contenido visual
    content = html.Div([
        # Card principal con resumen
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    # Ícono y título
                    html.Div([
                        html.I(className="bi bi-clipboard-check-fill", 
                              style={'fontSize': '48px', 'color': color_nivel, 
                                    'marginBottom': '16px'})
                    ], className="text-center"),
                    
                    html.H3(recs_base['titulo'], 
                           style={'color': COLORS['text'], 'fontWeight': '700', 
                                 'textAlign': 'center', 'marginBottom': '12px'}),
                    
                    html.Div([
                        dbc.Badge([
                            html.I(className="bi bi-info-circle me-2"),
                            f"Nivel de Riesgo: {nivel_riesgo}"
                        ], color=color_nivel.replace('#', ''),
                           style={'fontSize': '14px', 'padding': '8px 16px', 'fontWeight': '500'})
                    ], className="text-center mb-3"),
                    
                    html.Hr(style={'margin': '24px 0', 'borderColor': COLORS['border']}),
                    
                    # Descripción
                    html.P(recs_base['descripcion'],
                          style={'fontSize': '15px', 'color': COLORS['neutral'], 
                                'lineHeight': '1.8', 'textAlign': 'center', 
                                'marginBottom': '24px', 'padding': '0 20px'}),
                    
                    # Estadísticas clave
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.Small("Tasa Proyectada", 
                                          style={'color': COLORS['text_muted'], 
                                                'fontSize': '12px', 'display': 'block'}),
                                html.H4(f"{tasa_proyectada:.2f}", 
                                       style={'color': color_nivel, 'fontWeight': '700', 
                                             'marginTop': '8px', 'marginBottom': '4px'}),
                                html.Small("por 100k hab.", 
                                          style={'color': COLORS['text_muted'], 'fontSize': '11px'})
                            ], className="text-center")
                        ], md=4),
                        dbc.Col([
                            html.Div([
                                html.Small("Categorías de Acción", 
                                          style={'color': COLORS['text_muted'], 
                                                'fontSize': '12px', 'display': 'block'}),
                                html.H4(f"{len(recs_base['acciones']) + len(recomendaciones_adicionales)}", 
                                       style={'color': COLORS['primary'], 'fontWeight': '700', 
                                             'marginTop': '8px', 'marginBottom': '4px'}),
                                html.Small("áreas de intervención", 
                                          style={'color': COLORS['text_muted'], 'fontSize': '11px'})
                            ], className="text-center")
                        ], md=4),
                        dbc.Col([
                            html.Div([
                                html.Small("Acciones Sugeridas", 
                                          style={'color': COLORS['text_muted'], 
                                                'fontSize': '12px', 'display': 'block'}),
                                html.H4(f"{sum(len(cat['items']) for cat in recs_base['acciones'])}", 
                                       style={'color': COLORS['secondary'], 'fontWeight': '700', 
                                             'marginTop': '8px', 'marginBottom': '4px'}),
                                html.Small("recomendaciones", 
                                          style={'color': COLORS['text_muted'], 'fontSize': '11px'})
                            ], className="text-center")
                        ], md=4)
                    ], className="mb-3")
                ])
            ], style={'padding': '32px'})
        ], className="shadow-sm mb-4", style={'borderRadius': '16px'}),
        
        # Cards de recomendaciones por categoría
        html.Div([
            create_categoria_card(cat) for cat in recs_base['acciones']
        ]),
        
        # Recomendaciones adicionales específicas
        html.Div([
            create_recomendacion_adicional_card(rec) for rec in recomendaciones_adicionales
        ]) if recomendaciones_adicionales else html.Div(),
        
        # Card de recursos y contactos
        dbc.Card([
            dbc.CardBody([
                html.H5([
                    html.I(className="bi bi-telephone-fill me-2", 
                          style={'color': COLORS['primary']}),
                    "Recursos y Líneas de Contacto"
                ], style={'color': COLORS['text'], 'fontWeight': '600', 
                         'marginBottom': '20px'}),
                
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.I(className="bi bi-shield-fill-check", 
                                  style={'fontSize': '24px', 'color': COLORS['primary']}),
                            html.H6("ICBF", className="mt-2", 
                                   style={'fontSize': '14px', 'fontWeight': '600'}),
                            html.P("Línea 141", style={'fontSize': '13px', 'color': COLORS['neutral'], 
                                                       'marginBottom': '4px'}),
                            html.Small("Atención 24/7", style={'fontSize': '11px', 
                                                               'color': COLORS['text_muted']})
                        ], className="text-center p-3", 
                           style={'backgroundColor': COLORS['bg'], 'borderRadius': '12px'})
                    ], md=3, className="mb-3"),
                    
                    dbc.Col([
                        html.Div([
                            html.I(className="bi bi-hospital", 
                                  style={'fontSize': '24px', 'color': COLORS['danger']}),
                            html.H6("Emergencias", className="mt-2", 
                                   style={'fontSize': '14px', 'fontWeight': '600'}),
                            html.P("Línea 123", style={'fontSize': '13px', 'color': COLORS['neutral'], 
                                                       'marginBottom': '4px'}),
                            html.Small("Nacional", style={'fontSize': '11px', 
                                                         'color': COLORS['text_muted']})
                        ], className="text-center p-3", 
                           style={'backgroundColor': COLORS['bg'], 'borderRadius': '12px'})
                    ], md=3, className="mb-3"),
                    
                    dbc.Col([
                        html.Div([
                            html.I(className="bi bi-heart-fill", 
                                  style={'fontSize': '24px', 'color': COLORS['secondary']}),
                            html.H6("Te Protejo", className="mt-2", 
                                   style={'fontSize': '14px', 'fontWeight': '600'}),
                            html.P("www.teprotejo.org", style={'fontSize': '13px', 
                                                               'color': COLORS['neutral'], 
                                                               'marginBottom': '4px'}),
                            html.Small("Denuncias online", style={'fontSize': '11px', 
                                                                  'color': COLORS['text_muted']})
                        ], className="text-center p-3", 
                           style={'backgroundColor': COLORS['bg'], 'borderRadius': '12px'})
                    ], md=3, className="mb-3"),
                    
                    dbc.Col([
                        html.Div([
                            html.I(className="bi bi-people-fill", 
                                  style={'fontSize': '24px', 'color': COLORS['info']}),
                            html.H6("Comisaría", className="mt-2", 
                                   style={'fontSize': '14px', 'fontWeight': '600'}),
                            html.P("Local", style={'fontSize': '13px', 'color': COLORS['neutral'], 
                                                  'marginBottom': '4px'}),
                            html.Small("Familia y protección", style={'fontSize': '11px', 
                                                                      'color': COLORS['text_muted']})
                        ], className="text-center p-3", 
                           style={'backgroundColor': COLORS['bg'], 'borderRadius': '12px'})
                    ], md=3, className="mb-3")
                ])
            ], style={'padding': '28px'})
        ], className="shadow-sm mt-4", style={'borderRadius': '16px'}),
        
        # Botón de descarga
        html.Div([
            dbc.Button(
                [
                    html.I(className="bi bi-file-pdf me-2"),
                    "Descargar Recomendaciones en PDF"
                ],
                id="btn-download-recomendaciones",
                color="success",
                size="lg",
                className="w-100",
                outline=True,
                style={'fontWeight': '600', 'padding': '14px'}
            )
        ], className="mt-4")
    ])
    
    return content


def create_categoria_card(categoria):
    """Crear card para una categoría de recomendaciones"""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"{categoria['icon']} me-3", 
                      style={'fontSize': '28px', 'color': categoria['color']}),
                html.H5(categoria['categoria'], className="d-inline-block mb-0",
                       style={'color': COLORS['text'], 'fontWeight': '600', 
                             'verticalAlign': 'middle'})
            ], className="mb-4"),
            
            html.Ul([
                html.Li(item, style={'fontSize': '14px', 'color': COLORS['neutral'], 
                                    'lineHeight': '1.8', 'marginBottom': '12px'})
                for item in categoria['items']
            ], style={'paddingLeft': '20px', 'marginBottom': '0'})
        ], style={'padding': '24px'})
    ], className="shadow-sm mb-3", 
       style={'borderRadius': '16px', 'borderLeft': f"4px solid {categoria['color']}"})


def create_recomendacion_adicional_card(rec):
    """Crear card para recomendación adicional específica"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Alert([
                html.I(className=f"{rec['icon']} me-2", style={'fontSize': '20px'}),
                html.Strong(rec['titulo'])
            ], color=rec['color'].replace('#', ''), className="mb-3",
               style={'fontSize': '14px', 'fontWeight': '500'}),
            
            html.Ul([
                html.Li(item, style={'fontSize': '14px', 'color': COLORS['neutral'], 
                                    'lineHeight': '1.8', 'marginBottom': '10px'})
                for item in rec['items']
            ], style={'paddingLeft': '20px', 'marginBottom': '0'})
        ], style={'padding': '24px'})
    ], className="shadow-sm mb-3", style={'borderRadius': '16px'})