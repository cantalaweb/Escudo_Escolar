-- ============================================================================
-- ÍNDICES PARA OPTIMIZAR RENDIMIENTO DEL DASHBOARD
-- ============================================================================
-- Este script añade índices en las columnas más consultadas para acelerar
-- las queries del dashboard

-- Índices en teacher_reports
CREATE INDEX IF NOT EXISTS idx_teacher_reports_student_date
ON teacher_reports(student_id, date DESC);

CREATE INDEX IF NOT EXISTS idx_teacher_reports_date
ON teacher_reports(date DESC);

-- Índices en witness_reports
CREATE INDEX IF NOT EXISTS idx_witness_reports_class_date
ON witness_reports(class_id, date DESC);

CREATE INDEX IF NOT EXISTS idx_witness_reports_date
ON witness_reports(date DESC);

-- Índices en ai_daily_predictions
CREATE INDEX IF NOT EXISTS idx_ai_predictions_student_date
ON ai_daily_predictions(student_id, date DESC);

CREATE INDEX IF NOT EXISTS idx_ai_predictions_date
ON ai_daily_predictions(date DESC);

CREATE INDEX IF NOT EXISTS idx_ai_predictions_probability
ON ai_daily_predictions(bullying_probability);

-- Índices en students (para joins rápidos)
CREATE INDEX IF NOT EXISTS idx_students_class
ON students(class_id);

-- Analizar las tablas para actualizar estadísticas
ANALYZE teacher_reports;
ANALYZE witness_reports;
ANALYZE ai_daily_predictions;
ANALYZE students;

-- Mostrar los índices creados
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('teacher_reports', 'witness_reports', 'ai_daily_predictions', 'students')
ORDER BY tablename, indexname;
