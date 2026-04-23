# Flujo de autenticacion: login con DNI y contraseña

## Resumen rapido

Este proyecto implementa un flujo donde el usuario entra con `DNI + contraseña`, pero la contraseña no necesariamente existe desde el momento en que se crea el usuario.

La idea es esta:

1. Un usuario existe en base de datos con `email` y `dni`.
2. Si todavia no tiene acceso, o si necesita recuperar su acceso, pide un enlace con su DNI.
3. El sistema genera un token temporal y lo envia por email.
4. El usuario abre el enlace, define una contraseña nueva y su cuenta queda activa.
5. Desde entonces puede iniciar sesion con su DNI y esa contraseña.
6. Despues del login, el sistema todavia decide si va a onboarding o a una home concreta del dashboard.

## Explicado para una persona no tecnica

Imagina esto:

- La empresa ya te ha dado de alta en el sistema.
- El sistema sabe quien eres por tu email y tu DNI.
- Pero aun no tienes una contraseña que solo tu conozcas.
- Entonces escribes tu DNI en la pantalla de acceso.
- Si el sistema reconoce ese DNI, te manda un correo con un enlace temporal.
- Abres ese enlace, eliges tu contraseña y ya puedes entrar.

En otras palabras:

- el DNI identifica al empleado
- el email sirve para demostrar que esa cuenta le pertenece
- la contraseña se crea o se recupera solo a traves del enlace temporal

## Explicado tecnicamente

El flujo se reparte entre modelo, formularios, servicios, backend de autenticacion, vistas, templates y tests.

## 1. Modelo de usuario

El proyecto usa un usuario personalizado en `apps/users/models/user.py`.

Campos importantes:

- `email`: identificador unico de contacto
- `dni`: identificador unico de login
- `is_active`: bloquea el acceso hasta completar activacion
- `activation_token`: token temporal enviado por email
- `token_expires_at`: fecha de expiracion del token
- `registered_at`: fecha en la que termina el proceso de alta

Fragmento clave:

```python
class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    email = models.EmailField(max_length=150, unique=True)
    dni = models.CharField(max_length=20, unique=True, validators=[validate_dni])
    is_active = models.BooleanField(default=False)
    activation_token = models.CharField(max_length=255, blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    registered_at = models.DateTimeField(blank=True, null=True)
```

### Rol por defecto al crear usuario

El metodo `save()` del modelo asigna automaticamente el rol `employee` cuando el usuario se crea por primera vez.

Esto ayuda a que cualquier usuario nuevo ya entre en el sistema con un rol base definido, aunque luego la gestion de permisos pueda crecer mas adelante.

## 2. Como se crea un usuario sin contraseña inicial

El `UserManager` permite crear usuarios sin contraseña usable:

```python
if password:
    user.set_password(password)
else:
    user.set_unusable_password()
```

Esto significa:

- si el usuario nace con contraseña, se hashea y guarda
- si no, Django marca la cuenta con una contraseña inutilizable

Ese detalle encaja muy bien con este flujo, porque permite precargar empleados y dejar que el propio usuario cree su contraseña desde el email.

## 3. Validacion y normalizacion del DNI

Antes de autenticar o enviar emails, el DNI se normaliza y valida en `apps/users/services/validators.py`.

```python
def normalize_dni(value: str) -> str:
    return re.sub(r"[\s-]+", "", value).upper()
```

```python
def validate_dni(value: str) -> None:
    if not DNI_RE.match(normalized):
        raise ValidationError("El DNI debe tener 8 numeros y una letra.")
```

Eso evita problemas como:

- dni en minusculas
- espacios o guiones
- letras incorrectas
- formatos invalidos

Detalle importante para mantenimiento:

- El sistema guarda y compara el DNI normalizado.
- La letra del DNI queda en mayuscula.
- El login debe validar usando ese valor normalizado para evitar diferencias entre `12345678z` y `12345678Z`.

## 4. Formularios implicados

En `apps/users/forms.py` hay tres formularios:

### `RequestActivationForm`

Sirve para pedir el email de activacion o recuperacion.

- pide `dni`
- valida formato
- normaliza el valor

