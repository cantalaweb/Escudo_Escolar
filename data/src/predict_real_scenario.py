import pandas as pd
import numpy as np
import xgboost as xgb
import os
import random
import string
from datetime import date, timedelta
import warnings

# Ignorar warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# ==========================================
# CONFIGURACIÓN DEL COLEGIO "REAL"
# ==========================================
MODEL_PATH = './models/bullying_detection_model.json'
UMBRAL_DECISION = 0.7117  # Umbral optimizado F2

# Escenario pequeño y de baja incidencia
N_COLEGIOS = 1
N_CLASES_POR_CURSO = 2   
ALUMNOS_POR_CLASE = 25   
INCIDENCIA_REAL = 20     # 2% (Incidencia realista)

# ==========================================
# 1. GENERADOR (Versión Compacta para Inferencia)
# ==========================================
class SimuladorColegioReal:
    def __init__(self):
        self.alumnos = []
        self.profesores = []
        self.data_reportes = []
        self.casos_reales = [] 
        
        self.cursos = ['Primaria 4', 'Primaria 5', 'Primaria 6', 'ESO 1', 'ESO 2', 'ESO 3', 'ESO 4']
        self.asignaturas = ['Mates', 'Lengua', 'Inglés', 'EF', 'Sociales']
        # Simulamos 60 días
        self.fechas = [date(2025,9,1) + timedelta(days=i) for i in range(60)]

    def generar_datos(self):
        print(f"--- Generando Colegio Simulado (Incidencia {INCIDENCIA_REAL/10}%) ---")
        
        id_counter = 0
        for curso in self.cursos:
            for letra in ['A', 'B']:
                clase_id = f"{curso} {letra}"
                # Profesores
                for asig in self.asignaturas:
                    self.profesores.append({'id': f"P_{asig}_{curso}", 'sens': np.random.normal(-1.0, 0.8)})
                
                # Alumnos
                for _ in range(ALUMNOS_POR_CLASE):
                    id_counter += 1
                    es_victima = random.random() < (INCIDENCIA_REAL / 1000)
                    self.alumnos.append({
                        'id': id_counter, 
                        'clase': clase_id, 
                        'es_victima': es_victima,
                        'perfil': random.choice(['Normativo', 'Inhibido'])
                    })
                    if es_victima: self.casos_reales.append(id_counter)

        print(f"Total Alumnos: {len(self.alumnos)}")
        print(f"Casos Reales de Bullying escondidos: {len(self.casos_reales)}")
        
        # Simulación Día a Día
        for fecha in self.fechas:
            if fecha.weekday() > 4: continue # Finde
            
            for alumno in self.alumnos:
                sintomas = {'soc_aisl':0, 'con_inhib':0, 'diseng':0, 'testigos':0, 'intuicion':0}
                
                if alumno['es_victima']:
                    # Bullying activo
                    base = random.gauss(1.5, 0.8)
                    if base < 0: base = 0
                    
                    if random.random() > 0.4: 
                        sintomas['soc_aisl'] = int(base)
                        sintomas['intuicion'] = int(base * 0.5)
                        if random.random() < 0.6: 
                            sintomas['testigos'] = random.randint(1, 3)
                
                else:
                    # Alumno normal (ruido)
                    if random.random() < 0.05: 
                        base = random.gauss(1.2, 0.5)
                        sintomas['con_inhib'] = int(base)
                        sintomas['intuicion'] = int(base * 0.4)

                # Generar filas
                if sum(sintomas.values()) > 0 or random.random() < 0.05:
                    self.data_reportes.append({
                        'fecha': fecha,
                        'alumno_id': alumno['id'],
                        'clase_id': alumno['clase'],
                        'soc_aisl': min(3, sintomas['soc_aisl']),
                        'soc_excl': 0, 'con_reac': 0,
                        'con_inhib': min(3, sintomas['con_inhib']),
                        'diseng': min(3, sintomas['diseng']),
                        'fis_mat': 0,
                        'intuicion': min(3, sintomas['intuicion']),
                        'is_bullying_active': 1 if alumno['es_victima'] else 0 
                    })
                    
                # Fila Testigos
                if sintomas['testigos'] > 0:
                    for _ in range(sintomas['testigos']):
                        self.data_reportes.append({
                            'fecha': fecha,
                            'tipo_row': 'testigo',
                            'clase_reportada': alumno['clase'],
                            'alumno_asociado_simulacion': alumno['id']
                        })

        return pd.DataFrame([d for d in self.data_reportes if 'tipo_row' not in d]), \
               pd.DataFrame([d for d in self.data_reportes if 'tipo_row' in d])

