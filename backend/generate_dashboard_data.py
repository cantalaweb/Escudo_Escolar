"""
Script para generar datos de prueba para el dashboard
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
from datetime import date, timedelta
import random

def generate_dashboard_data():
    """Genera reportes y predicciones para probar el dashboard"""

    engine = create_engine(settings.DATABASE_URL)

    try:
        with engine.connect() as conn:
            print("Generando datos de prueba para el dashboard...\n")

            # Obtener profesores
            result = conn.execute(text("SELECT id, name FROM teachers WHERE is_admin = false LIMIT 2"))
            teachers = result.fetchall()

            if not teachers:
                print("✗ No hay profesores en la base de datos")
                return

            teacher_ids = [t[0] for t in teachers]
            print(f"✓ Profesores encontrados: {[t[1] for t in teachers]}")

            # Obtener estudiantes
            result = conn.execute(text("SELECT id, name, class_id FROM students LIMIT 10"))
            students = result.fetchall()

            if not students:
                print("✗ No hay estudiantes en la base de datos")
                return

            print(f"✓ {len(students)} estudiantes encontrados")

            # Obtener asignaturas
            result = conn.execute(text("SELECT id FROM subjects LIMIT 3"))
            subjects = result.fetchall()
            subject_ids = [s[0] for s in subjects] if subjects else [None]

            # Generar reportes de profesores desde el inicio del año escolar
            print("\nGenerando reportes de profesores...")
            end_date = date.today()

            # Calcular inicio del año escolar (1 de septiembre)
            current_year = end_date.year
            school_year_start = date(current_year, 9, 1)
            if end_date < school_year_start:
                school_year_start = date(current_year - 1, 9, 1)

            start_date = school_year_start
            days_in_range = (end_date - start_date).days

            reports_count = 0

            for student in students:
                student_id = student[0]
                student_name = student[1]

                # Cada estudiante tendrá reportes distribuidos a lo largo del año escolar
                # Aproximadamente 1-2 reportes por semana
                num_reports = random.randint(int(days_in_range / 5), int(days_in_range / 3))

                for _ in range(num_reports):
                    # Fecha aleatoria en el rango del año escolar
                    days_ago = random.randint(0, days_in_range)
                    report_date = end_date - timedelta(days=days_ago)

                    # Generar métricas aleatorias (0-3)
                    # Algunos estudiantes tendrán más problemas que otros
                    severity_level = random.choice(['low', 'low', 'medium', 'high'])

                    if severity_level == 'low':
                        max_val = 1
                    elif severity_level == 'medium':
                        max_val = 2
                    else:
                        max_val = 3

                    social_isolation = random.randint(0, max_val)
                    peer_exclusion = random.randint(0, max_val)
                    emotional_reactivity = random.randint(0, max_val)
                    inhibition = random.randint(0, max_val)
                    disengagement = random.randint(0, max_val)
                    physical_damage = random.randint(0, max_val)
                    intuition = random.randint(0, max_val)

                    # Insertar reporte
                    conn.execute(text("""
                        INSERT INTO teacher_reports
                        (teacher_id, student_id, subject_id, date,
                         social_isolation, peer_exclusion, emotional_reactivity,
                         inhibition, disengagement, physical_damage, intuition)
                        VALUES
                        (:teacher_id, :student_id, :subject_id, :date,
                         :social_isolation, :peer_exclusion, :emotional_reactivity,
                         :inhibition, :disengagement, :physical_damage, :intuition)
                    """), {
                        "teacher_id": random.choice(teacher_ids),
                        "student_id": student_id,
                        "subject_id": random.choice(subject_ids) if subject_ids else None,
                        "date": report_date,
                        "social_isolation": social_isolation,
                        "peer_exclusion": peer_exclusion,
                        "emotional_reactivity": emotional_reactivity,
                        "inhibition": inhibition,
                        "disengagement": disengagement,
                        "physical_damage": physical_damage,
                        "intuition": intuition
                    })

                    reports_count += 1

            print(f"✓ {reports_count} reportes de profesores generados")

            # Generar reportes de testigos
            print("\nGenerando reportes de testigos...")

            # Obtener clases
            result = conn.execute(text("SELECT id FROM classes"))
            classes = result.fetchall()
            class_ids = [c[0] for c in classes]

            witness_count = 0
            # Generar reportes de testigos distribuidos en el año escolar
            num_witness_reports = int(days_in_range * 0.5)  # Aproximadamente 1 cada 2 días
            for _ in range(num_witness_reports):
                days_ago = random.randint(0, days_in_range)
                report_date = end_date - timedelta(days=days_ago)

                conn.execute(text("""
                    INSERT INTO witness_reports (class_id, date)
                    VALUES (:class_id, :date)
                """), {
                    "class_id": random.choice(class_ids),
                    "date": report_date
                })

                witness_count += 1

            print(f"✓ {witness_count} reportes de testigos generados")

            # Generar predicciones de IA
            print("\nGenerando predicciones de IA...")

            predictions_count = 0
            for student in students:
                student_id = student[0]

                # Generar predicciones a lo largo del año escolar (cada 3 días)
                for days_ago in range(0, days_in_range, 3):
                    pred_date = end_date - timedelta(days=days_ago)

                    # Calcular probabilidad basada en reportes existentes
                    # (simulado con valores aleatorios pero coherentes)
                    base_prob = random.uniform(0.1, 0.8)

                    # A veces hay alertas (probabilidad > 0.7)
                    is_alert = base_prob > 0.7

                    # Risk factors simulados
                    risk_factors = {
                        "aislamiento": random.choice(["LOW", "MED", "HIGH"]),
                        "exclusion": random.choice(["LOW", "MED", "HIGH"]),
                        "desenganche": random.choice(["LOW", "MED", "HIGH"])
                    }

                    import json
                    conn.execute(text("""
                        INSERT INTO ai_daily_predictions
                        (student_id, date, bullying_probability, is_alert, risk_factors)
                        VALUES
                        (:student_id, :date, :probability, :is_alert, CAST(:risk_factors AS jsonb))
                    """), {
                        "student_id": student_id,
                        "date": pred_date,
                        "probability": base_prob,
                        "is_alert": is_alert,
                        "risk_factors": json.dumps(risk_factors)
                    })

                    predictions_count += 1

            print(f"✓ {predictions_count} predicciones de IA generadas")

            # Commit todos los cambios
            conn.commit()

            print("\n" + "="*60)
            print("✓ Datos de prueba generados exitosamente")
            print("="*60)
            print(f"\nResumen:")
            print(f"  • Reportes de profesores: {reports_count}")
            print(f"  • Reportes de testigos: {witness_count}")
            print(f"  • Predicciones de IA: {predictions_count}")
            print(f"  • Estudiantes con datos: {len(students)}")
            print(f"\nAhora puedes probar los endpoints del dashboard:")
            print(f"  • GET /dashboard/heatmap")
            print(f"  • GET /dashboard/risk-matrix")
            print(f"  • GET /dashboard/student/{{id}}/timeline")
            print(f"  • GET /dashboard/student/{{id}}/radar")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()

if __name__ == "__main__":
    generate_dashboard_data()
