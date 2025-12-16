import pandas as pd
import numpy as np
import random
import string
import os
from datetime import timedelta, date

# ==========================================
# CONFIGURACIÓN
# ==========================================
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

N_CLASES_POR_CURSO = 10
N_COLEGIOS = 10
ALUMNOS_POR_CLASE = 30 
INCIDENCIA_BULLYING_PER_1000 = 40 

CURSOS = ['Primaria 4', 'Primaria 5', 'Primaria 6', 'ESO 1', 'ESO 2', 'ESO 3', 'ESO 4', 'Bachillerato 1', 'Bachillerato 2']
FECHA_INICIO = date(2025, 9, 1) 
FECHA_FIN = date(2026, 6, 19)

ASIGNATURAS_ACADEMICAS = ['Matemáticas', 'Lengua', 'Inglés', 'Biología', 'Geografía e Historia', 'Física y Química', 'Plástica', 'Música', 'Tecnología', 'Filosofía', 'Economía']
ASIG_EF = 'Educación Física'
ASIG_RECREO = 'Recreo'
ASIG_COMEDOR = 'Comedor'

os.makedirs('./data/raw', exist_ok=True)

class GeneradorBullying:
    def __init__(self):
        self.alumnos = []
        self.profesores = []
        self.clases = [] 
        self.calendario = []
        self.casos_bullying = []
        self.eventos_ruido = []
        self.casos_rebeldia = [] # <--- NUEVO (Falsos positivos de asistencia)
        self.manias_profesores = {}
        self.horarios = {} 
        self.data_reportes_profesores = []
        self.data_reportes_alumnos = []

    def _generar_nombre_clase(self, n):
        nombre = ""
        while n >= 0:
            nombre = string.ascii_uppercase[n % 26] + nombre
            n = n // 26 - 1
        return nombre

    def ejecutar(self):
        print(f"1. Generando estructura ({N_COLEGIOS} Colegios)...")
        self._generar_estructura()
        print("2. Calendario...")
        self._generar_calendario_y_horarios()
        print("3. Escenarios (Bullying Invisible vs Rebeldía)...")
        self._generar_casos_bullying()
        self._generar_casos_rebeldia() # <--- NUEVO
        self._generar_ruido()
        self._generar_manias()
        print("4. Simulando curso (Testigos como única verdad)...")
        self._simular_curso()
        return self._crear_dataframes_y_resumen()

    def _generar_estructura(self):
        # Sensibilidad media -1.5 (Ceguera casi total para obligar a usar testigos)
        id_counter = 0
        for i_col in range(1, N_COLEGIOS + 1):
            col_id = f"COL_{i_col:02d}"
            
            for asig in ASIGNATURAS_ACADEMICAS + [ASIG_EF]:
                self.profesores.append({
                    'id': f"PROF_{col_id}_{asig[:4].upper()}",
                    'colegio_id': col_id, 'asignatura': asig,
                    'sensibilidad': np.random.normal(-1.5, 0.5), # Ceguera severa
                    'paranoia': np.random.uniform(0, 0.2), 
                    'historial_alertas': {}
                })

            for curso in CURSOS:
                for i_clase in range(N_CLASES_POR_CURSO):
                    letra = self._generar_nombre_clase(i_clase)
                    clase_id = f"{col_id}_{curso}_{letra}"
                    self.clases.append(clase_id)
                    self.profesores.append({
                        'id': f"PROF_G_{clase_id}", 'colegio_id': col_id, 'asignatura': 'Guardia', 
                        'sensibilidad': np.random.normal(-1.0, 0.6), # Guardia ve un poco más
                        'paranoia': np.random.uniform(0, 0.3), 'historial_alertas': {}
                    })
                    for _ in range(ALUMNOS_POR_CLASE):
                        id_counter += 1
                        self.alumnos.append({
                            'id': id_counter, 'colegio_id': col_id, 'clase_id': clase_id,
                            'perfil_victima': random.choice(['Normativo', 'Reactivo', 'Pasivo', 'Academico'])
                        })

    def _generar_calendario_y_horarios(self):
        delta = FECHA_FIN - FECHA_INICIO
        for i in range(delta.days + 1):
            day = FECHA_INICIO + timedelta(days=i)
            if day.weekday() < 5: self.calendario.append(day)
        for clase_id in self.clases:
            self.horarios[clase_id] = {}
            dias_ef = random.sample([0, 1, 2, 3, 4], k=random.choice([2, 3]))
            for dia in range(5):
                mix = [ASIG_RECREO, ASIG_RECREO, ASIG_COMEDOR]
                if dia in dias_ef: mix.append(ASIG_EF)
                while len(mix) < 7: mix.append(random.choice(ASIGNATURAS_ACADEMICAS))
                self.horarios[clase_id][dia] = mix

    def _generar_casos_bullying(self):
        colegios = pd.DataFrame(self.alumnos)['colegio_id'].unique()
        for col in colegios:
            alumnos_col = [a for a in self.alumnos if a['colegio_id'] == col]
            n_casos = int((len(alumnos_col) / 1000) * INCIDENCIA_BULLYING_PER_1000)
            n_casos = max(n_casos, 2)
            victimas = random.sample(alumnos_col, n_casos)
            for vic in victimas:
                duracion = random.randint(15, 50) 
                start_idx = random.randint(0, max(0, len(self.calendario) - duracion))
                self.casos_bullying.append({
                    'alumno_id': vic['id'],
                    'fecha_inicio': self.calendario[start_idx],
                    'fecha_fin': self.calendario[min(len(self.calendario)-1, start_idx + duracion)],
                    'tipo': random.choice(['Fisico', 'Verbal', 'Invisible', 'Invisible', 'Mixto']), # Invisible es clave
                    'perfil': vic['perfil_victima']
                })

    def _generar_casos_rebeldia(self):
        # "Rebeldía/Novillos": Alumnos que faltan a clase sistemáticamente (sintoma diseng alto)
        # pero NO sufren bullying. Esto rompe la correlación Asistencia=Bullying.
        n_casos = len(self.casos_bullying) * 2
        
        ids_bullying = [c['alumno_id'] for c in self.casos_bullying]
        candidatos = [a for a in self.alumnos if a['id'] not in ids_bullying]
        if not candidatos: return
        
        rebeldes = random.sample(candidatos, min(len(candidatos), n_casos))
        for reb in rebeldes:
            duracion = random.randint(10, 40)
            start_idx = random.randint(0, max(0, len(self.calendario) - duracion))
            self.casos_rebeldia.append({
                'alumno_id': reb['id'], 'fecha_inicio': self.calendario[start_idx], 'fecha_fin': self.calendario[min(len(self.calendario)-1, start_idx + duracion)], 'tipo': 'Rebeldia'
            })

    def _generar_ruido(self):
        n_ruido = len(self.casos_bullying) * 6
        for _ in range(n_ruido):
            alumno = random.choice(self.alumnos)
            self.eventos_ruido.append({ 'alumno_id': alumno['id'], 'fecha': random.choice(self.calendario), 'tipo': 'Puntual' })

    def _generar_manias(self):
        n_manias = len(self.alumnos) // 20 
        for _ in range(n_manias):
            alumno = random.choice(self.alumnos)
            # Buscar un profe de su colegio
            profes_col = [p for p in self.profesores if p.get('colegio_id') == alumno['colegio_id']]
            if profes_col:
                profe = random.choice(profes_col)
                self.manias_profesores[(profe['id'], alumno['id'])] = random.uniform(0.5, 1.2)

    def _simular_curso(self):
        mapa_bullying = {} 
        for c in self.casos_bullying:
            rango = [c['fecha_inicio'] + timedelta(days=x) for x in range((c['fecha_fin'] - c['fecha_inicio']).days + 1)]
            for i, d in enumerate(rango):
                if d in self.calendario and random.random() > 0.4: # Intermitencia alta
                    mapa_bullying[(d, c['alumno_id'])] = {'tipo': c['tipo'], 'perfil': c['perfil'], 'dias_activos': i+1}
        
        mapa_rebeldia = {}
        for c in self.casos_rebeldia:
            rango = [c['fecha_inicio'] + timedelta(days=x) for x in range((c['fecha_fin'] - c['fecha_inicio']).days + 1)]
            for d in rango:
                if d in self.calendario and random.random() > 0.3: # Faltan mucho
                    mapa_rebeldia[(d, c['alumno_id'])] = True

        mapa_ruido = {(r['fecha'], r['alumno_id']): True for r in self.eventos_ruido}

        for fecha in self.calendario:
            dia_semana = fecha.weekday()
            for alumno in self.alumnos:
                key = (fecha, alumno['id'])
                tiene_algo = key in mapa_bullying or key in mapa_rebeldia or key in mapa_ruido
                
                if not tiene_algo and random.random() > 0.05: continue 
                
                ctx = {'is_active': 0, 'tipo_bullying': 'Ninguno', 'perfil': alumno['perfil_victima'], 'dias_acumulados': 0, 'n_eventos': 0, 'evitacion': False}

                if key in mapa_bullying:
                    data = mapa_bullying[key]
                    ctx['is_active'] = 1; ctx['tipo_bullying'] = data['tipo']; ctx['dias_acumulados'] = data['dias_activos']
                    
                    # Bullying Invisible: Profes ven 0, pero testigos ven todo.
                    if data['tipo'] == 'Invisible':
                        ctx['n_eventos'] = 0 # Para los profes
                        ctx['evitacion'] = False # El alumno sufre en silencio, no falta
                        # Testigo GARANTIZADO si es invisible
                        if random.random() < 0.8: 
                             self._generar_reportes_testigos(fecha, alumno['clase_id'], 2, es_real=True)
                    else:
                        # Otros tipos
                        ctx['n_eventos'] = random.choices([0,1,2], weights=[0.6, 0.3, 0.1])[0]
                        if ctx['n_eventos'] == 0: ctx['evitacion'] = True
                        if random.random() < 0.5: 
                            self._generar_reportes_testigos(fecha, alumno['clase_id'], ctx['n_eventos'], es_real=True)

                elif key in mapa_rebeldia:
                    ctx['is_active'] = 0; ctx['tipo_bullying'] = 'Rebeldia'
                    ctx['evitacion'] = True # Faltan a clase (Logistica alta)
                    # OJO: Aquí NO hay testigos (o muy pocos falsos)
                    if random.random() < 0.05: self._generar_reportes_testigos(fecha, alumno['clase_id'], 1, es_real=False)

                elif key in mapa_ruido:
                    ctx['tipo_bullying'] = 'Puntual'; ctx['n_eventos'] = 1

                self._procesar_profesores(fecha, alumno, self.horarios[alumno['clase_id']][dia_semana], ctx)

    def _generar_reportes_testigos(self, fecha, clase_id, intensidad, es_real):
        n_reps = random.randint(1, 4) # Más testigos
        for _ in range(n_reps):
            self.data_reportes_alumnos.append({ 'fecha': fecha + timedelta(days=random.randint(0,2)), 'clase_reportada': clase_id })

    def _procesar_profesores(self, fecha, alumno, asignaturas, ctx):
        profes_asignados = []
        for asig in set(asignaturas):
            pid = ""
            if asig in [ASIG_RECREO, ASIG_COMEDOR]:
                pid = f"PROF_G_{alumno['clase_id']}"
            else:
                pid = f"PROF_{alumno['colegio_id']}_{asig[:4].upper()}"
            match = next((p for p in self.profesores if p['id'] == pid), None)
            if match: profes_asignados.append(match)
        profes_unicos = list({p['id']: p for p in profes_asignados}.values())

        for profe in profes_unicos:
            vals = {'soc_aisl':0, 'soc_excl':0, 'con_reac':0, 'con_inhib':0, 'diseng':0, 'fis_mat':0, 'intuicion':0}
            sensibilidad = profe['sensibilidad'] # Promedio -1.5 (Ciegos)
            
            # SÍNTOMAS
            if ctx['is_active'] == 1: # Bullying
                factor_t = min(1.5, 1 + (ctx['dias_acumulados']/100))
                base = random.gauss(1.5, 0.8) * factor_t 
                
                if ctx['tipo_bullying'] == 'Invisible':
                    # En invisible, los profes NO ven nada (todo 0)
                    # Solo la intuición puede subir un poco si el profe es muy sensible
                    if sensibilidad > 0: vals['intuicion'] += base * 0.3
                else:
                    if ctx['evitacion']:
                        vals['diseng'] += random.gauss(2.0, 0.6) # Asistencia sí se ve
                        vals['con_inhib'] += random.gauss(1.0, 0.6)
                    elif ctx['n_eventos'] > 0:
                        if profe['asignatura'] in [ASIG_EF, 'Guardia']: base *= 1.2
                        if ctx['tipo_bullying'] != 'Ciberbullying': vals['fis_mat'] += base * random.random()
                        vals['soc_aisl'] += base; vals['intuicion'] += base * 0.4

            elif ctx['tipo_bullying'] == 'Rebeldia':
                # El rebelde falta a clase (diseng alto)
                # Esto confunde al modelo: ¿Es bullying (evitación) o rebeldía?
                # El DESEMPATE es el testigo.
                vals['diseng'] += random.gauss(2.5, 0.5) 
                vals['con_reac'] += random.gauss(1.0, 0.5) # A veces contestan mal

            elif ctx['tipo_bullying'] == 'Puntual':
                vals['con_reac'] += random.gauss(2.0, 0.6)

            # GUARDADO
            row = {
                'fecha': fecha, 'colegio_id': alumno['colegio_id'], 'clase_id': alumno['clase_id'], 'alumno_id': alumno['id'],
                'profesor_id': profe['id'], 'asignatura': profe['asignatura'],
                'is_bullying_active': ctx['is_active'], 'meta_tipo': ctx['tipo_bullying']
            }
            
            for k, v in vals.items():
                v_final = v + sensibilidad + random.normalvariate(0, 0.5)
                v_int = max(0, min(3, int(round(v_final))))
                if v < 0.9 and v_int > 0: v_int = 0 
                row[k] = v_int
            self.data_reportes_profesores.append(row)

    def _crear_dataframes_y_resumen(self):
        df_p = pd.DataFrame(self.data_reportes_profesores)
        df_a = pd.DataFrame(self.data_reportes_alumnos)
        if not df_p.empty:
            df_p = df_p.sort_values(['fecha', 'alumno_id'])
            # Verificar
            invisibles = df_p[df_p['meta_tipo'] == 'Invisible'].shape[0]
            rebeldes = df_p[df_p['meta_tipo'] == 'Rebeldia'].shape[0]
            print(f"\n[INFO v12.0]")
            print(f"Filas Bullying Invisible (Solo Testigos): {invisibles}")
            print(f"Filas Rebeldía (Falta asistencia, 0 Testigos): {rebeldes}")
            
        df_p.to_csv("./data/raw/dataset_bullying_profesores.csv", index=False)
        df_a.to_csv("./data/raw/dataset_bullying_testigos.csv", index=False)
        return df_p, df_a

if __name__ == "__main__":
    gen = GeneradorBullying()
    gen.ejecutar()
