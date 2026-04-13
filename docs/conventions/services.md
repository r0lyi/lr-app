# Services y Selectors

- `views` no contienen reglas de negocio.
- `services` ejecutan casos de uso y validaciones de escritura.
- `selectors` concentran queries de lectura.
- `utils` solo para helpers genéricos, no para lógica de dominio.
- Se prioriza `services + selectors` sobre un repository pattern genérico.
