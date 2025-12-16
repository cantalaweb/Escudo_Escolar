import pandas as pd
import numpy as np
import random
import xgboost as xgb
from datetime import date, timedelta
import os
import warnings

# Ignorar warnings de pandas
warnings.simplefilter(action='ignore', category=FutureWarning)

# ==========================================
# 0. CONFIGURACIÓN Y DATOS MAESTROS
# ==========================================
OUTPUT_FILE = "insert_demo_data.sql"
MODEL_PATH = './models/bullying_detection_model.json'
UMBRAL_DECISION = 0.7117

FECHA_INICIO = date(2025, 9, 1)
FECHA_FIN = date(2025, 12, 18)

CURSOS = ['Primaria 4', 'Primaria 5', 'Primaria 6', 'ESO 1', 'ESO 2', 'ESO 3', 'ESO 4', 'Bachillerato 1', 'Bachillerato 2']
LETRAS = ['A', 'B']

# LISTA COMPLETA
ASIGNATURAS_ACADEMICAS = ['Matemáticas', 'Lengua', 'Inglés', 'Biología', 'Geografía e Historia', 'Física y Química', 'Plástica', 'Música', 'Tecnología', 'Filosofía', 'Economía']
ASIG_EF = 'Educación Física'
ASIG_RECREO = 'Recreo'
ASIG_COMEDOR = 'Comedor'
TODAS_ASIGNATURAS = ASIGNATURAS_ACADEMICAS + [ASIG_EF, ASIG_RECREO, ASIG_COMEDOR]

NOMBRES = ["Hugo", "Mateo", "Martin", "Lucas", "Leo", "Daniel", "Alejandro", "Manuel", "Pablo", "Alvaro", "Adrian", "Enzo", "Mario", "Diego", "David", "Oliver", "Marcos", "Thiago", "Marco", "Alex", "Javier", "Izan", "Bruno", "Miguel", "Antonio", "Gonzalo", "Liam", "Gael", "Marc", "Carlos", "Juan", "Angel", "Dylan", "Nicolas", "Jose", "Sergio", "Gabriel", "Luca", "Jorge", "Dario", "Lucia", "Sofia", "Martina", "Maria", "Julia", "Paula", "Valeria", "Emma", "Daniela", "Carla", "Alma", "Olivia", "Sara", "Carmen", "Vega", "Mia", "Lara", "Alba", "Noa", "Lola", "Valentina", "Chloe", "Claudia", "Jimena", "Elena"]
APELLIDOS = ["Garcia", "Rodriguez", "Gonzalez", "Fernandez", "Lopez", "Martinez", "Sanchez", "Perez", "Gomez", "Martin", "Jimenez", "Ruiz", "Hernandez", "Diaz", "Moreno", "Muñoz", "Alvarez", "Romero", "Alonso", "Gutierrez", "Navarro", "Torres", "Dominguez", "Vazquez", "Ramos", "Gil", "Ramirez", "Serrano", "Blanco", "Molina", "Morales", "Suarez", "Ortega", "Delgado", "Castro"]

def generar_nombre_completo():
    return f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"

# Memoria local
db_classes = []   
db_students = []  
db_teachers = []  
db_subjects = []  

# ==========================================
# 1. GENERACIÓN DE ESTRUCTURA
# ==========================================
def generar_sql_estructura(f):
    f.write("-- 0. LIMPIEZA INICIAL\n")
    f.write("TRUNCATE students, teachers, classes, subjects, teacher_reports, witness_reports, ai_daily_predictions, cases, teacher_classes RESTART IDENTITY CASCADE;\n\n")

    f.write("-- 1. ASIGNATURAS\n")
    for i, asig in enumerate(TODAS_ASIGNATURAS, 1):
        f.write(f"INSERT INTO subjects (name) VALUES ('{asig}');\n")
        db_subjects.append({'id': i, 'name': asig})

    f.write("\n-- 2. PROFESORES\n")
    for i in range(1, 26):
        nombre_completo = generar_nombre_completo()
        parts = nombre_completo.split()
        email = f"{parts[0].lower()}.{parts[1].lower()}@escudoescolar.demo"
        f.write(f"INSERT INTO teachers (name, email, password_hash) VALUES ('{nombre_completo}', '{email}', 'pbkdf2:sha256:dummyhash');\n")
        db_teachers.append({'id': i, 'name': nombre_completo})

    f.write("\n-- 3. CLASES Y ALUMNOS\n")
    class_id_counter = 0
    student_id_counter = 0
    
    for curso in CURSOS:
        for letra in LETRAS:
            class_id_counter += 1
            nombre_clase = f"{curso} {letra}"
            f.write(f"INSERT INTO classes (name) VALUES ('{nombre_clase}');\n")
            db_classes.append({'id': class_id_counter, 'name': nombre_clase})
            
            for _ in range(25):
                student_id_counter += 1
                nom = generar_nombre_completo()
                f.write(f"INSERT INTO students (name, class_id) VALUES ('{nom}', {class_id_counter});\n")
                db_students.append({'id': student_id_counter, 'name': nom, 'class_id': class_id_counter, 'class_name': nombre_clase})

    f.write("\n-- 4. ASIGNACIÓN PROFESORES\n")
    for tc in db_teachers:
        clases_asignadas = random.sample(db_classes, 5)
        for c in clases_asignadas:
            f.write(f"INSERT INTO teacher_classes (teacher_id, class_id) VALUES ({tc['id']}, {c['id']});\n")