### `SetPasswordForm`

Sirve para definir la contraseña desde el enlace.

- pide `password1`
- pide `password2`
- ejecuta `validate_password`
- comprueba que ambas coinciden

### `LoginForm`

Sirve para iniciar sesion.

- pide `dni`
- pide `password`
- valida y normaliza el DNI

## 5. Solicitud del enlace de activacion o recuperacion

La logica de negocio esta en `apps/users/services/auth_service.py`.

Fragmento principal:

```python
def request_activation(dni: str) -> tuple[bool, str]:
    try:
        user = User.objects.get(dni=dni)
    except User.DoesNotExist:
        return False, "Si el DNI es correcto, recibirás un email."

    token = secrets.token_urlsafe(32)
    user.activation_token = token
    user.token_expires_at = timezone.now() + timedelta(hours=24)
    user.save(update_fields=["activation_token", "token_expires_at"])

    send_activation_email(user.email, token)
    return True, "Si el DNI es correcto, recibirás un email."
```

### Lo que hace este servicio

1. Busca al usuario por DNI.
2. Si no existe, responde con un mensaje generico.
3. Si existe, genera un token seguro.
4. Guarda el token y su expiracion.
5. Envia un correo al email del usuario.

### Por que devuelve el mismo mensaje aunque no exista el DNI

Es una medida de seguridad para no revelar si un usuario existe o no en el sistema.

## 6. Construccion y envio del email

Esto se hace en `apps/users/services/email_service.py`.

### Construccion del enlace

```python
frontend_url = settings.FRONTEND_URL.rstrip("/")
activation_url = f"{frontend_url}/auth/set-password/{token}/"
```

### Contenido que se renderiza

Se usan dos plantillas:

- `templates/emails/activation_email.html`
- `templates/emails/activation_email.txt`

### Proveedores soportados

El servicio puede enviar correos por:

- `console`: util en desarrollo
- `resend`: util para envio real

La seleccion sale de `EMAIL_PROVIDER`, aunque si no se define y existe `RESEND_API_KEY`, el servicio intenta usar Resend.

## 7. Vista para pedir activacion

La vista HTTP es `request_activation_view` en `apps/users/views/auth_views.py`.

Esta vista hace tres cosas importantes:

- valida el formulario
- aplica rate limiting
- devuelve respuesta clasica o respuesta HTMX con toast

### Rate limiting

Antes de procesar la solicitud, la vista comprueba si el cliente ha excedido el numero de intentos permitidos:

```python
if is_rate_limited(
    "activation",
    client_ip=_client_ip(request),
    identifier=identifier,
    limit=settings.ACTIVATION_RATE_LIMIT_ATTEMPTS,
):
    return _rate_limit_response(...)
```

La clave de cache se construye combinando:

- tipo de accion: `activation` o `login`
- IP del cliente
- identificador enviado, en este caso el DNI

La implementacion real esta en `apps/core/utils/rate_limits.py` y usa cache de Django.

## 8. Validacion del token

Cuando el usuario abre el enlace del email entra en la ruta:

```text
/auth/set-password/<token>/
```

La funcion `validate_token(token)` comprueba dos cosas:

- que el token exista en base de datos
- que no haya expirado

```python
user = User.objects.get(
    activation_token=token,
    token_expires_at__gt=timezone.now(),
)
```

Si no encuentra un usuario valido, se renderiza `users/invalid_token.html`.

## 9. Establecer la contraseña

La vista `set_password_view` recibe el token, recupera el usuario valido y procesa `SetPasswordForm`.

Cuando el formulario es correcto, llama a:

```python
def set_password(user: User, password: str) -> None:
    user.set_password(password)
    user.is_active = True
    user.registered_at = timezone.now()
    user.activation_token = None
    user.token_expires_at = None
    user.save(update_fields=[
        "password",
        "is_active",
        "registered_at",
        "activation_token",
        "token_expires_at",
    ])
```

### Efectos importantes de este paso

- la contraseña se guarda hasheada, no en texto plano
- la cuenta se activa
- se registra la fecha de activacion
- el token queda invalidado para no poder reutilizarlo
- se registra en auditoria la accion `Cuenta activada`

