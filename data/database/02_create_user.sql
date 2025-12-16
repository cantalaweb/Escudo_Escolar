-- 1. Crear el usuario para el backend
CREATE USER backend_app WITH PASSWORD 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX';

-- 2. Dar permiso para conectarse a la base de datos
GRANT CONNECT ON DATABASE escudo_escolar_db TO backend_app;

-- 3. Dar permiso de uso sobre el esquema 'public' (donde están tus tablas)
GRANT USAGE ON SCHEMA public TO backend_app;

-- 4. Dar permisos sobre las tablas YA EXISTENTES
-- SELECT: Para los GET
-- INSERT: Para los POST (crear)
-- UPDATE: Por si necesitas editar algo (PUT/PATCH)
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO backend_app;

-- 5. ¡MUY IMPORTANTE! Permisos sobre las SECUENCIAS
-- Si no haces esto, los INSERT fallarán porque el usuario no podrá incrementar los IDs (SERIAL)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO backend_app;

-- 6. Configurar permisos automáticos para FUTURAS tablas
-- Esto asegura que si creas una tabla nueva mañana con el admin,
-- el usuario backend_app tenga acceso automáticamente.
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE ON TABLES TO backend_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT ON SEQUENCES TO backend_app;

-- Para borrar el usuario
-- 1. Haz que tu usuario actual (ee_admin) sea "miembro" de backend_app
-- GRANT backend_app TO ee_admin;
-- DROP OWNED BY backend_app; -- Quita sus permisos primero
-- DROP USER backend_app;     -- Borra el usuario



