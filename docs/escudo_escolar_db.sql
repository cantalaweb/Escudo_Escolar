-- =============================================================================
-- 1. ESTRUCTURA ACADÉMICA (ESTÁTICA)
-- =============================================================================

-- Clases / Aulas (Ej: "ESO 1º A")
CREATE TABLE classes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Asignaturas (Ej: "Matemáticas", "Educación Física", "Guardia")
CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Alumnos
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    class_id INT REFERENCES classes(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Profesores
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Relación: Qué profesores dan clase a qué grupos (Para permisos de la App)
CREATE TABLE teacher_classes (
    teacher_id INT REFERENCES teachers(id) ON DELETE CASCADE,
    class_id INT REFERENCES classes(id) ON DELETE CASCADE,
    PRIMARY KEY (teacher_id, class_id)
);

-- =============================================================================
-- 2. INPUTS DEL MODELO (DIARIO)
-- =============================================================================

-- Reportes de Observación Docente (Fuente Principal)
CREATE TABLE teacher_reports (
    id BIGSERIAL PRIMARY KEY, -- BIGSERIAL porque crecerá muy rápido
    teacher_id INT REFERENCES teachers(id),
    student_id INT REFERENCES students(id),
    subject_id INT REFERENCES subjects(id), -- Vital: saber si es EF o Mates
    
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Métricas Escala Likert (0-3). Usamos SMALLINT para ahorrar espacio.
    academic_performance SMALLINT DEFAULT 0, -- log_asis
    social_isolation SMALLINT DEFAULT 0,     -- soc_aisl
    peer_exclusion SMALLINT DEFAULT 0,       -- soc_excl
    emotional_reactivity SMALLINT DEFAULT 0, -- con_reac
    inhibition SMALLINT DEFAULT 0,           -- con_inhib
    physical_damage SMALLINT DEFAULT 0,      -- fis_mat
    intuition SMALLINT DEFAULT 0,            -- intuicion
    
    notes TEXT, -- Feedback cualitativo para el psicólogo
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reportes de Testigos (Fuente Secundaria / Desempate)
CREATE TABLE witness_reports (
    id BIGSERIAL PRIMARY KEY,
    class_id INT REFERENCES classes(id), -- El reporte se asocia a la clase, no al alumno específico (anonimato)
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 3. CEREBRO DE LA IA Y GESTIÓN
-- =============================================================================

-- Histórico de Predicciones (Para gráficas de evolución)
CREATE TABLE ai_daily_predictions (
    id BIGSERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    bullying_probability REAL, -- FLOAT de 4 bytes es suficiente (0.0 a 1.0)
    is_alert BOOLEAN DEFAULT FALSE, -- Si superó el umbral (0.7117)
    
    -- Aquí guardamos el "Por qué" (Feature Importance local)
    -- Ej: {"testigos": "HIGH", "aislamiento": "MED"}
    risk_factors JSONB, 
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Gestión de Casos (El ciclo de feedback humano)
CREATE TABLE cases (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    
    opened_at DATE DEFAULT CURRENT_DATE,
    closed_at DATE,
    
    -- Estados del caso
    status VARCHAR(50) CHECK (status IN ('INVESTIGATING', 'CONFIRMED', 'FALSE_ALARM', 'RESOLVED', 'MONITORING')),
    
    psychologist_notes TEXT,
    final_diagnosis VARCHAR(100) -- Ej: "Conflicto puntual", "Acoso escolar", "Problema familiar"
);

-- =============================================================================
-- 4. ÍNDICES DE RENDIMIENTO (CRÍTICO PARA MACHINE LEARNING)
-- =============================================================================
-- El script Python va a pedir: "Dame datos de tal alumno entre fecha X e Y" constantemente.

CREATE INDEX idx_reports_student_date ON teacher_reports(student_id, date);
CREATE INDEX idx_reports_date ON teacher_reports(date); -- Para "dame todo lo de hoy"
CREATE INDEX idx_witness_class_date ON witness_reports(class_id, date);
CREATE INDEX idx_predictions_student_date ON ai_daily_predictions(student_id, date);