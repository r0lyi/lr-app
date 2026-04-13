"""Politicas centrales del dominio de vacaciones.

Este archivo concentra las reglas configurables del sistema para que no queden
repartidas entre formularios, selectores y servicios. La idea es sencilla:

- Si cambia el convenio o una norma interna de la empresa, primero se revisa
  este modulo.
- El resto del codigo debe leer las reglas desde aqui, en lugar de repetir
  literales como "30 dias" o "pending/approved".

En esta fase del proyecto usamos un conjunto pequeno de reglas, pero ya
preparado para crecer de forma ordenada.
"""

from decimal import Decimal

FULL_ANNUAL_VACATION_DAYS = Decimal("30.00")
ACTIVE_REQUEST_STATUS_NAMES = ("pending", "approved")
OPEN_REQUEST_STATUS_NAMES = ("pending",)
DEFAULT_NEW_REQUEST_STATUS_NAME = "pending"
VACATION_DAY_COUNT_MODE = "natural"
MIN_REQUESTED_VACATION_DAYS = Decimal("3.00")
MAX_REQUESTED_VACATION_DAYS = Decimal("30.00")
MIN_ADVANCE_NOTICE_DAYS = 30
LONG_DURATION_VACATION_DAYS = Decimal("30.00")
HIGH_LOAD_PERIODS = (
    ("Verano", (6, 15), (9, 15)),
    ("Navidad", (12, 15), (1, 7)),
)
