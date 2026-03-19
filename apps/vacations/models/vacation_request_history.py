# Recovered from apps/vacations/models/__pycache__/vacation_request_history.cpython-312.pyc
# Tool: pycdc (Decompyle++)
from django.db import models
from django.conf import settings
from apps.core.models import CreatedAtModel
from .vacation_request import VacationRequest
from .vacation_status import VacationStatus

class VacationRequestHistory(CreatedAtModel):
    vacation_request = models.ForeignKey(VacationRequest, on_delete = models.CASCADE, related_name = 'histories')
    previous_status = models.ForeignKey(VacationStatus, on_delete = models.PROTECT, null = True, blank = True, related_name = '+')
    new_status = models.ForeignKey(VacationStatus, on_delete = models.PROTECT, related_name = '+')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True, blank = True, related_name = 'vacation_changes')
    change_date = models.DateTimeField(auto_now_add = True)
    comment = models.TextField(blank = True, null = True)
    
    class Meta:
        db_table = 'vacation_request_histories'
        verbose_name = 'Historial de solicitud'
        verbose_name_plural = 'Historial de solicitudes'