La auditoria se registra desde `apps/users/services/auth_service.py` llamando a
`log_user_account_activated(...)`. Esto permite saber cuando un usuario completo
su acceso inicial o recupero su acceso mediante el enlace temporal.

## 10. Login con DNI y contraseña

Aqui hay una sutileza importante.

El modelo `User` tiene:

```python
USERNAME_FIELD = "email"
```

Pero el login de la aplicacion no usa email. Usa DNI. Eso es posible porque Django esta configurado con un backend propio:

```python
AUTHENTICATION_BACKENDS = [
    "apps.users.services.backends.DNIBackend",
    "django.contrib.auth.backends.ModelBackend",
]
```

Y el backend hace esto:

```python
class DNIBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(dni=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None
```

### Traduccion mental

Aunque Django llama al campo de entrada `username`, en este proyecto ese valor contiene el DNI.

## 11. Vista de login

La vista `login_view` hace esto:

1. crea `LoginForm`
2. aplica rate limit
3. llama a `authenticate(...)`
4. si el usuario existe y la contraseña es correcta, hace `login(request, user)`
5. si no, devuelve error

Fragmento clave:

```python
user = authenticate(
    request,
    username=form.cleaned_data["dni"],
    password=form.cleaned_data["password"],
)
```

Si la autenticacion funciona:

- se resetea el rate limit de login
- se crea la sesion con `login(request, user)`
- se redirige a `dashboard:home`, que despues decide el destino final

Si falla:

- se incrementa el contador de intentos
- se muestra el mensaje `DNI o contraseña incorrectos.`

## 12. Por que un usuario inactivo no puede entrar

El backend llama a:

```python
self.user_can_authenticate(user)
```

Como el usuario hereda del sistema de autenticacion de Django y empieza con `is_active = False`, el login no se completa hasta que el proceso de activacion establece `is_active = True`.

## 13. Proteccion de rutas y comportamiento de navegacion

Las vistas de auth usan el decorador `anonymous_required`:

- si el usuario ya esta autenticado y entra en login, activacion o set-password, se le redirige a `dashboard:home`
- eso evita mostrar pantallas de acceso a alguien que ya tiene sesion activa

La pantalla principal del dashboard usa `login_required(login_url="/auth/login/")`:

- si el usuario no esta autenticado, Django lo devuelve al login
- si si lo esta, entra en el dispatcher `dashboard:home`

Ademas, `config/urls.py` tiene una redireccion raiz:

- `"/"` envia a `dashboard:home` si hay sesion
- `"/"` envia al login si no la hay

En conjunto, estas reglas hacen que la navegacion basica del sistema sea coherente sin tener que repetir validaciones en cada vista.

## 13.1. Lo que ocurre justo despues del login

El login no decide por si solo si el usuario ve ya su panel final. Solo crea la sesion y envia al dispatcher principal:

```python
login(request, user)
return redirect("dashboard:home")
```

Desde ahi, `dashboard:home` aplica la siguiente logica:

- si el rol principal es `admin`, entra a `dashboard:admin-home`
- si el rol principal es `rrhh`, entra a `dashboard:rrhh-home`
- si el rol principal es `employee`, primero comprueba si existe `employee_profile`
- si no existe esa ficha, envia a `employees:onboarding`

Ese segundo tramo ya no pertenece al login puro. Forma parte del flujo de roles y post-login, que se explica con detalle en `doc/04-flujo-roles-y-post-login.md`.

## 14. Logout

El logout es simple:

```python
if request.method == "POST":
    logout(request)
return redirect("auth:login")
```

Con eso Django destruye la sesion del usuario y lo devuelve a la pantalla de login.

## 15. Donde entran HTMX y los toasts

Las pantallas de login y activacion usan HTMX para mejorar la experiencia sin tener que recargar toda la pagina en algunos casos.

Ejemplo desde `apps/users/templates/users/partials/auth/login_panel.html`:

```html
<form
  action="{% url 'auth:login' %}"
  hx-post="{% url 'auth:login' %}"
  hx-target="#ui-toast-root"
  hx-swap="innerHTML"
  hx-indicator="#login-btn"
>
```