# ==========================================
# 2. GUION DE REPORTES (DINÁMICO Y VARIADO)
# ==========================================
reportes_profesores_data = [] 
reportes_testigos_data = []   

def get_student_by_class(class_name_partial):
    candidatos = [s for s in db_students if class_name_partial in s['class_name']]
    if not candidatos: return db_students[0]
    return random.choice(candidatos)

def get_subject_id(name_partial):
    match = next((s for s in db_subjects if name_partial in s['name']), None)
    if match: return match['id']
    return random.choice(db_subjects)['id']

SCENARIOS = {
    'FISICO_MATERIAL': {
        'metrics': {'physical_damage': (1, 3), 'emotional_reactivity': (1, 2)},
        'notes': [
            "Le han roto el estuche de lápices.", "Le han tirado la mochila al suelo.", 
            "Empujones en el pasillo.", "Le han manchado la ropa en el recreo.",
            "Ha llegado a clase con el material roto."
        ],
        'subject_hint': 'General'
    },
    'EXCLUSION_SOCIAL': {
        'metrics': {'peer_exclusion': (2, 3), 'social_isolation': (2, 3)},
        'notes': [
            "Nadie quiere ponerse con él en el grupo.", "Se queda solo en el patio sistemáticamente.",
            "Le hacen el vacío cuando intenta hablar.", "Excluido del juego de equipo.",
            "Los compañeros le ignoran deliberadamente."
        ],
        'subject_hint': 'EF' 
    },
    'VERBAL_HUMILLACION': {
        'metrics': {'inhibition': (2, 3), 'emotional_reactivity': (2, 3)},
        'notes': [
            "Risas y cuchicheos cuando interviene.", "Burlas sobre su aspecto físico.",
            "Le han puesto un mote ofensivo.", "Ha salido llorando de clase.",
            "Murmullos constantes a su alrededor."
        ],
        'subject_hint': 'General'
    },
    'CIBER_SILENCIOSO': {
        'metrics': {'social_isolation': (2, 3), 'inhibition': (2, 3), 'intuition': (1, 2)},
        'notes': [
            "Parece tener miedo de mirar el móvil.", "Rumores circulando por WhatsApp.",
            "Muy callado y asustadizo hoy.", "Evita el contacto visual con ciertos alumnos.",
            "Bajada brusca de rendimiento, muy distraído."
        ],
        'subject_hint': 'General'
    }
}

def generar_evento_variado(teacher_id, student_id, date, last_scenario=None):
    keys = list(SCENARIOS.keys())
    if last_scenario and random.random() < 0.3:
        scenario_key = last_scenario
    else:
        scenario_key = random.choice(keys)
    
    scenario = SCENARIOS[scenario_key]
    
    if scenario['subject_hint'] == 'EF':
        s_id = get_subject_id("Educación Física") if random.random() > 0.5 else get_subject_id("Recreo")
    else:
        s_id = random.choice([s['id'] for s in db_subjects if s['name'] in ASIGNATURAS_ACADEMICAS])

    report_data = {
        'teacher_id': teacher_id,
        'student_id': student_id,
        'subject_id': s_id,
        'date': date,
        'notes': random.choice(scenario['notes'])
    }
    
    for metric, (min_v, max_v) in scenario['metrics'].items():
        val = random.randint(min_v, max_v)
        if random.random() < 0.3: val = max(1, val - 1)
        report_data[metric] = val
        
    if 'intuition' not in report_data:
        report_data['intuition'] = random.choice([0, 1, 2])
        
    return report_data, scenario_key


