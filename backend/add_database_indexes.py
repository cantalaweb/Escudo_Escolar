"""
Script para añadir índices a la base de datos y mejorar el rendimiento
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

def add_indexes():
    """Añade índices a las tablas para optimizar las consultas del dashboard"""

    engine = create_engine(settings.DATABASE_URL)

    indexes = [
        # Índices en teacher_reports
        "CREATE INDEX IF NOT EXISTS idx_teacher_reports_student_date ON teacher_reports(student_id, date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_teacher_reports_date ON teacher_reports(date DESC)",

        # Índices en witness_reports
        "CREATE INDEX IF NOT EXISTS idx_witness_reports_class_date ON witness_reports(class_id, date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_witness_reports_date ON witness_reports(date DESC)",

        # Índices en ai_daily_predictions
        "CREATE INDEX IF NOT EXISTS idx_ai_predictions_student_date ON ai_daily_predictions(student_id, date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_ai_predictions_date ON ai_daily_predictions(date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_ai_predictions_probability ON ai_daily_predictions(bullying_probability)",

        # Índices en students
        "CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_id)",
    ]

    try:
        with engine.connect() as conn:
            print("="*70)
            print("AÑADIENDO ÍNDICES PARA OPTIMIZAR RENDIMIENTO DEL DASHBOARD")
            print("="*70)
            print()

            for i, index_sql in enumerate(indexes, 1):
                print(f"[{i}/{len(indexes)}] Creando índice...")
                conn.execute(text(index_sql))
                conn.commit()
                print(f"  ✓ {index_sql.split('idx_')[1].split(' ON')[0]}")

            print()
            print("Analizando tablas para actualizar estadísticas...")

            tables = ['teacher_reports', 'witness_reports', 'ai_daily_predictions', 'students']
            for table in tables:
                conn.execute(text(f"ANALYZE {table}"))
                conn.commit()
                print(f"  ✓ {table}")

            print()
            print("="*70)
            print("✓ ÍNDICES CREADOS EXITOSAMENTE")
            print("="*70)
            print()
            print("Beneficios esperados:")
            print("  • Consultas por fecha: 10-100x más rápidas")
            print("  • Búsquedas por estudiante: 5-50x más rápidas")
            print("  • Joins entre tablas: 3-10x más rápidos")
            print("  • Tiempo de carga del dashboard: reducido significativamente")
            print()
            print("El dashboard ahora debería cargar mucho más rápido.")

    except Exception as e:
        print(f"\n✗ Error al crear índices: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()

if __name__ == "__main__":
    add_indexes()
