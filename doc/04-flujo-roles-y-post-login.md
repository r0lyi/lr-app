# Flujo de roles y post-login

## Resumen rapido

En este proyecto, hacer login no significa automaticamente entrar en una pantalla final.

Despues de autenticar al usuario:

1. Django crea la sesion.
2. El sistema redirige a `/dashboard/`.
3. `/dashboard/` resuelve el rol principal del usuario.
4. Si el usuario es `employee`, comprueba si ya existe su ficha `Employee`.
5. Segun ese estado, lo manda a onboarding o a su panel.

Ese detalle es importante porque el login y el destino final estan separados a proposito.

## Modelo mental de roles

El sistema maneja tres roles de aplicacion:

- `employee`
- `rrhh`
- `admin`

Un usuario puede tener varios roles asociados en la relacion many-to-many, pero el sistema trabaja con la idea de `rol principal`.

La prioridad esta definida asi:

```python
PRIMARY_ROLE_PRIORITY = ("admin", "rrhh", "employee")
```

Eso significa:

- si un usuario tiene `admin` y `rrhh`, se trata como `admin`
- si tiene `rrhh` y `employee`, se trata como `rrhh`
- si solo tiene `employee`, se trata como `employee`

La resolucion real vive en `apps/users/selectors/roles.py`.

## Rol asignado vs rol principal resuelto

Conviene separar dos conceptos:

### Rol asignado

Es lo que existe en la tabla intermedia `user_role`.

Ejemplos:

- un usuario nuevo queda con `employee`
- un administrador puede tener `admin`
- un usuario avanzado podria terminar teniendo mas de un rol

### Rol principal resuelto

Es el rol que el sistema usa para decidir navegacion y permisos.

Fragmento simplificado:

```python
def get_primary_role(user):
    role_names = get_user_role_names(user)

    if getattr(user, "is_superuser", False):
        return "admin"

    for role_name in PRIMARY_ROLE_PRIORITY:
        if role_name in role_names:
            return role_name
    return None
```

Dos ideas clave:

- el orden importa
- un `superuser` de Django se trata como `admin` incluso si la relacion de roles no se ha sincronizado

## Por que todo usuario nuevo nace como `employee`

El modelo `User` asigna automaticamente el rol `employee` en su primer guardado.

La intencion es sencilla:

- cualquier usuario nuevo entra con una base funcional minima
- el flujo post-login ya sabe que hacer con un empleado
- mas adelante RRHH o admin pueden reasignar el rol si hace falta

Fragmento reducido:

```python
if is_new:
    default_role = Role.objects.get(name=DEFAULT_ROLE_NAME)
    self.roles.add(default_role)
```

No significa que todo usuario vaya a quedarse como empleado para siempre. Solo marca el punto de partida.

## Gestion administrativa de usuarios

El panel de administracion funcional permite crear y editar usuarios sin entrar
directamente a Django Admin.

La gestion vive principalmente en:

- `apps/users/views/admin/list.py`: listado y modal de alta rapida.
- `apps/users/views/admin/edit.py`: edicion de rol y estado.
- `apps/users/services/admin/management.py`: reglas de negocio de administracion.

Reglas importantes:

- Al crear un usuario desde el panel admin se pide solo `DNI` y `email`.
- El usuario nace inactivo y sin contraseña usable.
- Se envia un enlace de activacion para que la persona configure su contraseña.
- El usuario nuevo mantiene `employee` como rol base hasta que un admin lo cambie.
- Cambiar rol significa reemplazar el rol funcional, no añadir roles acumulados.
- No se permite quitar el ultimo admin funcional del sistema.
- No se permite activar manualmente una cuenta sin contraseña usable.
- No se permite desactivar al ultimo admin activo.

Acciones de administracion que generan auditoria:

- crear usuario
- cambiar rol principal
- activar o desactivar acceso
- cambiar departamento si se usa desde flujos internos preparados

## El contrato real de las rutas

Estas son las rutas que definen el flujo post-login:

### `/auth/login/`

- valida DNI y contraseña
- autentica mediante `DNIBackend`
- crea la sesion con `login(request, user)`
- redirige a `/dashboard/`

### `/dashboard/`

- no es una home final
- funciona como dispatcher autenticado
- decide el destino real segun rol principal y estado del perfil

### `/employees/onboarding/`

- solo tiene sentido para usuarios autenticados
- recoge o actualiza la ficha interna del empleado
- al guardar correctamente, redirige otra vez a `/dashboard/`

### `/dashboard/employee/`

- exige rol `employee`
- ademas exige que exista `employee_profile`
- si no existe, devuelve al onboarding

### `/dashboard/rrhh/`

- exige rol `rrhh`
- tambien permite `admin` mediante `allow_admin=True`

### `/dashboard/admin/`

- exige rol `admin`

## Que pasa justo despues de `login(request, user)`

La vista de login termina aqui:

```python
login(request, user)
return redirect("dashboard:home")
```

Eso no cierra el flujo. Solo abre el tramo autenticado.

La vista `home_view` del dashboard es la que toma la decision final:

```python
primary_role = get_primary_role(request.user)

if primary_role == "admin":
    return redirect("dashboard:admin-home")

if primary_role == "rrhh":
    return redirect("dashboard:rrhh-home")

if primary_role != "employee":
    return redirect("dashboard:error-400")
```

Y para `employee` aplica una comprobacion extra:

```python
try:
    request.user.employee_profile
except Employee.DoesNotExist:
    return redirect("employees:onboarding")
```

Traduccion mental:

- el login solo confirma identidad
- el dashboard decide a donde pertenece navegar
- el onboarding actua como puerta obligatoria para empleados incompletos

