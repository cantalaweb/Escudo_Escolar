#!/usr/bin/env python3
"""
Script para crear usuarios de prueba en la base de datos
Genera profesores con contraseñas hasheadas correctamente
"""

import sys
from app.core.security import get_password_hash
from app.database.session import get_db
from app.models.database_models import Teacher

# Usuarios de prueba a crear
TEST_USERS = [
    {
        "name": "Gustavo de Básica",
        "email": "gustavo.debasica@escudoescolar.demo",
        "password": "password123",
        "is_admin": True
    },
    {
        "name": "Maripi Olet",
        "email": "maripi.olet@escudoescolar.demo",
        "password": "password123",
        "is_admin": False
    },
    {
        "name": "Admin Principal",
        "email": "admin@escudoescolar.demo",
        "password": "admin123",
        "is_admin": True
    },
    {
        "name": "Carlos Ruiz Sánchez",
        "email": "carlos.ruiz@escudoescolar.demo",
        "password": "password123",
        "is_admin": False
    },
    {
        "name": "Ana Martínez Pérez",
        "email": "ana.martinez@escudoescolar.demo",
        "password": "password123",
        "is_admin": False
    }
]


def update_existing_user(db, email: str, password: str):
    """Actualiza la contraseña de un usuario existente"""
    teacher = db.query(Teacher).filter(Teacher.email == email).first()

    if teacher:
        teacher.password_hash = get_password_hash(password)
        db.commit()
        return True
    return False


def create_or_update_users():
    """Crea o actualiza usuarios de prueba"""
    db = next(get_db())

    print("=" * 70)
    print("CREANDO/ACTUALIZANDO USUARIOS DE PRUEBA")
    print("=" * 70)
    print()

    created_count = 0
    updated_count = 0

    for user_data in TEST_USERS:
        email = user_data["email"]
        password = user_data["password"]

        # Verificar si el usuario ya existe
        existing = db.query(Teacher).filter(Teacher.email == email).first()

        if existing:
            # Actualizar contraseña
            existing.password_hash = get_password_hash(password)
            db.commit()
            updated_count += 1
            status = "✓ ACTUALIZADO"
        else:
            # Crear nuevo usuario
            new_teacher = Teacher(
                name=user_data["name"],
                email=email,
                password_hash=get_password_hash(password),
                is_admin=user_data["is_admin"]
            )
            db.add(new_teacher)
            db.commit()
            created_count += 1
            status = "✓ CREADO"

        admin_badge = " [ADMIN]" if user_data["is_admin"] else ""
        print(f"{status}{admin_badge}")
        print(f"  Nombre: {user_data['name']}")
        print(f"  Email:  {email}")
        print(f"  Pass:   {password}")
        print()

    db.close()

    print("=" * 70)
    print(f"RESUMEN: {created_count} creados, {updated_count} actualizados")
    print("=" * 70)
    print()
    print("Puedes usar estos usuarios para hacer login en:")
    print("  POST http://localhost:8000/auth/login")
    print()
    print("Ejemplo de request:")
    print("""
curl -X POST "http://localhost:8000/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{"email": "admin@escudoescolar.demo", "password": "admin123"}'
    """)


if __name__ == "__main__":
    try:
        create_or_update_users()
    except KeyboardInterrupt:
        print("\n\n✗ Cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
