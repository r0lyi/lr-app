# Project Structure

## Objetivo
El proyecto se organiza por dominio funcional y separa:

- `views`: HTTP y orquestación ligera
- `services`: casos de uso y escritura
- `selectors`: lectura y consultas ORM
- `templates`: propiedad de cada app
- `static`: global compartido vs assets propios por app

## Reglas rápidas
- `dashboard` es shell y entrypoint, no dueño de pantallas de dominio.
- `core` contiene presentación y utilidades transversales reales.
- Cada app funcional renderiza sus propios `pages/` y compone sus `partials/`.
- Los exports se guardan en `var/exports/`, fuera de código versionado.
