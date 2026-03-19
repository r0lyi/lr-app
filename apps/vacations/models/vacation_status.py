# Recovered from apps/vacations/models/__pycache__/vacation_status.cpython-312.pyc
# Tool: pycdc (Decompyle++)
from django.db import models

class VacationStatus(models.Model):
    name = models.CharField(max_length = 50, unique = True)
    
    class Meta:
        db_table = 'vacation_statuses'
        verbose_name = 'Estado de vacaciones'
        verbose_name_plural = 'Estados de vacaciones'

    
    def __str__(self):
        return self.name
