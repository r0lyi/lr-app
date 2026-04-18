# ADR 004 - Estructura de documentacion

## Estado

Aceptado.

## Contexto

El proyecto mantiene dos carpetas de documentacion:

- `doc/`
- `docs/`

Ambas son utiles, pero tienen audiencias distintas. Sin una regla clara, una
persona nueva puede no saber donde empezar y una persona senior puede perder
tiempo buscando convenciones concretas.

## Decision

Se mantienen ambas carpetas, con responsabilidades separadas y enlazadas:

- `doc/`: guias de onboarding y flujos funcionales en espanol claro.
- `docs/`: referencia tecnica compacta, convenciones y decisiones ADR.

`doc/README.md` es la puerta de entrada para entender el producto.

`docs/README.md` es la puerta de entrada para escribir codigo siguiendo las
convenciones del repositorio.

## Consecuencias

- Cuando cambie una regla de negocio, se actualiza la guia correspondiente en `doc/`.
- Cuando cambie una convencion tecnica, se actualiza `docs/conventions/`.
- Cuando cambie una decision arquitectonica estable, se crea o actualiza un ADR.
- Los indices deben mantenerse cruzados para que `doc/` y `docs/` no compitan.

## Alternativas descartadas

Unificar todo en una sola carpeta fue descartado porque mezclaria dos necesidades
distintas:

- Aprender como funciona el producto.
- Consultar reglas tecnicas concretas.

Separar por audiencia reduce ruido y hace la documentacion mas facil de mantener.
