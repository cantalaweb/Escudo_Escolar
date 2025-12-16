import pandas as pd
import numpy as np
import warnings
import os

warnings.simplefilter(action='ignore', category=FutureWarning)
os.makedirs('./data/processed', exist_ok=True)

VENTANAS = [3, 10, 30]

def feature_engineering():
    print("1. Cargando datos...")
    df_prof = pd.read_csv('./data/raw/dataset_bullying_profesores.csv')
    df_testigos = pd.read_csv('./data/raw/dataset_bullying_testigos.csv')

    df_prof['fecha'] = pd.to_datetime(df_prof['fecha'])
    df_testigos['fecha'] = pd.to_datetime(df_testigos['fecha'])

    print("2. Procesando testigos y densidad...")
    df_testigos_agg = df_testigos.groupby(['fecha', 'clase_reportada']).size().reset_index(name='n_reportes_testigos')

    cols_sintomas = ['soc_aisl', 'soc_excl', 'con_reac', 'con_inhib', 'diseng', 'fis_mat']
    df_prof['suma_puntos_dia'] = df_prof[cols_sintomas].sum(axis=1)
    df_prof['reporto_algo'] = (df_prof['suma_puntos_dia'] > 0).astype(int)

    print("3. Comprimiendo...")
    agg_funcs = {
        'soc_aisl': 'max', 'soc_excl': 'max', 'con_reac': 'max', 'con_inhib': 'max',
        'diseng': 'max', 'fis_mat': 'max', 'intuicion': 'mean',
        'reporto_algo': 'sum', 'suma_puntos_dia': 'sum',
        'is_bullying_active': 'max', 'colegio_id': 'first', 'clase_id': 'first'
    }
    df_daily = df_prof.groupby(['fecha', 'alumno_id']).agg(agg_funcs).reset_index()
    df_daily.rename(columns={'reporto_algo': 'n_profesores_alertados', 'suma_puntos_dia': 'intensidad_diaria_total'}, inplace=True)
    df_daily = df_daily.sort_values(by=['alumno_id', 'fecha'])

    print("4. Cruzando...")
    df_daily = pd.merge(df_daily, df_testigos_agg, left_on=['fecha', 'clase_id'], right_on=['fecha', 'clase_reportada'], how='left')
    df_daily['n_reportes_testigos'] = df_daily['n_reportes_testigos'].fillna(0)
    df_daily.drop(columns=['clase_reportada'], inplace=True)

    print("5. Calculando ventanas (Híbrido)...")
    
    metricas_todas = ['soc_aisl', 'soc_excl', 'con_reac', 'con_inhib', 'diseng', 'fis_mat', 'intuicion', 'n_reportes_testigos', 'n_profesores_alertados', 'intensidad_diaria_total']
    metricas_largo_plazo = ['soc_aisl', 'soc_excl', 'con_reac', 'con_inhib', 'diseng', 'fis_mat', 'intensidad_diaria_total']

    def calcular_rolling(grupo_alumno):
        grupo_alumno = grupo_alumno.sort_values('fecha').set_index('fecha')
        features_nuevas = pd.DataFrame(index=grupo_alumno.index)
        
        for ventana in VENTANAS:
            if ventana == 30: cols_to_roll = metricas_largo_plazo
            else: cols_to_roll = metricas_todas

            # Media
            roll_mean = grupo_alumno[cols_to_roll].rolling(window=f'{ventana}D', min_periods=1).mean()
            roll_mean.columns = [f'{col}_mean_{ventana}d' for col in cols_to_roll]
            
            # Max (Solo síntomas)
            cols_max = [c for c in cols_to_roll if c in cols_sintomas]
            if cols_max:
                roll_max = grupo_alumno[cols_max].rolling(window=f'{ventana}D', min_periods=1).max()
                roll_max.columns = [f'{col}_max_{ventana}d' for col in cols_max]
            
            # --- CORRECCIÓN AQUÍ ---
            # Permitimos Sumas para ventanas 3 y 10 (antes solo era 10)
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

    # ==============================================================================
    # 6. FEATURE ENGINEERING AVANZADO (INTERACCIONES)
    # ==============================================================================
    print("6. Creando Features de Interacción (Smart Features)...")
    
    # A. Ratio de Discrepancia
    df_final['ratio_testigos_vs_profes'] = df_final['n_reportes_testigos_sum_10d'] / (df_final['n_profesores_alertados_sum_10d'] + 1)
    
    # B. Índice de Sufrimiento Silencioso
    df_final['indice_sufrimiento_silencioso'] = (df_final['con_inhib_mean_10d'] + df_final['soc_aisl_mean_10d']) * (df_final['intuicion_mean_10d'] + 0.5)
    
    # C. Índice de Rebeldía
    df_final['indice_rebeldia'] = df_final['diseng_mean_30d'] - (df_final['n_reportes_testigos_mean_10d'] + df_final['soc_aisl_mean_30d'])

    # D. Aceleración de Testigos (AHORA SÍ EXISTE LA VARIABLE DE 3D)
    df_final['aceleracion_testigos'] = df_final['n_reportes_testigos_sum_3d'] - (df_final['n_reportes_testigos_sum_10d'] / 3.3)

    # Deltas clásicos
    for col in metricas_todas:
        if col in metricas_largo_plazo:
            if f'{col}_mean_30d' in df_final.columns:
                df_final[f'{col}_delta_trend'] = df_final[f'{col}_mean_3d'] - df_final[f'{col}_mean_30d']
        elif 'intuicion' in col:
             df_final[f'{col}_delta_trend'] = df_final[f'{col}_mean_3d'] - df_final[f'{col}_mean_10d']

    df_final.to_csv("./data/processed/dataset_training_bullying_enhanced.csv", index=False)
    print("¡Hecho! Smart Features añadidas correctamente.")

if __name__ == "__main__":
    feature_engineering()
