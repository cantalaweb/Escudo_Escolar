"""
Script para asignar clases a Maripi Olet
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

def assign_maripi_classes():
    """Asigna clases a Maripi Olet"""

    engine = create_engine(settings.DATABASE_URL)

    try:
        with engine.connect() as conn:
            # Buscar a Maripi Olet
            result = conn.execute(text(
                "SELECT id, name, email FROM teachers WHERE name ILIKE '%maripi%' OR name ILIKE '%olet%'"
            ))
            teachers = result.fetchall()

            if not teachers:
                print("✗ Profesora Maripi Olet no encontrada")
                print("\nBuscando todos los profesores...")
                result = conn.execute(text("SELECT id, name, email FROM teachers ORDER BY id"))
                all_teachers = result.fetchall()
                for t in all_teachers:
                    print(f"  - {t[1]} ({t[2]}) - ID: {t[0]}")
                return

            teacher = teachers[0]
            teacher_id = teacher[0]
            print(f"✓ Profesora encontrada: {teacher[1]} (ID: {teacher_id})")
            print(f"  Email: {teacher[2]}")

            # Verificar clases ya asignadas
            result = conn.execute(text(
                "SELECT COUNT(*) FROM teacher_classes WHERE teacher_id = :teacher_id"
            ), {"teacher_id": teacher_id})
            count = result.fetchone()[0]

            print(f"  Clases asignadas actualmente: {count}")

            # Obtener clases disponibles que aún no tenga
            result = conn.execute(text("""
                SELECT id, name FROM classes
                WHERE id NOT IN (
                    SELECT class_id FROM teacher_classes WHERE teacher_id = :teacher_id
                )
                ORDER BY id
                LIMIT 3
            """), {"teacher_id": teacher_id})

            available_classes = result.fetchall()

            if available_classes:
                print(f"\n  Asignando {len(available_classes)} clases adicionales...")

                for class_row in available_classes:
                    class_id = class_row[0]
                    class_name = class_row[1]

                    # Asignar clase
                    conn.execute(text(
                        "INSERT INTO teacher_classes (teacher_id, class_id) VALUES (:teacher_id, :class_id)"
                    ), {"teacher_id": teacher_id, "class_id": class_id})

                    print(f"    ✓ Asignada: {class_name} (ID: {class_id})")

                conn.commit()
                print(f"\n✓ Total de clases asignadas a {teacher[1]}: {count + len(available_classes)}")
            else:
                print("\n  No hay más clases disponibles para asignar")

            # Mostrar todas las clases actuales
            result = conn.execute(text("""
                SELECT c.id, c.name
                FROM classes c
                JOIN teacher_classes tc ON tc.class_id = c.id
                WHERE tc.teacher_id = :teacher_id
                ORDER BY c.id
            """), {"teacher_id": teacher_id})

            classes = result.fetchall()
            print(f"\n  Clases de {teacher[1]}:")
            for class_row in classes:
                print(f"    - {class_row[1]} (ID: {class_row[0]})")

    except Exception as e:
        print(f"✗ Error: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    assign_maripi_classes()
