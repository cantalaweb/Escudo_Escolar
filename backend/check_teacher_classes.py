"""
Script para verificar y asignar clases al profesor
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

def check_and_assign_classes():
    """Verifica las clases del profesor y asigna algunas si no tiene"""

    engine = create_engine(settings.DATABASE_URL)

    try:
        with engine.connect() as conn:
            # Obtener el profesor Gustavo
            result = conn.execute(text(
                "SELECT id, name, email FROM teachers WHERE email = 'gustavo.debasica@escudoescolar.demo'"
            ))
            teacher = result.fetchone()

            if not teacher:
                print("✗ Profesor no encontrado")
                return

            teacher_id = teacher[0]
            print(f"✓ Profesor encontrado: {teacher[1]} (ID: {teacher_id})")

            # Verificar clases asignadas
            result = conn.execute(text(
                "SELECT COUNT(*) FROM teacher_classes WHERE teacher_id = :teacher_id"
            ), {"teacher_id": teacher_id})
            count = result.fetchone()[0]

            print(f"  Clases asignadas: {count}")

            if count == 0:
                print("\n  Asignando clases al profesor...")

                # Obtener todas las clases disponibles
                result = conn.execute(text("SELECT id, name FROM classes ORDER BY id LIMIT 3"))
                classes = result.fetchall()

                for class_row in classes:
                    class_id = class_row[0]
                    class_name = class_row[1]

                    # Asignar clase al profesor
                    conn.execute(text(
                        "INSERT INTO teacher_classes (teacher_id, class_id) VALUES (:teacher_id, :class_id)"
                    ), {"teacher_id": teacher_id, "class_id": class_id})

                    print(f"    ✓ Asignada clase: {class_name} (ID: {class_id})")

                conn.commit()
                print("\n✓ Clases asignadas exitosamente")
            else:
                # Mostrar clases actuales
                result = conn.execute(text("""
                    SELECT c.id, c.name
                    FROM classes c
                    JOIN teacher_classes tc ON tc.class_id = c.id
                    WHERE tc.teacher_id = :teacher_id
                """), {"teacher_id": teacher_id})

                classes = result.fetchall()
                print("\n  Clases actuales:")
                for class_row in classes:
                    print(f"    - {class_row[1]} (ID: {class_row[0]})")

    except Exception as e:
        print(f"✗ Error: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    check_and_assign_classes()
