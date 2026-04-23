# Static

Esta convencion define como organizar CSS, JavaScript, imagenes y assets para
mantener una interfaz consistente.

## Static global

`static/` contiene assets compartidos.

Uso esperado:

- `static/css/`: base visual, layout, componentes y tokens globales.
- `static/js/`: comportamiento reutilizable o transversal.
- `static/images/`: imagenes compartidas como fondos, logos o recursos de marca.

Debe vivir aqui si:

- Se usa en mas de una app.
- Define una regla visual de sistema.
- Forma parte de la identidad del producto.
- Evita duplicar estilos entre pantallas.

## Static por app

`apps/<app>/static/<app>/` contiene assets especificos de esa app.

Patron recomendado:

```text
apps/<app>/static/<app>/
  css/
    pages/
      <screen>.css
  js/
    pages/
      <screen>.js
```

Debe vivir aqui si:

- Solo se usa en una app.
- Solo afecta a una pantalla concreta.
- Depende de markup muy especifico de esa app.

## CSS global vs CSS de pagina

CSS global:

- Botones.
- Inputs base.
- Modales.
- Header y sidebar.
- Paginacion.
- Badges.
- Utilidades de layout compartidas.

CSS de pagina:

- Composicion especifica de una pantalla.
- Grid propio de un formulario complejo.
- Ajustes visuales que no se repiten.
- Estados visuales de una feature.

Regla practica:

- Si el estilo se repite, sube a global.
- Si el estilo solo existe por una pantalla, dejalo en la app.

## Componentes visuales

Los estilos de componentes reutilizables deben tener una clase estable y no
depender de un template concreto.

Ejemplos:

- `.btn-primary`
- `.btn-secondary`
- `.filter-actions`
- `.status-badge`
- `.dashboard-pagination`
- `.modal`

Evitar:

- Crear una variante nueva de boton para cada pantalla.
- Cambiar colores de estado en templates.
- Usar selectores demasiado profundos que rompen al reordenar HTML.

## JavaScript

JavaScript debe ser pequeno y especifico.

Buenas practicas:

- Usar `data-*` para conectar comportamiento con HTML.
- Evitar depender de texto visible para seleccionar elementos.
- Separar comportamiento de modales, filtros o acordeones si se reutiliza.
- No duplicar reglas de negocio que ya valida el backend.

Ejemplos:

- Abrir/cerrar modal.
- Confirmar eliminacion.
- Mostrar/ocultar panel desplegable de alertas.
- Actualizar resumen visual antes de enviar formulario.

## Imagenes y fondos

Las imagenes compartidas viven en `static/images/`.

Reglas:

- Usar nombres descriptivos.
- Evitar imagenes enormes sin optimizar.
- Si una imagen es de identidad o auth, documentar donde se usa.
- No meter imagenes de prueba si no son parte del producto.

Ejemplo actual:

- `static/images/oficina.jpg`: fondo visual usado en pantallas de auth.

## Responsive

Los estilos responsive deben estar cerca del CSS que modifican.

Checklist minimo:

- Desktop.
- Tablet.
- Movil.
- Moviles con barra de navegacion tactil inferior.

Regla de UX:

- Las acciones principales deben seguir visibles.
- El sidebar movil no debe tapar botones criticos.
- El boton de cerrar sesion debe tener margen inferior suficiente.
- Los textos pequenos deben revisarse pensando en usuarios de mas de 40 anos.

## Promocion de assets

Antes de crear un nuevo CSS/JS global:

- Confirmar que se usara en mas de una app.
- Revisar si ya existe componente parecido.
- Nombrar de forma generica.
- Evitar mezclar reglas de dominio dentro de componentes globales.

Antes de dejar un asset local:

- Confirmar que no se repite.
- Confirmar que su nombre indica la pantalla o feature.
- Confirmar que no rompe la consistencia visual del sistema.
