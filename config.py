import os

# API URL
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Paleta de colores
COLORS = {
    'primary': '#3b82f6', 'secondary': '#10b981', 'danger': '#ef4444',
    'warning': '#f59e0b', 'info': '#06b6d4', 'neutral': '#64748b',
    'bg': '#f8fafc', 'card': '#ffffff', 'border': '#e2e8f0',
    'text': '#1e293b', 'text_muted': '#94a3b8'
}

COLORS_ALPHA = {
    'primary_10': 'rgba(59, 130, 246, 0.1)',
    'secondary_10': 'rgba(16, 185, 129, 0.1)',
    'danger_10': 'rgba(239, 68, 68, 0.1)',
    'warning_10': 'rgba(245, 158, 11, 0.1)',
}

# Umbrales
UMBRALES_RIESGO = {'bajo': 15, 'medio': 30, 'alto': float('inf')}
UMBRALES_CLUSTER = {0: 'Bajo', 1: 'Medio', 2: 'Alto', 3: 'Crítico'}

# Opciones
SEXO_OPTIONS = ['F', 'M']
GRUPO_EDAD_OPTIONS = ['0-4', '5-9', '10-14', '15-17']
CICLO_VITAL_OPTIONS = ['primera_infancia', 'infancia', 'adolescencia']
ESCOLARIDAD_OPTIONS = ['sin_escolaridad', 'primaria_incompleta', 'primaria_completa', 
                       'secundaria_incompleta', 'secundaria_completa', 'tecnico', 'universitario']
DEPARTAMENTOS = ['Amazonas', 'Antioquia', 'Arauca', 'Atlántico', 'Bolívar', 'Boyacá', 
                 'Caldas', 'Caquetá', 'Casanare', 'Cauca', 'Cesar', 'Chocó', 'Córdoba',
                 'Cundinamarca', 'Guainía', 'Guaviare', 'Huila', 'La Guajira', 'Magdalena',
                 'Meta', 'Nariño', 'Norte de Santander', 'Putumayo', 'Quindío', 'Risaralda',
                 'San Andrés y Providencia', 'Santander', 'Sucre', 'Tolima', 'Valle del Cauca',
                 'Vaupés', 'Vichada']

