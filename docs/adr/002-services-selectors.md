# ADR 002 - Services + Selectors

## Decisión
El proyecto usa `services` para escritura/reglas y `selectors` para lectura.

## Consecuencia
Se evita mezclar lógica de negocio con vistas y no se introduce una capa
repository genérica mientras el ORM de Django siga siendo suficiente.
