-- Migración: Renombrar columna academic_performance a disengagement
-- Fecha: 2025-12-16
-- Descripción: Cambiar el nombre de la columna academic_performance a disengagement
--              para reflejar mejor su propósito de medir desenganche escolar

-- Renombrar la columna
ALTER TABLE teacher_reports
RENAME COLUMN academic_performance TO disengagement;

-- Nota: Esta migración es compatible con PostgreSQL
-- El cambio de nombre no afecta los datos existentes
