from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import joblib
import numpy as np

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
app = FastAPI(
    title="API – Predicción con CatBoost y Clustering con KMeans",
    description=(
        "API para:\n"
        "1) Predicción con modelo CatBoost.\n"
        "2) Asignación de cluster con modelo KMeans (requiere scaler).\n\n"
        "Asegúrate de enviar las características en el mismo orden que se usó para entrenar KMeans."
    ),
    version="2.0.1"
)

# ============================================================
# FUNCIÓN PARA CARGA SEGURA DE MODELOS
# ============================================================
def cargar_modelo(path: str):
    """
    Carga un objeto guardado con joblib. Devuelve None si falla.
    """
    try:
        return joblib.load(path)
    except Exception as e:
        print(f"[ERROR] No se pudo cargar {path}: {e}")
        return None


# ============================================================
# CARGA DE MODELOS
# ============================================================
modelo_catboost = cargar_modelo("modelo_catboost.joblib")
modelo_kmeans = cargar_modelo("kmeans_model.pkl")
scaler = cargar_modelo("scaler.pkl")  # Obligatorio para transformar entradas del KMeans


# ============================================================
# ESTRUCTURA DE ENTRADA PARA CATBOOST
# ============================================================
class CatBoostInput(BaseModel):
    """
    Estructura esperada por el modelo CatBoost.
    Las variables deben coincidir exactamente con las usadas durante el entrenamiento.
    """
    poblacion_menores: float
    porc_poblacion_urbana: float
    porc_poblacion_rural: float
    ipm: float
    cobertura_acueducto: float
    cobertura_alcantarillado: float
    cobertura_energia: float
    pib_per_capita: float
    tasa_homicidio: float
    sexo_victima: str
    grupo_edad_victima: str
    ciclo_vital: str
    escolaridad: str
    depto_hecho_dane: str


# ============================================================
# ENDPOINT DE PREDICCIÓN CON CATBOOST
# ============================================================
@app.post("/predict/catboost")
def predict_catboost(data: CatBoostInput):
    """
    Realiza predicción usando el modelo CatBoost cargado.
    """
    if modelo_catboost is None:
        raise HTTPException(status_code=500, detail="Modelo CatBoost no cargado.")

    valores = [[
        data.poblacion_menores,
        data.porc_poblacion_urbana,
        data.porc_poblacion_rural,
        data.ipm,
        data.cobertura_acueducto,
        data.cobertura_alcantarillado,
        data.cobertura_energia,
        data.pib_per_capita,
        data.tasa_homicidio,
        data.sexo_victima,
        data.grupo_edad_victima,
        data.ciclo_vital,
        data.escolaridad,
        data.depto_hecho_dane
    ]]

    try:
        pred = modelo_catboost.predict(valores)[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción CatBoost: {e}")

    return {"prediccion": float(pred)}


# ============================================================
# ESTRUCTURA DE ENTRADA PARA KMEANS
# ============================================================
class KMeansInput(BaseModel):
    """
    Lista de valores numéricos en el mismo orden que las columnas
    usadas para entrenar el modelo KMeans (N = 6).
    """

    valores: List[float]


# ============================================================
# VARIABLES NUMÉRICAS (ORDEN ESPERADO POR KMEANS)
# ============================================================
# El modelo KMeans fue entrenado con 6 características numéricas.
# Debes enviar los valores exactamente en este orden:
#
# 1) tasa_x100mil
#    - Tasa de eventos (por ejemplo, tasa por 100.000 habitantes).
#
# 2) porcentaje_pobreza_proxy
#    - "Porcentaje de niñas, niños y adolescentes en pobreza (proxy)"
#
# 3) pib_per_capita
#    - Producto Interno Bruto per cápita (puede estar en pesos o la unidad usada).
#
# 4) tasa_homicidio_intencional_x100k
#    - Tasa de homicidio intencional por cada 100.000 habitantes.
#
# 5) desviacion_estandar_tasa
#    - Desviación estándar de la tasa (por municipio, calculada durante agregación).
#
# 6) mediana_tasa
#    - Mediana de la tasa (por municipio).
#
# Ejemplo de payload correcto:
# {
#   "valores": [28.068763, 64.79, 17168300, 649.0, 15.522718, 19.367427]
# }
#
# Nota: el scaler transformará estos valores antes de predecir el cluster.


# ============================================================
# ENDPOINT PARA CONSULTAR EL ORDEN DE VARIABLES DEL KMEANS
# ============================================================
@app.get("/kmeans/features")
def kmeans_features():
    """
    Devuelve el orden de columnas usado en el scaler (si está disponible).
    Útil para clientes que necesiten confirmar el orden exacto.
    """
    if scaler is None:
        raise HTTPException(status_code=500, detail="Scaler no cargado.")

    if hasattr(scaler, "feature_names_in_"):
        return {"features_order": scaler.feature_names_in_.tolist()}

    # Si no existe feature_names_in_, devolvemos la lista documentada arriba
    return {
        "features_order": [
            "tasa_x100mil",
            "porcentaje_pobreza_proxy",
            "pib_per_capita",
            "tasa_homicidio_intencional_x100k",
            "desviacion_estandar_tasa",
            "mediana_tasa"
        ],
        "note": "El scaler no tiene 'feature_names_in_'. Se devuelve el orden documentado."
    }


# ============================================================
# ENDPOINT DE PREDICCIÓN CON KMEANS
# ============================================================
@app.post("/predict/kmeans")
def predict_kmeans(data: KMeansInput):
    """
    Asigna un cluster usando scaler.transform(...) y modelo_kmeans.predict(...).
    Requiere exactamente 6 valores en el orden documentado.
    """
    if modelo_kmeans is None or scaler is None:
        raise HTTPException(
            status_code=500,
            detail="Modelo KMeans o scaler no cargados."
        )

    vector = np.array(data.valores).reshape(1, -1)

    # Validación del número de características
    expected = getattr(modelo_kmeans, "n_features_in_", None)
    if expected is None:
        # fallback: si el modelo no tiene n_features_in_, asumimos 6 (documentado)
        expected = 6

    if vector.shape[1] != expected:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Se esperaban {expected} valores, pero se enviaron {vector.shape[1]}. "
                "Consulta /kmeans/features para ver el orden correcto."
            )
        )

    try:
        vector_scaled = scaler.transform(vector)
        cluster = modelo_kmeans.predict(vector_scaled)[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción KMeans: {e}")

    return {"cluster_asignado": int(cluster)}


# ============================================================
# HEALTH CHECK
# ============================================================
@app.get("/health")
def health():
    """
    Verifica si los modelos fueron cargados correctamente.
    """
    return {
        "catboost_cargado": modelo_catboost is not None,
        "kmeans_cargado": modelo_kmeans is not None,
        "scaler_cargado": scaler is not None,
        "estado": "API funcionando correctamente"
    }
