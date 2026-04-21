# Sistema de Solicitud de Días Vacaciones

# Índice {#índice}

[**Índice	2**](#índice)

[**1 Introducción	3**](#1-introducción)

[**2 Resumen Ejecutivo	4**](#2-resumen-ejecutivo)

[**3 Objetivos del proyecto	4**](#3-objetivos-del-proyecto)

[3.1 Objetivos Generales	4](#3.1-objetivos-generales)

[3.2 Objetivos para los empleados	5](#3.2-objetivos-para-los-empleados)

[3.3 Objetivos para el departamento de RRHH	5](#3.3-objetivos-para-el-departamento-de-rrhh)

[3.4 Objetivos para el administrador	5](#3.4-objetivos-para-el-administrador)

[**4 Funcionalidades del sistema	5**](#4-funcionalidades-del-sistema)

[4.1 Empleado (employe)	6](#4.1-empleado-\(employe\))

[4.2 Recursos Humanos (RRHH)	6](#4.2-recursos-humanos-\(rrhh\))

[4.3 Administrador(ADMIN)	7](#4.3-administrador\(admin\))

[**5 Flujo de uso de la aplicación	8**](#5-flujo-de-uso-de-la-aplicación)

[5.1 Inicio	8](#5.1-inicio)

[5.2 Empleado accede al sistema	8](#5.2-empleado-accede-al-sistema)

[5.3 Crea solicitud de vacaciones	8](#5.3-crea-solicitud-de-vacaciones)

[5.4 Solicitud registrada (pendiente)	9](#5.4-solicitud-registrada-\(pendiente\))

[5.5 Sistema detecta posibles conflictos	9](#5.5-sistema-detecta-posibles-conflictos)

[5.6 RRHH visualiza solicitudes	9](#5.6-rrhh-visualiza-solicitudes)

[5.7 RRHH exporta solicitudes a Excel	10](#5.7-rrhh-exporta-solicitudes-a-excel)

[5.8 Evaluación externa (implícita en el proceso)	10](#5.8-evaluación-externa-\(implícita-en-el-proceso\))

[5.9 RRHH actualiza el estado de la solicitud	10](#5.9-rrhh-actualiza-el-estado-de-la-solicitud)

[5.10  Solicitud estado “aprobado”	10](#5.10-solicitud-estado-“aprobado”)

[5.11 Solicitud estado “rechazado”	11](#5.11-solicitud-estado-“rechazado”)

[5.12 Sistema notifica al empleado	11](#5.12-sistema-notifica-al-empleado)

[5.13 Fin	11](#5.13-fin)

[6 Mockups / Diseño de pantallas	11](#6-mockups-/-diseño-de-pantallas)

[7 Indicadores de éxito	11](#7-indicadores-de-éxito)

[7.1 Reducción del tiempo de gestión	12](#7.1-reducción-del-tiempo-de-gestión)

[7.2 Número de solicitudes gestionadas	12](#7.2-número-de-solicitudes-gestionadas)

[7.3 Porcentaje de solicitudes resueltas	12](#7.3-porcentaje-de-solicitudes-resueltas)

[7.4 Reducción de errores o incidencias	12](#7.4-reducción-de-errores-o-incidencias)

[7.5 Uso del sistema por parte de empleados	12](#7.5-uso-del-sistema-por-parte-de-empleados)

[7.6 Eficiencia en la generación de reportes	12](#7.6-eficiencia-en-la-generación-de-reportes)

[7.7 Satisfacción del usuario	12](#7.7-satisfacción-del-usuario)

[8 Plan de implantación	13](#8-plan-de-implantación)

[9 Evolución Futura	13](#9-evolución-futura)

# 1 Introducción {#1-introducción}

El **Sistema de Solicitud de Vacaciones** es una plataforma digital diseñada para simplificar y optimizar el proceso mediante el cual los empleados solicitan y gestionan sus periodos de descanso anual dentro de la empresa.

Actualmente, la gestión de vacaciones puede implicar registros manuales mediante documentos, lo que puede generar demoras, errores en la información y dificultades para mantener un control claro del calendario laboral. Esta situación impacta tanto en la planificación operativa como en la experiencia de los empleados.

La solución propuesta consiste en la implantación de una aplicación web corporativa que permitirá registrar cada solicitud de vacaciones de forma estructurada, transparencia y una comunicación directa entre los empleados y el departamento de Recursos Humanos.

# 2 Resumen Ejecutivo {#2-resumen-ejecutivo}

La gestión de solicitudes de vacaciones es un proceso dentro de la organización, ya que impacta directamente en la planificación de equipos, la continuidad operativa y la satisfacción de los empleados. En la situación actual, este proceso se realiza mediante métodos no centralizados, lo que puede generar dificultades en el seguimiento, control y análisis de la información.

Ante este contexto, se propone el desarrollo de una aplicación web corporativa que permita gestionar de forma estructurada y eficiente todas las solicitudes de vacaciones. La solución centralizará la información en una única plataforma, facilitando tanto a los empleados como al departamento de Recursos Humanos el acceso, seguimiento y gestión de cada solicitud.

A través del sistema, los empleados podrán registrar sus solicitudes de vacaciones de manera sencilla, mientras que RRHH dispondrá de un entorno desde el cual podrá visualizar todas las peticiones, exportarlas en formato Excel y tomar decisiones informadas basadas en una visión global de la organización. El sistema, además, incorporará mecanismos de detección de posibles conflictos y notificará automáticamente a los empleados sobre el estado final de sus solicitudes.

La implantación de esta solución permitirá reducir la carga administrativa, minimizar errores derivados de procesos manuales y mejorar la transparencia en la gestión interna. Asimismo, proporcionará una base sólida para la toma de decisiones y la planificación de recursos, alineándose con los objetivos de digitalización y eficiencia de la empresa.

# 3 Objetivos del proyecto {#3-objetivos-del-proyecto}

La herramienta buscará mejorar tanto la operativa interna del departamento de Recursos Humanos como la experiencia de los trabajadores al momento de planificar su periodo de vacaciones.

## 3.1 Objetivos Generales {#3.1-objetivos-generales}

* Interfaz intuitiva y moderna.  
* Centralizar en una única plataforma toda la información relacionada con las vacaciones del personal.  
* Reducir la carga administrativa asociada a la gestión manual de solicitudes.  
* Minimizar errores derivados de comunicaciones informales o registros dispersos  
* Facilitar la planificación de equipos mediante una visión clara de ausencias.  
* Disponer de información actualizada y exportable para reportes y seguimiento.

## 3.2 Objetivos para los empleados {#3.2-objetivos-para-los-empleados}

* Poder solicitar vacaciones de manera rápida y sencilla.  
* Informar : Solicitudes pendientes , días disponibles y última resolución.  
* Conocer en todo momento el estado de su petición.  
* Tener acceso al historial de solicitudes realizadas.  
* FIltrar historial de solicitudes por : fecha inicio , fecha final y estado  
* Modificación de datos personales.

## 3.3 Objetivos para el departamento de RRHH {#3.3-objetivos-para-el-departamento-de-rrhh}

* Contar con una tabla de revisión de solicitudes.  
* Filtrar el panel de revisión de solicitudes por : nombre, apellido ,fecha inicio ,fecha final, estado.  
* Agilizar la toma de decisiones exportando en un excel las solicitudes pendientes.  
* Informar de advertencia de solapamiento.  
* Mantener un histórico organizado y fácilmente consultable.  
* Edición de solicitudes fácil y rápidas.  
* Historial de exportaciones de Excel realizadas.  
* Filtrar Historial de exportaciones , poder descargarlos o verlos.

## 3.4 Objetivos para el administrador {#3.4-objetivos-para-el-administrador}

* Gestionar Usuarios rapido y facil.


# 4 Funcionalidades del sistema  {#4-funcionalidades-del-sistema}

El Sistema de Solicitud de Vacaciones incorpora un conjunto de funcionalidades orientadas a simplificar la gestión administrativa, mejorar la comunicación interna y garantizar un control centralizado de la información.

Las capacidades de la plataforma están organizadas según el tipo de **ROLE**, asegurando que cada perfil disponga únicamente de las herramientas necesarias para el desempeño de sus responsabilidades.

### 4.1 Empleado (employe) {#4.1-empleado-(employe)}

|  |  |
| :---- | :---- |
| Creación de solicitudes | El empleado podrá registrar una nueva petición seleccionando el rango de fechas en el que desea disfrutar sus vacaciones. La solicitud quedará automáticamente almacenada en el sistema para su revisión por parte de RRHH. |
| Consulta Historial | El usuario tendrá acceso a un listado completo de todas las solicitudes realizadas anteriormente, permitiendo revisar fechas, estados y posibles modificaciones. |
| Seguimiento del estado | Cada solicitud mostrará claramente su situación actual, pudiendo encontrarse en estados como: Pendiente de revisión Aprobada Denegada  |
| Recepción de Notificaciones \*\*\* | Cuando RRHH tome una decisión, el empleado será informado a través de la propia plataforma, evitando la necesidad de comunicaciones adicionales por correo electrónico u otros medios. |

### 

### 

### 4.2 Recursos Humanos (rrhh) {#4.2-recursos-humanos-(rrhh)}

| Panel general de solicitudes | Visualización centralizada de todas las peticiones registradas en el sistema, con acceso inmediato a la información de cada empleado y las fechas solicitadas. |
| :---- | :---- |
| Búsqueda y filtros | El sistema permitirá localizar solicitudes de forma rápida mediante criterios como: Empleado Intervalo de fechas Estado de la solicitud  |
| Edición de solicitudes | Después de llegar a un acuerdo con el empleado puede editar la solicitud :  cambiando el estado cambiando las fechas  |
| Exportación de información | La plataforma permitirá generar archivos en formato Excel con el detalle de las solicitudes, facilitando reportes, controles internos y análisis posteriores. |

### 4.3 Administrador(admin) {#4.3-administrador(admin)}

| Gestión de usuarios | Alta de nuevos empleados. Modificación de datos existentes. Activación o desactivación de cuentas. |
| :---- | :---- |
| Supervisión global | Acceso completo a la información para garantizar el correcto uso de la plataforma y la coherencia de los datos registrados. |

# 5 Flujo de uso de la aplicación {#5-flujo-de-uso-de-la-aplicación}

![][image1]

### 5.1 Inicio {#5.1-inicio}

El proceso comienza cuando el empleado decide gestionar una nueva solicitud de vacaciones dentro del sistema.

### 5.2 Empleado accede al sistema {#5.2-empleado-accede-al-sistema}

El empleado inicia sesión en la plataforma utilizando sus credenciales corporativas.

En este punto:

* Se valida su identidad.

* Accede a su panel personal.

* Puede visualizar su historial de solicitudes anteriores.

### 5.3 Crea solicitud de vacaciones {#5.3-crea-solicitud-de-vacaciones}

El empleado completa el formulario indicando:

* Fecha de inicio del periodo de vacaciones.

* Fecha de fin.

* (En caso de existir) información adicional requerida por la empresa.

Una vez enviada, la solicitud queda registrada automáticamente.

### 5.4 Solicitud registrada (pendiente) {#5.4-solicitud-registrada-(pendiente)}

El sistema almacena la solicitud en la base de datos y le asigna el estado inicial:

**“Pendiente”**

Esto significa que:

* Aún no ha sido evaluada por RRHH.

* Está a la espera de revisión.

* Forma parte del listado general de solicitudes.

### 5.5 Sistema detecta posibles conflictos {#5.5-sistema-detecta-posibles-conflictos}

El sistema realiza una verificación automática para identificar:

* Coincidencias con otras solicitudes.

* Posibles solapamientos en el mismo periodo.

* Riesgos de exceso de ausencias simultáneas.

En caso de detectar alguna situación relevante, genera una advertencia visual para RRHH.

Importante:  
 El sistema solo informa, no toma decisiones.

### 5.6 RRHH visualiza solicitudes {#5.6-rrhh-visualiza-solicitudes}

El departamento de Recursos Humanos accede al panel general donde puede:

* Ver todas las solicitudes registradas.

* Identificar el estado de cada una.

* Revisar advertencias de posibles conflictos.

* Filtrar por fechas o empleados si es necesario.

### 5.7 RRHH exporta solicitudes a Excel {#5.7-rrhh-exporta-solicitudes-a-excel}

RRHH genera un archivo Excel que contiene la información completa de las solicitudes registradas.

El documento puede incluir:

* Número de empleado

* Nombre y apellidos

* Fecha inicio de vacaciones

* Fecha fin de vacaciones

* Días solicitados

* Días pendientes según convenio

Este archivo permite realizar un análisis global fuera del sistema.

### 5.8 Evaluación externa (implícita en el proceso) {#5.8-evaluación-externa-(implícita-en-el-proceso)}

A partir de la información exportada, RRHH realiza un análisis fuera del sistema, pudiendo comunicarse directamente con el empleado para resolver conflictos o aclarar situaciones.

### 

### 5\.9 RRHH actualiza el estado de la solicitud {#5.9-rrhh-actualiza-el-estado-de-la-solicitud}

Tras la evaluación externa este punto puede:

* Aprobar la solicitud

* Rechazar la solicitud

La decisión se registra manualmente en el sistema.

### 5.10  Solicitud estado “aprobado” {#5.10-solicitud-estado-“aprobado”}

Si la solicitud es validada:

* Se actualiza su estado a “Aprobado”.

* El periodo queda confirmado oficialmente.

* Pasa a formar parte del histórico aprobado.

### 5.11 Solicitud estado “rechazado” {#5.11-solicitud-estado-“rechazado”}

Si la solicitud no puede ser aceptada:

* Se actualiza el estado a “Rechazado”.

* Queda registrada la resolución.

* El empleado deberá, si lo desea, generar una nueva solicitud.

### 5.12 Sistema notifica al empleado {#5.12-sistema-notifica-al-empleado}

Una vez actualizado el estado, el sistema envía automáticamente una notificación al empleado informando del resultado final.

Esto garantiza:

* Transparencia.

* Comunicación inmediata.

* Eliminación de correos manuales.

### 5.13 Fin {#5.13-fin}

El proceso concluye cuando:

* La solicitud tiene un estado definitivo (Aprobado o Rechazado).

* El empleado ha sido notificado.

* La información queda almacenada en el histórico del sistema.

## 6 Mockups / Diseño de pantallas  {#6-mockups-/-diseño-de-pantallas}

Se mostrarán los prototipos visuales de las pantallas del sistema o aplicación, incluyendo la estructura de la interfaz, navegación y disposición de los elementos principales, con el objetivo de validar la experiencia de usuario antes del desarrollo final.(La Imagen es provisional)

![][image2]

## 7 Indicadores de éxito {#7-indicadores-de-éxito}

Con el objetivo de evaluar la eficacia del sistema una vez implantado, se definirán una serie de indicadores clave que permitirán medir su impacto en la operativa de la empresa y en la experiencia de los usuarios.

Estos indicadores facilitarán la toma de decisiones y la mejora continua del sistema.

### 7.1 Reducción del tiempo de gestión {#7.1-reducción-del-tiempo-de-gestión}

Qué mide:  
 El tiempo que tarda una solicitud desde que se registra hasta que se resuelve.

Objetivo:  
 Disminuir los tiempos de gestión respecto al proceso actual.

### 7.2 Número de solicitudes gestionadas {#7.2-número-de-solicitudes-gestionadas}

Qué mide:  
 Cantidad total de solicitudes procesadas a través del sistema.

Objetivo:  
 Verificar la adopción de la herramienta por parte de los empleados.

### 7.3 Porcentaje de solicitudes resueltas {#7.3-porcentaje-de-solicitudes-resueltas}

Qué mide:  
 Relación entre solicitudes registradas y solicitudes finalizadas (aprobadas o rechazadas).

Objetivo:  
 Garantizar que las solicitudes no queden sin gestionar.

### 7.4 Reducción de errores o incidencias {#7.4-reducción-de-errores-o-incidencias}

Qué mide:  
 Número de conflictos no detectados, errores en fechas o problemas derivados de la gestión manual.

Objetivo:  
 Minimizar errores gracias a la centralización del sistema.

### 7.5 Uso del sistema por parte de empleados {#7.5-uso-del-sistema-por-parte-de-empleados}

Qué mide:  
 Frecuencia de uso de la plataforma por parte de los usuarios.

Objetivo:  
 Asegurar que el sistema sustituye completamente a los métodos anteriores (emails, etc.).

### 7.6 Eficiencia en la generación de reportes {#7.6-eficiencia-en-la-generación-de-reportes}

Qué mide:  
 Tiempo necesario para obtener información en formato Excel.

Objetivo:  
 Reducir el esfuerzo necesario para generar informes y análisis.

### 7.7 Satisfacción del usuario {#7.7-satisfacción-del-usuario}

Qué mide:  
 Percepción de empleados y RRHH sobre el uso del sistema.

Objetivo:  
 Mejorar la experiencia de uso y la claridad del proceso.

## 8 Plan de implantación {#8-plan-de-implantación}

Se describe la estrategia para poner en marcha la solución, incluyendo fases, cronograma, recursos necesarios, tareas de despliegue, formación de usuarios y medidas para garantizar una transición controlada.

## 9 Evolución Futura {#9-evolución-futura}

Se detallarán las posibles mejoras y ampliaciones del sistema a medio y largo plazo, como nuevas funcionalidades, optimizaciones, escalabilidad y adaptación a futuras necesidades del negocio o tecnología.

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,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>