# Documentacion tecnica

Esta carpeta contiene la referencia tecnica compacta del proyecto. Se usa para
resolver dudas de arquitectura, ownership de carpetas y convenciones de codigo.

Si necesitas entender el producto paso a paso, empieza por
[`../doc/README.md`](../doc/README.md). Si ya sabes que vas a tocar una capa
concreta, usa este indice.

El mapa actualizado de flujos funcionales esta en
[`../doc/README.md`](../doc/README.md#mapa-rapido-de-flujos-actuales). Desde ahi
se salta a la guia concreta de auth, roles, vacaciones, exportaciones o
auditoria.

## Arquitectura

- [`architecture/project_structure.md`](./architecture/project_structure.md): estructura oficial por apps, capas y ownership.

## Convenciones

- [`conventions/services.md`](./conventions/services.md): reglas para `views`, `services`, `selectors`, validaciones y efectos secundarios.
- [`conventions/templates.md`](./conventions/templates.md): patron de `pages/`, `partials/` y componentes reutilizables.
- [`conventions/static.md`](./conventions/static.md): CSS, JS, imagenes y promocion de assets compartidos.

## ADR

- [`adr/001-dashboard-ownership.md`](./adr/001-dashboard-ownership.md): propiedad del dashboard.
- [`adr/002-services-selectors.md`](./adr/002-services-selectors.md): uso de servicios y selectors.
- [`adr/003-templates-static-policy.md`](./adr/003-templates-static-policy.md): politica de templates y static.
- [`adr/004-documentation-structure.md`](./adr/004-documentation-structure.md): relacion entre `doc/` y `docs/`.

## Regla practica

- `doc/` explica flujos a personas nuevas.
- `docs/` fija reglas para escribir codigo.
- Los cambios de negocio deben actualizar al menos una guia de `doc/`.
- Los cambios de arquitectura o convencion deben actualizar `docs/` y, si aplica, un ADR.
