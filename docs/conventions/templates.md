# Templates

- `templates/` global:
  - `base.html`
  - `layouts/`
  - `components/`
  - `emails/`
  - `errors/`
- `apps/<app>/templates/<app>/pages/`: wrappers completos renderizados por vistas.
- `apps/<app>/templates/<app>/partials/`: fragmentos internos de la app.
- Una feature app no debe incluir templates de otra feature app.
- Si un fragmento se reutiliza entre dominios, se promociona a `templates/components/`.
