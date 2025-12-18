"""
Módulo de predicción de bullying usando el modelo entrenado
"""

import os
import pandas as pd
import xgboost as xgb
from datetime import date
from sqlalchemy.orm import Session
from typing import Dict, Optional
import logging

from app.ml.feature_engineering import calcular_features_estudiante
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

# Path al modelo (desde variable de entorno)
MODEL_PATH = settings.MODEL_PATH

# Umbral óptimo determinado durante el entrenamiento (optimizado para F2-score)
OPTIMAL_THRESHOLD = 0.7117

# Modelo global (se carga una sola vez)
_model = None


def cargar_modelo() -> Optional[xgb.XGBClassifier]:
    """
    Carga el modelo XGBoost desde disco.
    Retorna None si el modelo no existe aún.
    """
    global _model

    if _model is not None:
        return _model

    if not os.path.exists(MODEL_PATH):
        logger.warning(f"Modelo no encontrado en {MODEL_PATH}")
        return None

    try:
        _model = xgb.XGBClassifier()
        _model.load_model(MODEL_PATH)
        logger.info("Modelo de ML cargado exitosamente")
        return _model
    except Exception as e:
        logger.error(f"Error cargando modelo: {e}")
        return None


def predecir_bullying(
    db: Session,
    student_id: int,
    fecha_reporte: date
) -> Dict:
    """
    Realiza predicción de bullying para un estudiante en una fecha específica.

    Args:
        db: Sesión de base de datos
        student_id: ID del estudiante
        fecha_reporte: Fecha del reporte

    Returns:
        Dict con:
            - bullying_probability: float (0-1)
            - is_alert: bool
            - risk_factors: Dict con las principales features contribuyentes
    """

    # 1. Calcular features
    try:
        df_features = calcular_features_estudiante(db, student_id, fecha_reporte)
    except Exception as e:
        logger.error(f"Error calculando features para estudiante {student_id}: {e}")
        # Retornar predicción neutra en caso de error
        return {
            "bullying_probability": 0.0,
            "is_alert": False,
            "risk_factors": {"error": str(e)}
        }

    # Si no hay datos, retornar predicción neutra
    if df_features.empty or len(df_features) == 0:
        logger.warning(f"No hay features disponibles para estudiante {student_id}")
        return {
            "bullying_probability": 0.0,
            "is_alert": False,
            "risk_factors": {"message": "Sin datos históricos suficientes"}
        }

    # 2. Cargar modelo
    modelo = cargar_modelo()

    if modelo is None:
        error_msg = f"CRÍTICO: Modelo ML no encontrado en {MODEL_PATH}. No se puede realizar predicción."
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    # 3. Preparar features para predicción
    # Excluir columnas no necesarias para el modelo
    cols_a_excluir = ['fecha', 'alumno_id', 'colegio_id', 'clase_id']

    # Filtrar columnas que existen en el DataFrame
    cols_a_excluir_existentes = [col for col in cols_a_excluir if col in df_features.columns]

    X = df_features.drop(columns=cols_a_excluir_existentes, errors='ignore')

    # Excluir también cualquier columna meta_ o intuicion_mean_30d/n_reportes_testigos_mean_30d
    # (según el código de entrenamiento)
    cols_trampa = [c for c in X.columns if 'meta_' in c]
    cols_prohibidas = [c for c in X.columns if 'intuicion_mean_30d' in c or 'n_reportes_testigos_mean_30d' in c]

    X = X.drop(columns=cols_trampa + cols_prohibidas, errors='ignore')

    # 4. Realizar predicción
    try:
        probabilidad = modelo.predict_proba(X)[0, 1]  # Probabilidad de clase positiva
        is_alert = probabilidad >= OPTIMAL_THRESHOLD

        # 5. Identificar factores de riesgo principales
        risk_factors = _identificar_factores_riesgo(X, modelo)

        return {
            "bullying_probability": float(probabilidad),
            "is_alert": bool(is_alert),
            "risk_factors": risk_factors
        }

    except Exception as e:
        logger.error(f"Error durante predicción: {e}")
        return {
            "bullying_probability": 0.0,
            "is_alert": False,
            "risk_factors": {"error": str(e)}
        }


def _identificar_factores_riesgo(X: pd.DataFrame, modelo: xgb.XGBClassifier) -> Dict:
    """
    Identifica las principales features que contribuyen a la predicción.
    """
    try:
        # Obtener importancia de features
        importances = modelo.feature_importances_
        feature_names = X.columns

        # Crear DataFrame de importancias
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)

        # Tomar top 5 features más importantes
        top_features = importance_df.head(5)

        # Crear diccionario de factores de riesgo
        risk_factors = {}
        for _, row in top_features.iterrows():
            feature = row['feature']
            importance = row['importance']
            valor = X[feature].iloc[0]

            risk_factors[feature] = {
                "value": float(valor) if pd.notna(valor) else 0.0,
                "importance": float(importance)
            }

        return risk_factors

    except Exception as e:
        logger.error(f"Error identificando factores de riesgo: {e}")
        return {}
