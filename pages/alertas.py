from dash import html, dcc, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from config import COLORS, COLORS_ALPHA, DEPARTAMENTOS

def create_alertas_bar_chart(data):
    data_sorted = data.nlargest(10, 'Tasa_Proyectada')
    colors_map = {'Crítico': COLORS['danger'], 'Alto': COLORS['warning'], 'Medio': COLORS['info'], 'Bajo': COLORS['secondary']}
    bar_colors = [colors_map.get(nivel, COLORS['neutral']) for nivel in data_sorted['Nivel_Alerta']]
    
    fig = go.Figure(data=[go.Bar(
        x=data_sorted['Tasa_Proyectada'],
        y=data_sorted['Municipio'] + ' - ' + data_sorted['Departamento'],
        orientation='h',
        marker=dict(color=bar_colors, line=dict(color='white', width=1)),
        text=data_sorted['Tasa_Proyectada'].round(1),
        textposition='auto',
        texttemplate='%{text} /100k',
        hovertemplate='<b>%{y}</b><br>Tasa: %{x:.2f} por 100k hab.<br>Nivel: %{customdata}<extra></extra>',
        customdata=data_sorted['Nivel_Alerta']
    )])
    fig.update_layout(xaxis_title='Tasa Proyectada por 100,000 habitantes', yaxis_title='', plot_bgcolor='rgba(248, 250, 252, 0.5)', paper_bgcolor='rgba(0,0,0,0)', font={'family': 'Inter, sans-serif', 'color': COLORS['neutral']}, height=400, margin=dict(l=20, r=20, t=20, b=40), xaxis=dict(gridcolor=COLORS['border'], showgrid=True), yaxis=dict(autorange='reversed'))
    return fig

def create_alertas_table(data):
    badge_colors = {'Crítico': ('danger', 'bi-exclamation-octagon-fill'), 'Alto': ('warning', 'bi-exclamation-triangle-fill'), 'Medio': ('info', 'bi-exclamation-circle-fill'), 'Bajo': ('success', 'bi-check-circle-fill')}
    rows = []
    for idx, row in data.iterrows():
        badge_color, badge_icon = badge_colors.get(row['Nivel_Alerta'], ('secondary', 'bi-circle'))
        rows.append(html.Tr([
            html.Td(row['Municipio'], style={'fontWeight': '500', 'color': COLORS['text'], 'fontSize': '14px'}),
            html.Td(row['Departamento'], style={'color': COLORS['neutral'], 'fontSize': '14px'}),
            html.Td(f"{row['Tasa_Proyectada']:.1f}", style={'fontWeight': '600', 'color': COLORS['text'], 'fontSize': '14px'}),
            html.Td(f"Cluster {row['Cluster']}", style={'color': COLORS['neutral'], 'fontSize': '14px'}),
            html.Td(dbc.Badge([html.I(className=f"{badge_icon} me-1"), row['Nivel_Alerta']], color=badge_color, pill=True, style={'fontSize': '12px', 'fontWeight': '500', 'padding': '6px 12px'}), style={'textAlign': 'center'}),
            html.Td(f"{row['Poblacion_Menores']:,}", style={'color': COLORS['neutral'], 'fontSize': '14px'}),
            html.Td(dbc.Button(html.I(className="bi bi-eye"), id={'type': 'view-detail', 'index': idx}, color="primary", size="sm", outline=True, style={'padding': '4px 12px'}), style={'textAlign': 'center'})
        ], style={'borderBottom': f'1px solid {COLORS["border"]}'}))
    
    return html.Table([
        html.Thead(html.Tr([html.Th(c, style={'fontWeight': '600', 'fontSize': '13px', 'color': COLORS['text'], 'padding': '12px', 'borderBottom': f'2px solid {COLORS["border"]}'}) for c in ["Municipio", "Departamento", "Tasa /100k", "Cluster", "Nivel Alerta", "Población <18", "Acciones"]])),
        html.Tbody(rows)
    ], style={'width': '100%', 'borderCollapse': 'collapse'}, className="table-hover")