### Que significa esto

- el formulario funciona con POST normal
- pero si HTMX esta activo, envia la peticion por AJAX
- la respuesta puede reemplazar el contenedor de toasts
- el boton puede mostrar un indicador de carga

### Respuesta especial al login exitoso con HTMX

```python
response = HttpResponse()
response["HX-Redirect"] = "/dashboard/"
return response
```

Eso le dice a HTMX que haga una navegacion completa hacia el dispatcher del dashboard, que despues resolvera el destino final segun rol y perfil.

### Como se muestran los toasts

- HTML del toast: `templates/components/feedback/toast_card.html`
- JS de comportamiento: `static/js/core/toast.js`

## 16. Secuencia completa del primer acceso

```text
Administrador crea usuario
    -> usuario queda con email + DNI
    -> sin contraseña usable
    -> is_active = False

Usuario escribe su DNI en /auth/activate/
    -> formulario valida DNI
    -> se aplica rate limit
    -> se genera token temporal
    -> se envia email con enlace

Usuario abre /auth/set-password/<token>/
    -> se valida que el token exista
    -> se valida que no haya expirado
    -> usuario define contraseña
    -> is_active pasa a True
    -> token se invalida

Usuario entra en /auth/login/
    -> backend busca por DNI
    -> compara hash de contraseña
    -> crea sesion
    -> redirige a /dashboard/
    -> dashboard resuelve el rol principal
    -> si es employee sin ficha, entra en onboarding
    -> si ya tiene ficha o pertenece a otro rol, entra en su panel
```

## 17. Secuencia de recuperacion de contraseña

En la implementacion actual, el mismo flujo de activacion sirve tambien para recuperar el acceso:

```text
Usuario ya existente
    -> pide enlace con su DNI
    -> recibe token temporal
    -> abre set-password
    -> define una nueva contraseña
    -> el token anterior deja de ser valido
```

No hay dos flujos separados; hay un flujo reutilizable.

## 18. Seguridad aplicada en este flujo

### Medidas ya presentes

- validacion fuerte del DNI
- normalizacion del DNI con letra en mayuscula
- contraseña hasheada con `set_password`
- usuario inactivo hasta terminar activacion
- token con expiracion de 24 horas
- invalidacion del token al usarlo
- mensaje generico para no revelar si el DNI existe
- rate limit por IP + identificador
- CSRF activo en formularios POST
- auditoria de activacion de cuenta

### Detalle tecnico importante

En la implementacion actual el token se guarda en la base de datos en el campo `activation_token` y luego se limpia al usarse. Es una estrategia valida y simple de entender, aunque depende de proteger correctamente la base de datos y las copias de seguridad.

## 19. Test que valida el flujo

El archivo `apps/users/tests/test_auth_flow.py` prueba el caso feliz completo:

1. solicita activacion
2. comprueba que se envia un email
3. recupera el token generado
4. establece una contraseña
5. confirma que el usuario queda activo
6. hace login con DNI y contraseña
7. verifica que el flujo continue hacia onboarding cuando el empleado aun no tiene ficha interna

Comando:

```bash
uv run python manage.py test apps.users.tests.test_auth_flow
```

## 20. Archivos clave para entender auth

- `apps/users/models/user.py`
- `apps/users/forms.py`
- `apps/users/services/validators.py`
- `apps/users/services/auth_service.py`
- `apps/users/services/email_service.py`
- `apps/users/services/backends.py`
- `apps/users/views/auth_views.py`
- `apps/users/urls.py`
- `apps/users/templates/users/pages/login.html`
- `apps/users/templates/users/pages/request_activation.html`
- `apps/users/templates/users/pages/set_password.html`
- `apps/users/templates/users/partials/auth/`
- `templates/emails/activation_email.html`
- `apps/users/tests/test_auth_flow.py`

## Explicacion final en una frase

Este auth funciona como una combinacion de:

- identificacion por DNI
- verificacion de propiedad por email
- activacion o recuperacion mediante token temporal
- acceso persistente mediante sesion de Django
- y un segundo paso de resolucion de destino dentro del dashboard