def generar_eventos():
    vic_1 = get_student_by_class("ESO 1") 
    vic_2 = get_student_by_class("ESO 3") 
    
    candidatos_3 = [s for s in db_students if "Primaria 4 A" in s['class_name']]
    vic_3 = candidatos_3[0] if candidatos_3 else db_students[0]
    
    rebelde_1 = get_student_by_class("ESO 2")
    
    print(f"Víctimas seleccionadas: \n  1. {vic_1['name']} (ESO 1)\n  2. {vic_2['name']} (ESO 3)\n  3. {vic_3['name']} (PRI 4A)")

    dias = pd.date_range(FECHA_INICIO, FECHA_FIN, freq='D')
    
    last_scen_1 = None
    last_scen_2 = None

    for fecha in dias:
        if fecha.weekday() > 4: continue 
        
        # CASO 1
        if random.random() < 0.7:
            t_id = random.choice(db_teachers)['id']
            rep, last_scen_1 = generar_evento_variado(t_id, vic_1['id'], fecha, last_scen_1)
            reportes_profesores_data.append(rep)
            if random.random() < 0.6:
                for _ in range(random.randint(1, 3)):
                    reportes_testigos_data.append({'class_id': vic_1['class_id'], 'date': fecha})

        # CASO 2
        if fecha >= pd.Timestamp(2025, 12, 1):
            if random.random() < 0.4: 
                t_id = random.choice(db_teachers)['id']
                rep, last_scen_2 = generar_evento_variado(t_id, vic_2['id'], fecha, last_scen_2)
                reportes_profesores_data.append(rep)
                if random.random() < 0.25:
                    reportes_testigos_data.append({'class_id': vic_2['class_id'], 'date': fecha})

        # CASO 3 (Reciente, Fijo)
        if fecha == pd.Timestamp(2025, 12, 17):
            reportes_profesores_data.append({
                'teacher_id': random.choice(db_teachers)['id'], 'student_id': vic_3['id'], 'subject_id': 1, 'date': fecha,
                'social_isolation': 1, 'inhibition': 1, 'intuition': 1, 'notes': 'Le he visto triste hoy.'
            })
        
        if fecha == pd.Timestamp(2025, 12, 18):
            reportes_profesores_data.append({
                'teacher_id': random.choice(db_teachers)['id'], 'student_id': vic_3['id'], 'subject_id': 3, 'date': fecha,
                'emotional_reactivity': 2, 'notes': 'Ha llorado en clase sin decir por qué.'
            })
            reportes_profesores_data.append({
                'teacher_id': random.choice(db_teachers)['id'], 'student_id': vic_3['id'], 'subject_id': get_subject_id("Recreo"), 'date': fecha,
                'social_isolation': 1, 'intuition': 2, 'notes': None
            })

        # RUIDO
        if fecha == pd.Timestamp(2025, 11, 12):
             reportes_profesores_data.append({
                'teacher_id': 1, 'student_id': rebelde_1['id'], 'subject_id': 1, 'date': fecha,
                'disengagement': 3, 'notes': 'Falta injustificada'
            })
             
        if random.random() < 0.05:
            a_rand = random.choice(db_students)
            if a_rand['id'] not in [vic_1['id'], vic_2['id'], vic_3['id']]:
                reportes_profesores_data.append({
                    'teacher_id': 1, 'student_id': a_rand['id'], 'subject_id': 1, 'date': fecha,
                    'inhibition': 1, 'notes': 'Mal dia.'
                })

    return [vic_1['id'], vic_2['id'], vic_3['id']]