def create_alertas_module():
    alertas_data = pd.DataFrame({
        'Municipio': ['Cartagena', 'Barranquilla', 'Santa Marta', 'Magangué', 'Turbaco', 'Soledad', 'Malambo', 'Ciénaga', 'Sabanalarga', 'Baranoa'],
        'Departamento': ['Bolívar', 'Atlántico', 'Magdalena', 'Bolívar', 'Bolívar', 'Atlántico', 'Atlántico', 'Magdalena', 'Atlántico', 'Atlántico'],
        'Tasa_Proyectada': [45.2, 38.7, 32.1, 51.3, 28.4, 41.8, 35.2, 29.7, 33.5, 27.8],
        'Cluster': [2, 2, 1, 3, 1, 2, 2, 1, 2, 1],
        'Nivel_Alerta': ['Alto', 'Alto', 'Medio', 'Crítico', 'Medio', 'Alto', 'Alto', 'Medio', 'Alto', 'Medio'],
        'Poblacion_Menores': [185430, 234567, 98234, 45678, 23456, 156789, 87654, 56789, 34567, 28901]
    })
    
    return dbc.Container([
        dbc.Row([dbc.Col([html.Div([html.H2([html.I(className="bi bi-exclamation-triangle-fill me-3", style={'color': COLORS['danger']}), "Alertas Tempranas"], style={'fontWeight': '700', 'color': COLORS['text'], 'marginBottom': '8px'}), html.P("Identificación de municipios que requieren atención prioritaria", style={'color': COLORS['text_muted'], 'fontSize': '15px', 'marginBottom': '0'})])])], className="mb-4"),
        dbc.Row([
            dbc.Col([dbc.Card([dbc.CardBody([html.Div([html.I(className="bi bi-exclamation-octagon-fill", style={'fontSize': '32px', 'color': COLORS['danger']}), html.H3("24", className="mb-0 mt-2", style={'color': COLORS['danger'], 'fontWeight': '700', 'fontSize': '36px'}), html.P("Municipios Críticos", className="mb-0 mt-1", style={'color': COLORS['text_muted'], 'fontSize': '13px', 'fontWeight': '500'})], className="text-center")], style={'padding': '24px'})], className="shadow-sm stat-card", style={'borderRadius': '16px', 'borderLeftColor': COLORS['danger'], 'borderLeftWidth': '4px'})], md=3, className="mb-3"),
            dbc.Col([dbc.Card([dbc.CardBody([html.Div([html.I(className="bi bi-exclamation-triangle-fill", style={'fontSize': '32px', 'color': COLORS['warning']}), html.H3("48", className="mb-0 mt-2", style={'color': COLORS['warning'], 'fontWeight': '700', 'fontSize': '36px'}), html.P("Alerta Alta", className="mb-0 mt-1", style={'color': COLORS['text_muted'], 'fontSize': '13px', 'fontWeight': '500'})], className="text-center")], style={'padding': '24px'})], className="shadow-sm stat-card", style={'borderRadius': '16px', 'borderLeftColor': COLORS['warning'], 'borderLeftWidth': '4px'})], md=3, className="mb-3"),
            dbc.Col([dbc.Card([dbc.CardBody([html.Div([html.I(className="bi bi-exclamation-circle-fill", style={'fontSize': '32px', 'color': COLORS['info']}), html.H3("87", className="mb-0 mt-2", style={'color': COLORS['info'], 'fontWeight': '700', 'fontSize': '36px'}), html.P("Alerta Media", className="mb-0 mt-1", style={'color': COLORS['text_muted'], 'fontSize': '13px', 'fontWeight': '500'})], className="text-center")], style={'padding': '24px'})], className="shadow-sm stat-card", style={'borderRadius': '16px', 'borderLeftColor': COLORS['info'], 'borderLeftWidth': '4px'})], md=3, className="mb-3"),
            dbc.Col([dbc.Card([dbc.CardBody([html.Div([html.I(className="bi bi-check-circle-fill", style={'fontSize': '32px', 'color': COLORS['secondary']}), html.H3("163", className="mb-0 mt-2", style={'color': COLORS['secondary'], 'fontWeight': '700', 'fontSize': '36px'}), html.P("Bajo Riesgo", className="mb-0 mt-1", style={'color': COLORS['text_muted'], 'fontSize': '13px', 'fontWeight': '500'})], className="text-center")], style={'padding': '24px'})], className="shadow-sm stat-card", style={'borderRadius': '16px', 'borderLeftColor': COLORS['secondary'], 'borderLeftWidth': '4px'})], md=3, className="mb-3")
        ], className="mb-4"),
        dbc.Row([dbc.Col([dbc.Card([dbc.CardBody([html.H5([html.I(className="bi bi-bar-chart-fill me-2", style={'color': COLORS['danger']}), "Top 10 Municipios con Mayor Riesgo"], style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '20px'}), dcc.Graph(id="alertas-bar-chart", config={'displayModeBar': False}, figure=create_alertas_bar_chart(alertas_data))], style={'padding': '28px'})], className="shadow-sm", style={'borderRadius': '16px'})], md=12, className="mb-4")]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([html.H5([html.I(className="bi bi-table me-2", style={'color': COLORS['primary']}), "Tabla de Alertas Municipales"], style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '0', 'flex': '1'}), dbc.Button([html.I(className="bi bi-download me-2"), "Exportar CSV"], id="btn-export-alertas", color="success", size="sm", outline=True, style={'fontWeight': '500'})], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '24px'}),
                        dbc.Row([
                            dbc.Col([dbc.Label("Filtrar por Departamento"), dcc.Dropdown(id="filter-departamento", options=[{'label': 'Todos', 'value': 'all'}] + [{'label': d, 'value': d} for d in DEPARTAMENTOS], value='all', clearable=False)], md=4, className="mb-3"),
                            dbc.Col([dbc.Label("Filtrar por Nivel de Alerta"), dcc.Dropdown(id="filter-nivel", options=[{'label': 'Todos', 'value': 'all'}, {'label': 'Crítico', 'value': 'Crítico'}, {'label': 'Alto', 'value': 'Alto'}, {'label': 'Medio', 'value': 'Medio'}, {'label': 'Bajo', 'value': 'Bajo'}], value='all', clearable=False)], md=4, className="mb-3"),
                            dbc.Col([dbc.Label("Ordenar por"), dcc.Dropdown(id="sort-column", options=[{'label': 'Tasa Proyectada (Mayor a Menor)', 'value': 'tasa_desc'}, {'label': 'Tasa Proyectada (Menor a Mayor)', 'value': 'tasa_asc'}, {'label': 'Municipio (A-Z)', 'value': 'municipio_asc'}, {'label': 'Población Menores', 'value': 'poblacion_desc'}], value='tasa_desc', clearable=False)], md=4, className="mb-3")
                        ]),
                        html.Div(id="alertas-table-container", children=create_alertas_table(alertas_data), style={'maxHeight': '500px', 'overflowY': 'auto', 'marginTop': '20px'})
                    ], style={'padding': '28px'})
                ], className="shadow-sm", style={'borderRadius': '16px'})
            ])
        ]),
        # Modal para detalles
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Detalle de Alerta"), close_button=True),
            html.Div(id='modal-detalle-alerta-content')
        ], id='modal-detalle-alerta', size='lg', is_open=False)
    ], fluid=True, style={'maxWidth': '1600px'})