## Por que un `employee` sin `employee_profile` entra en onboarding

La aplicacion separa dos niveles de informacion:

- `User`: identidad, credenciales, estado de activacion y roles
- `Employee`: datos internos necesarios para operar vacaciones y panel de empleado

Mientras exista solo `User`, el sistema sabe que la persona puede autenticarse, pero todavia no tiene toda la informacion funcional que necesita el modulo de empleados.

Por eso onboarding pide:

- nombre
- apellidos
- email
- telefono
- fecha de ingreso

Y al guardar:

- crea la ficha `Employee` si no existia
- actualiza el email del `User` si ha cambiado
- redirige otra vez a `dashboard:home`
- registra cambios de datos de usuario en el historial de actividad

Ese ultimo redirect es deliberado: deja que el mismo dispatcher confirme que el usuario ya puede entrar al panel correcto.

## Proteccion de paneles por rol

Las vistas del dashboard usan `role_required(...)`.

El comportamiento general es:

- si el rol encaja, deja pasar
- si `allow_admin=True` y el usuario es admin, deja pasar
- si no encaja, redirige a `dashboard:home`
- si no hay sesion, Django envia al login

Fragmento simplificado:

```python
if current_role == normalized_role:
    return view_func(request, *args, **kwargs)

if allow_admin and current_role == "admin":
    return view_func(request, *args, **kwargs)

return redirect("dashboard:home")
```

Esto explica dos comportamientos importantes:

- un `employee` no puede abrir RRHH ni admin
- un `admin` si puede abrir RRHH

## Navegacion generada por presentacion compartida

El menu lateral no se construye a mano en cada template.

La configuracion vive en `apps/core/presentation/dashboard/`:

- `navigation.py`: entradas del menu por rol.
- `display.py`: etiquetas, iniciales y avatar textual.
- `notifications.py`: resumen de notificaciones visibles.
- `context.py`: `build_dashboard_base_context(...)` para layout, header y sidebar.

Eso aporta dos ventajas:

- el layout del dashboard mantiene una estructura uniforme
- si el menu crece, se extiende desde un punto central

## Escenarios tipicos

### 1. Usuario nuevo activa cuenta y entra en onboarding

Secuencia:

```text
Usuario activa su contraseña
    -> hace login con DNI + contraseña
    -> /dashboard/ detecta rol employee
    -> no existe employee_profile
    -> redirige a /employees/onboarding/
```

Este es el caso normal del primer acceso de un empleado.

### 2. Empleado con perfil completo entra directo a su panel

Secuencia:

```text
Empleado autenticado
    -> /dashboard/ detecta rol employee
    -> employee_profile existe
    -> redirige a /dashboard/employee/
```

### 3. Usuario RRHH entra a su panel

Secuencia:

```text
Usuario con rol rrhh
    -> /dashboard/ resuelve rrhh
    -> redirige a /dashboard/rrhh/
```

El onboarding no participa porque esa comprobacion solo existe para `employee`.

### 4. Admin entra a su panel y tambien puede abrir RRHH

Secuencia:

```text
Usuario con rol admin
    -> /dashboard/ resuelve admin
    -> redirige a /dashboard/admin/
    -> tambien puede abrir /dashboard/rrhh/
```

Ese acceso adicional a RRHH sale de `@role_required("rrhh", allow_admin=True)`.

### 5. Usuario sin rol valido acaba en error 400

Si `get_primary_role(user)` no consigue resolver un rol:

- `/dashboard/` redirige a `dashboard:error-400`
- esa vista devuelve un `400` real si el usuario sigue sin rol valido

Es un caso defensivo para configuraciones inconsistentes.

## Resumen rapido de destino

| Estado del usuario | Destino |
| --- | --- |
| No autenticado | `/auth/login/` |
| Autenticado con rol `employee` y sin ficha `Employee` | `/employees/onboarding/` |
| Autenticado con rol `employee` y ficha completa | `/dashboard/employee/` |
| Autenticado con rol `rrhh` | `/dashboard/rrhh/` |
| Autenticado con rol `admin` | `/dashboard/admin/` |
| Autenticado sin rol principal resoluble | `/dashboard/error-400/` |

## Tests que ya describen este comportamiento

Los tests mas utiles para leer este flujo son:

- `apps/dashboard/tests/test_dashboard_routing.py`
- `apps/dashboard/tests/test_dashboard_permissions.py`
- `apps/dashboard/tests/test_dashboard_navigation.py`
- `apps/users/tests/test_auth_flow.py`
- `apps/dashboard/tests/test_admin_users.py`
- `apps/audit/tests/test_audit_log_view.py`

En conjunto cubren:

- el primer acceso sin perfil
- la entrada al panel correcto por rol
- la proteccion de rutas
- la navegacion mostrada en cada dashboard

## Archivos clave para otro desarrollador

- `apps/users/selectors/roles.py`
- `apps/core/utils/decorators.py`
- `apps/dashboard/views/view_dashboard.py`
- `apps/dashboard/views/view_admin.py`
- `apps/dashboard/views/__init__.py`
- `apps/employees/views/view_employee_home.py`
- `apps/vacations/views/rrhh/requests_management.py`
- `apps/core/presentation/dashboard/context.py`
- `apps/core/presentation/dashboard/navigation.py`
- `apps/employees/views/onboarding.py`
- `apps/dashboard/tests/`

## Idea final

El post-login de este proyecto funciona como un dispatcher de estado:

- primero confirma que el usuario es quien dice ser
- despues decide que pantalla puede ver realmente segun su rol y los datos internos que ya haya completado