# ==========================================
# 3. FEATURE ENGINEERING & IA
# ==========================================
def calcular_predicciones():
    df_prof = pd.DataFrame(reportes_profesores_data)
    mapping_cols = {
        'disengagement': 'diseng',
        'social_isolation': 'soc_aisl',
        'peer_exclusion': 'soc_excl',
        'emotional_reactivity': 'con_reac',
        'inhibition': 'con_inhib',
        'physical_damage': 'fis_mat',
        'date': 'fecha',
        'student_id': 'alumno_id'
    }
    df_prof_ml = df_prof.rename(columns=mapping_cols)
    
    columnas_requeridas = ['diseng', 'soc_aisl', 'soc_excl', 'con_reac', 'con_inhib', 'fis_mat', 'intuicion']
    for col in columnas_requeridas:
        if col not in df_prof_ml.columns: df_prof_ml[col] = 0
        df_prof_ml[col] = df_prof_ml[col].fillna(0)

    df_prof_ml['fecha'] = pd.to_datetime(df_prof_ml['fecha'])

    df_testigos = pd.DataFrame(reportes_testigos_data)
    if not df_testigos.empty:
        df_testigos['fecha'] = pd.to_datetime(df_testigos['date'])
        testigos_agg = df_testigos.groupby(['fecha', 'class_id']).size().reset_index(name='n_reportes_testigos')
        testigos_agg.rename(columns={'class_id': 'clase_reportada'}, inplace=True)
    else:
        testigos_agg = pd.DataFrame(columns=['fecha', 'clase_reportada', 'n_reportes_testigos'])

    cols_sintomas = ['soc_aisl', 'soc_excl', 'con_reac', 'con_inhib', 'diseng', 'fis_mat']
    df_prof_ml['suma_puntos_dia'] = df_prof_ml[cols_sintomas].sum(axis=1)
    df_prof_ml['reporto_algo'] = (df_prof_ml['suma_puntos_dia'] > 0).astype(int)
    
    student_class_map = {s['id']: s['class_id'] for s in db_students}
    df_prof_ml['clase_id'] = df_prof_ml['alumno_id'].map(student_class_map)

    agg_funcs = {
        'soc_aisl': 'max', 'soc_excl': 'max', 'con_reac': 'max', 'con_inhib': 'max',
        'diseng': 'max', 'fis_mat': 'max', 'intuicion': 'mean',
        'reporto_algo': 'sum', 'suma_puntos_dia': 'sum',
        'clase_id': 'first'
    }
    df_daily = df_prof_ml.groupby(['fecha', 'alumno_id']).agg(agg_funcs).reset_index()
    df_daily.rename(columns={'reporto_algo': 'n_profesores_alertados', 'suma_puntos_dia': 'intensidad_diaria_total'}, inplace=True)
    
    df_daily = pd.merge(df_daily, testigos_agg, left_on=['fecha', 'clase_id'], right_on=['fecha', 'clase_reportada'], how='left')
    df_daily['n_reportes_testigos'] = df_daily['n_reportes_testigos'].fillna(0)
    
    metricas_todas = ['soc_aisl', 'soc_excl', 'con_reac', 'con_inhib', 'diseng', 'fis_mat', 'intuicion', 'n_reportes_testigos', 'n_profesores_alertados', 'intensidad_diaria_total']
    metricas_largo_plazo = ['soc_aisl', 'soc_excl', 'con_reac', 'con_inhib', 'diseng', 'fis_mat', 'intensidad_diaria_total']
    
    df_final = df_daily.sort_values(['alumno_id', 'fecha']).set_index('fecha')
    
    model = xgb.Booster()
    model.load_model(MODEL_PATH)
    feature_names = model.feature_names
    
    sql_predictions = []
    
    for uid, group in df_final.groupby('alumno_id'):
        feats = group.copy()
        
        for ventana in [3, 10, 30]:
            if ventana == 30: cols_to_roll = metricas_largo_plazo
            else: cols_to_roll = metricas_todas

            roll_mean = group[cols_to_roll].rolling(f'{ventana}D', min_periods=1).mean().add_suffix(f'_mean_{ventana}d')
            feats = pd.concat([feats, roll_mean], axis=1)
            
            cols_max_src = [c for c in cols_to_roll if c in cols_sintomas]
            if cols_max_src:
                roll_max = group[cols_max_src].rolling(f'{ventana}D', min_periods=1).max().add_suffix(f'_max_{ventana}d')
                feats = pd.concat([feats, roll_max], axis=1)
            
            if ventana in [3, 10]:
                cols_sum_src = [c for c in ['n_reportes_testigos', 'n_profesores_alertados', 'intensidad_diaria_total'] if c in cols_to_roll]
                if cols_sum_src:
                    roll_sum = group[cols_sum_src].rolling(f'{ventana}D', min_periods=1).sum().add_suffix(f'_sum_{ventana}d')
                    feats = pd.concat([feats, roll_sum], axis=1)

        roll_std = group[metricas_largo_plazo].rolling('30D', min_periods=5).std().add_suffix('_std_30d').fillna(0)
        feats = pd.concat([feats, roll_std], axis=1)

        feats = feats.fillna(0)
        feats['ratio_testigos_vs_profes'] = feats['n_reportes_testigos_sum_10d'] / (feats['n_profesores_alertados_sum_10d'] + 1)
        feats['indice_sufrimiento_silencioso'] = (feats['con_inhib_mean_10d'] + feats['soc_aisl_mean_10d']) * (feats['intuicion_mean_10d'] + 0.5)
        feats['indice_rebeldia'] = feats['diseng_mean_30d'] - (feats['n_reportes_testigos_mean_10d'] + feats['soc_aisl_mean_30d'])
        feats['aceleracion_testigos'] = feats['n_reportes_testigos_sum_3d'] - (feats['n_reportes_testigos_sum_10d'] / 3.3)
        
        for col in metricas_todas:
            if col in metricas_largo_plazo:
                if f'{col}_mean_30d' in feats.columns:
                    feats[f'{col}_delta_trend'] = feats[f'{col}_mean_3d'] - feats[f'{col}_mean_30d']
            elif 'intuicion' in col:
                 feats[f'{col}_delta_trend'] = feats[f'{col}_mean_3d'] - feats[f'{col}_mean_10d']

        for f in feature_names:
            if f not in feats.columns: feats[f] = 0
            
        dtest = xgb.DMatrix(feats[feature_names])
        probs = model.predict(dtest)
        
        feats['prob'] = probs
        feats = feats.reset_index()
        
        for _, row in feats.iterrows():
            prob = row['prob']
            is_alert = prob >= UMBRAL_DECISION
            
            # --- CORRECCIÓN AQUÍ: JSON SIN BARRAS ESCAPADAS ---
            # El SQL debe quedar: '{"key": value}'
            risk_factors = []
            if row.get('n_reportes_testigos_sum_10d', 0) > 0:
                risk_factors.append(f'"testigos": {row["n_reportes_testigos_sum_10d"]}')
            if row.get('soc_aisl_mean_10d', 0) > 0:
                risk_factors.append(f'"aislamiento": {round(row["soc_aisl_mean_10d"], 2)}')
            if row.get('intuicion_mean_10d', 0) > 0:
                risk_factors.append(f'"intuicion_profe": {round(row["intuicion_mean_10d"], 2)}')
            
            risk_json = "{" + ", ".join(risk_factors) + "}"
            
            sql_predictions.append({
                'student_id': uid,
                'date': row['fecha'].date(),
                'prob': prob,
                'is_alert': is_alert,
                'risk': risk_json
            })
            
    return sql_predictions