# ==========================================
# 2. PROCESADOR (Feature Engineering)
# ==========================================
def procesar_datos(df_prof, df_testigos):
    print("--- Procesando datos del colegio ---")
    
    # --- CORRECCIÓN CRÍTICA AQUÍ ---
    # Convertimos a datetime explícitamente para que .rolling('3D') funcione
    df_prof['fecha'] = pd.to_datetime(df_prof['fecha'])
    df_testigos['fecha'] = pd.to_datetime(df_testigos['fecha'])
    # -------------------------------
    
    # 1. Agregación de testigos
    testigos_agg = df_testigos.groupby(['fecha', 'alumno_asociado_simulacion']).size().reset_index(name='n_reportes_testigos')
    
    # 2. Métricas densidad
    cols_sintomas = ['soc_aisl', 'con_inhib', 'diseng']
    df_prof['suma_puntos_dia'] = df_prof[cols_sintomas].sum(axis=1)
    df_prof['reporto_algo'] = (df_prof['suma_puntos_dia'] > 0).astype(int)
    
    # 3. Compresión diaria
    df_daily = df_prof.groupby(['fecha', 'alumno_id']).agg({
        'soc_aisl': 'max', 'con_inhib': 'max', 'diseng': 'max', 'intuicion': 'mean',
        'reporto_algo': 'sum', 'suma_puntos_dia': 'sum', 'is_bullying_active': 'max'
    }).reset_index()
    
    # 4. Merge Testigos
    df_daily = pd.merge(df_daily, testigos_agg, left_on=['fecha', 'alumno_id'], right_on=['fecha', 'alumno_asociado_simulacion'], how='left').fillna(0)
    
    # Rellenar columnas faltantes (simulación simplificada)
    cols_missing = ['soc_excl', 'con_reac', 'fis_mat']
    for c in cols_missing: df_daily[c] = 0
    
    df_daily.rename(columns={'reporto_algo': 'n_profesores_alertados', 'suma_puntos_dia': 'intensidad_diaria_total'}, inplace=True)
    
    # 5. Rolling Windows & Features
    metricas = ['soc_aisl', 'soc_excl', 'con_reac', 'con_inhib', 'diseng', 'fis_mat', 'intuicion', 'n_reportes_testigos', 'n_profesores_alertados', 'intensidad_diaria_total']
    
    df_final = df_daily.sort_values(['alumno_id', 'fecha']).set_index('fecha')
    results = []
    
    for uid, group in df_final.groupby('alumno_id'):
        feats = group.copy()
        for v in [3, 10, 30]:
            # Medias
            roll_mean = group[metricas].rolling(f'{v}D', min_periods=1).mean().add_suffix(f'_mean_{v}d')
            feats = pd.concat([feats, roll_mean], axis=1)
            # Sumas (eventos - solo 10d realmente necesario para smart features, pero generamos por consistencia)
            if v == 10:
                roll_sum = group[['n_reportes_testigos', 'n_profesores_alertados', 'intensidad_diaria_total']].rolling(f'{v}D', min_periods=1).sum().add_suffix(f'_sum_{v}d')
                feats = pd.concat([feats, roll_sum], axis=1)
            # También necesitamos suma 3d para la aceleración
            if v == 3:
                roll_sum_3 = group[['n_reportes_testigos']].rolling(f'{v}D', min_periods=1).sum().add_suffix(f'_sum_{v}d')
                feats = pd.concat([feats, roll_sum_3], axis=1)
            
            # Max (sintomas)
            cols_max_src = ['soc_aisl', 'soc_excl', 'con_reac', 'con_inhib', 'diseng', 'fis_mat']
            roll_max = group[cols_max_src].rolling(f'{v}D', min_periods=1).max().add_suffix(f'_max_{v}d')
            feats = pd.concat([feats, roll_max], axis=1)
            
        # Smart Features
        # Rellenamos nans por si acaso (aunque min_periods=1 ayuda)
        feats = feats.fillna(0)
        
        feats['ratio_testigos_vs_profes'] = feats['n_reportes_testigos_sum_10d'] / (feats['n_profesores_alertados_sum_10d'] + 1)
        feats['indice_sufrimiento_silencioso'] = (feats['con_inhib_mean_10d'] + feats['soc_aisl_mean_10d']) * (feats['intuicion_mean_10d'] + 0.5)
        feats['indice_rebeldia'] = feats['diseng_mean_30d'] - (feats['n_reportes_testigos_mean_10d'] + feats['soc_aisl_mean_30d'])
        feats['aceleracion_testigos'] = feats['n_reportes_testigos_sum_3d'] - (feats['n_reportes_testigos_sum_10d'] / 3.3)
        
        # Std 30d
        cols_std = ['soc_aisl', 'soc_excl', 'con_reac', 'con_inhib', 'diseng', 'fis_mat', 'intensidad_diaria_total']
        roll_std = group[cols_std].rolling('30D', min_periods=1).std().add_suffix('_std_30d').fillna(0)
        feats = pd.concat([feats, roll_std], axis=1)
        
        # Deltas
        for m in metricas:
            if m == 'intuicion':
                feats[f'{m}_delta_trend'] = feats[f'{m}_mean_3d'] - feats[f'{m}_mean_10d']
            elif f'{m}_mean_30d' in feats.columns:
                feats[f'{m}_delta_trend'] = feats[f'{m}_mean_3d'] - feats[f'{m}_mean_30d']
                
        results.append(feats.iloc[-1:]) # Nos quedamos con el ÚLTIMO DÍA

    return pd.concat(results).reset_index()

