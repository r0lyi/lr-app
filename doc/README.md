# Documentacion del proyecto `lr-app`

Esta carpeta contiene documentacion pensada para que otro desarrollador pueda entender el proyecto sin tener que leer todo el codigo desde cero.

## Que vas a encontrar aqui

- [`01-estructura-del-proyecto.md`](./01-estructura-del-proyecto.md): explica la organizacion de carpetas, el papel de cada app y el patron que sigue el repositorio.
- [`02-settings-y-configuracion-django.md`](./02-settings-y-configuracion-django.md): explica por que existe `config/settings/`, como se cargan los entornos y que configuraciones importantes de Django usa el proyecto.
- [`03-flujo-auth-login-dni.md`](./03-flujo-auth-login-dni.md): explica el flujo completo de autenticacion con DNI, creacion o recuperacion de contraseña por email y el login final.

## Resumen rapido del stack

- Backend: Django 6
- Base de datos: PostgreSQL
- Variables de entorno: `django-environ`
- Email: backend de Django o Resend
- UI interactiva en auth: HTMX + toasts propios

## Punto de entrada del proyecto

- `manage.py`: comandos de Django
- `config/urls.py`: rutas raiz
- `config/settings/local.py`: settings por defecto en desarrollo
- `apps/users/`: autenticacion y usuario personalizado

## Flujo funcional mas importante

1. Se crea un usuario con email y DNI, pero sin contraseña usable.
2. El usuario solicita acceso o recuperacion con su DNI.
3. El sistema genera un token temporal y envia un email.
4. El usuario abre el enlace, define su contraseña y activa su cuenta.
5. A partir de ese momento entra con `DNI + contraseña`.

## Comandos utiles

```bash
uv run python manage.py migrate
uv run python manage.py runserver
uv run python manage.py test apps.users.tests.test_auth_flow
```

## Recomendacion de lectura

Si eres nuevo en el proyecto, este orden suele funcionar bien:

1. Lee la estructura general.
2. Entiende como se cargan los `settings`.
3. Revisa el flujo de autenticacion.