# ==========================================
# 4. ESCRITURA SQL
# ==========================================
def main():
    print(f"Generando {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        generar_sql_estructura(f)
        
        print("Generando Guion (Eventos Variados)...")
        victims_ids = generar_eventos()
        
        f.write("\n-- 5. REPORTES PROFESORES\n")
        for r in reportes_profesores_data:
            cols = ['teacher_id', 'student_id', 'subject_id', 'date']
            vals = [str(r['teacher_id']), str(r['student_id']), str(r['subject_id']), f"'{r['date'].date()}'"]
            
            metrics = ['disengagement', 'social_isolation', 'peer_exclusion', 'emotional_reactivity', 'inhibition', 'physical_damage', 'intuition']
            for m in metrics:
                if m in r: cols.append(m); vals.append(str(r[m]))
            
            if 'notes' in r and r['notes']: cols.append('notes'); vals.append(f"'{r['notes']}'")
            f.write(f"INSERT INTO teacher_reports ({','.join(cols)}) VALUES ({','.join(vals)});\n")

        f.write("\n-- 6. REPORTES TESTIGOS\n")
        for r in reportes_testigos_data:
            f.write(f"INSERT INTO witness_reports (class_id, date) VALUES ({r['class_id']}, '{r['date'].date()}');\n")

        print("Calculando IA...")
        ai_preds = calcular_predicciones()
        
        f.write("\n-- 7. PREDICCIONES IA\n")
        for p in ai_preds:
            if p['prob'] > 0.01:
                # El risk_json ya viene limpio: {"testigos": 5}
                # Solo necesitamos envolverlo en comillas simples para SQL
                f.write(f"INSERT INTO ai_daily_predictions (student_id, date, bullying_probability, is_alert, risk_factors) VALUES ({p['student_id']}, '{p['date']}', {round(p['prob'], 4)}, {'TRUE' if p['is_alert'] else 'FALSE'}, '{p['risk']}');\n")

        f.write("\n-- 8. CASOS\n")
        f.write(f"INSERT INTO cases (student_id, opened_at, status, psychologist_notes, final_diagnosis) VALUES ({victims_ids[0]}, '2025-10-15', 'CONFIRMED', 'Caso grave detectado.', 'Acoso Escolar');\n")
        f.write(f"INSERT INTO cases (student_id, opened_at, status, psychologist_notes) VALUES ({victims_ids[1]}, '2025-12-10', 'INVESTIGATING', 'Alertas recientes.');\n")

    print(f"¡Hecho! Archivo '{OUTPUT_FILE}' generado.")

if __name__ == "__main__":
    main()
