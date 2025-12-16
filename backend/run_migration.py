"""
Script para ejecutar la migración: renombrar academic_performance a disengagement
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """Ejecuta la migración para renombrar la columna"""

    engine = create_engine(settings.DATABASE_URL)

    sql = """
    ALTER TABLE teacher_reports
    RENAME COLUMN academic_performance TO disengagement;
    """

    try:
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
            print("✓ Migración ejecutada exitosamente: academic_performance → disengagement")
    except Exception as e:
        if "column \"academic_performance\" does not exist" in str(e):
            print("✓ La columna ya ha sido renombrada (academic_performance no existe)")
        elif "column \"disengagement\" of relation \"teacher_reports\" already exists" in str(e):
            print("✓ La columna 'disengagement' ya existe")
        else:
            print(f"✗ Error ejecutando migración: {e}")
            raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    run_migration()