# ==========================================
# 3. MOTOR DE INFERENCIA
# ==========================================
def predecir():
    # 1. Generar
    sim = SimuladorColegioReal()
    df_raw, df_test = sim.generar_datos()
    
    # 2. Procesar
    df_ready = procesar_datos(df_raw, df_test)
    
    # 3. Cargar Modelo
    print("--- Cargando Modelo Inteligente ---")
    model = xgb.Booster()
    model.load_model(MODEL_PATH)
    
    feature_names = model.feature_names
    
    # Asegurar features
    for f in feature_names:
        if f not in df_ready.columns:
            df_ready[f] = 0
            
    dtest = xgb.DMatrix(df_ready[feature_names])
    
    # 4. Predecir
    probs = model.predict(dtest)
    
    # 5. Reportar
    df_ready['probabilidad_bullying'] = probs
    df_ready['prediccion'] = (probs >= UMBRAL_DECISION).astype(int)
    
    detectados = df_ready[df_ready['prediccion'] == 1]
    reales_perdidos = df_ready[(df_ready['is_bullying_active'] == 1) & (df_ready['prediccion'] == 0)]
    falsos_positivos = df_ready[(df_ready['is_bullying_active'] == 0) & (df_ready['prediccion'] == 1)]
    
    print("\n" + "="*50)
    print(f" INFORME DIARIO DE CONVIVENCIA - COLEGIO SIMULADO")
    print("="*50)
    print(f"Población Total: {len(df_ready)} alumnos")
    print(f"Incidencia Real (Oculta): {df_ready['is_bullying_active'].sum()} casos")
    print("-" * 30)
    print(f"ALERTA ROJA (Sistema): {len(detectados)} alumnos identificados")
    print(f" > Casos Reales Detectados: {len(detectados) - len(falsos_positivos)}")
    print(f" > Falsas Alarmas (Revisión): {len(falsos_positivos)}")
    print("-" * 30)
    print(f"FALSOS NEGATIVOS (Peligro): {len(reales_perdidos)}")
    
    if not reales_perdidos.empty:
        print("\n[ANÁLISIS DE CASOS PERDIDOS]")
        cols_show = ['alumno_id', 'probabilidad_bullying', 'soc_aisl_mean_30d', 'n_reportes_testigos_sum_10d', 'ratio_testigos_vs_profes']
        # Aseguramos que las columnas existen antes de imprimir
        cols_existentes = [c for c in cols_show if c in reales_perdidos.columns]
        print(reales_perdidos[cols_existentes])
    else:
        print("\n¡ÉXITO! Ningún caso real ha pasado desapercibido.")

if __name__ == "__main__":
    predecir()
