# Templates

Esta convencion define como organizar HTML para que las pantallas sean faciles
de mantener y no acumulen codigo duplicado.

## Carpetas globales

`templates/` contiene piezas compartidas por varias apps.

Uso esperado:

- `templates/base.html`: base comun.
- `templates/layouts/`: layouts globales como el dashboard.
- `templates/components/`: componentes reutilizables.
- `templates/emails/`: emails transversales.
- `templates/errors/`: paginas de error.

Un componente debe vivir aqui cuando se usa en mas de una app o cuando queremos
forzar consistencia visual.

Ejemplos de componentes globales:

- Boton primario.
- Boton secundario.
- Boton de filtro.
- Paginacion.
- Modal reutilizable.
- Badges de estado.

## Templates por app

Cada app funcional es propietaria de sus pantallas.

Patron recomendado:

```text
apps/<app>/templates/<app>/
  pages/
    <screen>.html
  partials/
    <feature>/
      <fragment>.html
```

`pages/`:

- Wrapper completo renderizado por una vista.
- Extiende el layout correspondiente.
- Incluye CSS/JS especifico si lo necesita.
- Compone partials.

`partials/`:

- Fragmentos internos de una app.
- Se nombran por feature o pantalla.
- No deberian conocer detalles de apps hermanas.

## Dashboard

`apps/dashboard` es shell de navegacion y entrada por rol.

Regla:

- El dashboard decide layout, header, sidebar y home por rol.
- Las pantallas de dominio viven en su app funcional.
- Una pantalla de vacaciones no debe vivir en dashboard solo porque se vea dentro del dashboard.

Ejemplo:

- Correcto: `apps/vacations/templates/vacations/pages/create_request.html`
- Incorrecto: `apps/dashboard/templates/dashboard/pages/create_request.html`

## Reutilizacion

Cuando dos pantallas copian el mismo bloque, revisar si debe ser componente.

Promocionar a `templates/components/` si:

- Se usa en mas de una app.
- Tiene estilo y comportamiento comun.
- Cambiarlo en un sitio deberia cambiarlo en todos.

Mantener como partial local si:

- Solo pertenece a una feature.
- Depende mucho del contexto de esa app.
- No tiene valor fuera de esa pantalla.

## Formularios

Los formularios deben usar estructura visual consistente.

Buenas practicas:

- Inputs con label visible.
- Errores cerca del campo.
- Boton primario para confirmar.
- Boton secundario para cancelar o volver.
- Textos de ayuda claros, especialmente en auth y onboarding.

Evitar:

- Mezclar estilos inline.
- Crear botones diferentes por pantalla sin necesidad.
- Ocultar labels si el placeholder es la unica pista.
- Repetir modales completos si ya existe un patron global.

## Modales

Los modales deben ser cancelables.

Checklist:

- Boton de cerrar `X`.
- Boton secundario de cancelar.
- Cierre por overlay si el patron actual lo permite.
- Foco visual claro.
- Texto de accion irreversible escrito de forma directa.

Ejemplo de uso:

- Confirmar eliminacion de solicitud pendiente.
- Crear usuario desde gestion admin.
- Editar rol y acceso de usuario.

## Listas y tablas

Las listas deben compartir patrones:

- Filtros arriba.
- Boton filtrar y limpiar consistentes.
- Paginacion compartida.
- Badges de estado en espanol.
- Acciones al final de la fila.

No traducir estados en cada template si ya existe helper, filtro o contexto
preparado.

## Accesibilidad basica

Mantener:

- Textos legibles.
- Labels visibles.
- Botones con texto o `aria-label`.
- Contraste suficiente.
- Orden visual coherente en responsive.

Esto es especialmente importante porque la aplicacion la usan personas con
distintas edades y niveles de familiaridad tecnologica.
