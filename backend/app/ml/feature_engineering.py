"""
Feature Engineering para predicciones en tiempo real
Replica exactamente el proceso de /data/src/feature_engineering.py
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.database_models import TeacherReport, WitnessReport, Student

# Constantes (mismo que en training)
VENTANAS = [3, 10, 30]


def calcular_features_estudiante(
    db: Session,
    student_id: int,
    fecha_reporte: date
) -> pd.DataFrame:
    """
    Calcula las features para un estudiante en una fecha específica.
    Replica exactamente el feature engineering usado en el entrenamiento.

    Args:
        db: Sesión de base de datos
        student_id: ID del estudiante
        fecha_reporte: Fecha del reporte (normalmente hoy)

    Returns:
        DataFrame con UNA fila conteniendo todas las features calculadas
    """

    # 1. Obtener datos de los últimos 30 días
    fecha_inicio = fecha_reporte - timedelta(days=30)

    # Obtener clase del estudiante
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError(f"Estudiante {student_id} no encontrado")

    clase_id = student.class_id

    # 1.1 Reportes de profesores del estudiante
    reportes_prof = db.query(TeacherReport).filter(
        TeacherReport.student_id == student_id,
        TeacherReport.date >= fecha_inicio,
        TeacherReport.date <= fecha_reporte
    ).all()

    if not reportes_prof:
        # Si no hay reportes, retornar features vacías (ceros)
        return _crear_features_vacias(student_id, fecha_reporte)

    # Convertir a DataFrame con mapeo de columnas
    df_prof = pd.DataFrame([{
        'fecha': r.date,
        'alumno_id': r.student_id,
        'soc_aisl': r.social_isolation,
        'soc_excl': r.peer_exclusion,
        'con_reac': r.emotional_reactivity,
        'con_inhib': r.inhibition,
        'diseng': r.disengagement,
        'fis_mat': r.physical_damage,
        'intuicion': r.intuition,
        'colegio_id': 1,  # Asumimos un colegio por ahora
        'clase_id': clase_id
    } for r in reportes_prof])

    df_prof['fecha'] = pd.to_datetime(df_prof['fecha'])

    # 1.2 Reportes de testigos de la clase (si hay)
    reportes_testigos = []
    if clase_id:
        reportes_testigos = db.query(WitnessReport).filter(
            WitnessReport.class_id == clase_id,
            WitnessReport.date >= fecha_inicio,
            WitnessReport.date <= fecha_reporte
        ).all()

    if reportes_testigos:
        df_testigos = pd.DataFrame([{
            'fecha': r.date,
            'clase_reportada': r.class_id
        } for r in reportes_testigos])
        df_testigos['fecha'] = pd.to_datetime(df_testigos['fecha'])
    else:
        df_testigos = pd.DataFrame(columns=['fecha', 'clase_reportada'])

    # 2. Procesando testigos y densidad (IGUAL QUE TRAINING)
    if not df_testigos.empty:
        df_testigos_agg = df_testigos.groupby(['fecha', 'clase_reportada']).size().reset_index(name='n_reportes_testigos')
    else:
        df_testigos_agg = pd.DataFrame(columns=['fecha', 'clase_reportada', 'n_reportes_testigos'])

    cols_sintomas = ['soc_aisl', 'soc_excl', 'con_reac', 'con_inhib', 'diseng', 'fis_mat']
    df_prof['suma_puntos_dia'] = df_prof[cols_sintomas].sum(axis=1)
    df_prof['reporto_algo'] = (df_prof['suma_puntos_dia'] > 0).astype(int)

    # 3. Comprimiendo (IGUAL QUE TRAINING)
    agg_funcs = {
        'soc_aisl': 'max', 'soc_excl': 'max', 'con_reac': 'max', 'con_inhib': 'max',
        'diseng': 'max', 'fis_mat': 'max', 'intuicion': 'mean',
        'reporto_algo': 'sum', 'suma_puntos_dia': 'sum',
        'colegio_id': 'first', 'clase_id': 'first'
    }
    df_daily = df_prof.groupby(['fecha', 'alumno_id']).agg(agg_funcs).reset_index()
    df_daily.rename(columns={'reporto_algo': 'n_profesores_alertados', 'suma_puntos_dia': 'intensidad_diaria_total'}, inplace=True)
    df_daily = df_daily.sort_values(by=['alumno_id', 'fecha'])

    # 4. Cruzando (IGUAL QUE TRAINING)
    if not df_testigos_agg.empty:
        df_daily = pd.merge(df_daily, df_testigos_agg, left_on=['fecha', 'clase_id'], right_on=['fecha', 'clase_reportada'], how='left')
        df_daily.drop(columns=['clase_reportada'], inplace=True, errors='ignore')
    else:
        df_daily['n_reportes_testigos'] = 0

    df_daily['n_reportes_testigos'] = df_daily['n_reportes_testigos'].fillna(0)

    # 5. Calculando ventanas (IGUAL QUE TRAINING)
    metricas_todas = ['soc_aisl', 'soc_excl', 'con_reac', 'con_inhib', 'diseng', 'fis_mat', 'intuicion', 'n_reportes_testigos', 'n_profesores_alertados', 'intensidad_diaria_total']
    metricas_largo_plazo = ['soc_aisl', 'soc_excl', 'con_reac', 'con_inhib', 'diseng', 'fis_mat', 'intensidad_diaria_total']

    def calcular_rolling(grupo_alumno):
        grupo_alumno = grupo_alumno.sort_values('fecha').set_index('fecha')
        features_nuevas = pd.DataFrame(index=grupo_alumno.index)

        for ventana in VENTANAS:
            if ventana == 30:
                cols_to_roll = metricas_largo_plazo
            else:
                cols_to_roll = metricas_todas

            # Media
            roll_mean = grupo_alumno[cols_to_roll].rolling(window=f'{ventana}D', min_periods=1).mean()
            roll_mean.columns = [f'{col}_mean_{ventana}d' for col in cols_to_roll]

            # Max (Solo síntomas)
            cols_max = [c for c in cols_to_roll if c in cols_sintomas]
            if cols_max:
                roll_max = grupo_alumno[cols_max].rolling(window=f'{ventana}D', min_periods=1).max()
                roll_max.columns = [f'{col}_max_{ventana}d' for col in cols_max]

            # Sumas para ventanas 3 y 10
            if ventana in [3, 10]:
                cols_sum = [c for c in ['n_reportes_testigos', 'n_profesores_alertados'] if c in cols_to_roll]
                if cols_sum:
                    roll_sum = grupo_alumno[cols_sum].rolling(window=f'{ventana}D', min_periods=1).sum()
                    roll_sum.columns = [f'{col}_sum_{ventana}d' for col in cols_sum]
                    features_nuevas = pd.concat([features_nuevas, roll_mean, roll_max, roll_sum], axis=1)
                else:
                    features_nuevas = pd.concat([features_nuevas, roll_mean, roll_max], axis=1)
            else:
                features_nuevas = pd.concat([features_nuevas, roll_mean, roll_max], axis=1)

        # Volatilidad 30d
        roll_std = grupo_alumno[metricas_largo_plazo].rolling(window='30D', min_periods=5).std().fillna(0)
        roll_std.columns = [f'{col}_std_30d' for col in metricas_largo_plazo]
        features_nuevas = pd.concat([features_nuevas, roll_std], axis=1)
        return pd.concat([grupo_alumno, features_nuevas], axis=1)

    df_final = df_daily.groupby('alumno_id', group_keys=False).apply(calcular_rolling)
    df_final = df_final.reset_index()
    df_final = df_final.fillna(0)

    # 6. FEATURE ENGINEERING AVANZADO (INTERACCIONES) - IGUAL QUE TRAINING
    # A. Ratio de Discrepancia
    df_final['ratio_testigos_vs_profes'] = df_final['n_reportes_testigos_sum_10d'] / (df_final['n_profesores_alertados_sum_10d'] + 1)

    # B. Índice de Sufrimiento Silencioso
    df_final['indice_sufrimiento_silencioso'] = (df_final['con_inhib_mean_10d'] + df_final['soc_aisl_mean_10d']) * (df_final['intuicion_mean_10d'] + 0.5)

    # C. Índice de Rebeldía
    df_final['indice_rebeldia'] = df_final['diseng_mean_30d'] - (df_final['n_reportes_testigos_mean_10d'] + df_final['soc_aisl_mean_30d'])

    # D. Aceleración de Testigos
    df_final['aceleracion_testigos'] = df_final['n_reportes_testigos_sum_3d'] - (df_final['n_reportes_testigos_sum_10d'] / 3.3)

    # Deltas clásicos
    for col in metricas_todas:
        if col in metricas_largo_plazo:
            if f'{col}_mean_30d' in df_final.columns:
                df_final[f'{col}_delta_trend'] = df_final[f'{col}_mean_3d'] - df_final[f'{col}_mean_30d']
        elif 'intuicion' in col:
            df_final[f'{col}_delta_trend'] = df_final[f'{col}_mean_3d'] - df_final[f'{col}_mean_10d']

    # Filtrar solo la fecha del reporte
    df_result = df_final[df_final['fecha'] == pd.Timestamp(fecha_reporte)]

    if df_result.empty:
        return _crear_features_vacias(student_id, fecha_reporte)

    return df_result


def _crear_features_vacias(student_id: int, fecha: date) -> pd.DataFrame:
    """Crea un DataFrame con features en cero para casos sin datos históricos"""
    return pd.DataFrame([{
        'alumno_id': student_id,
        'fecha': pd.Timestamp(fecha),
        # Aquí irían todas las features en 0
        # Por simplicidad, retornamos un DataFrame vacío que será manejado por el predictor
    }])
