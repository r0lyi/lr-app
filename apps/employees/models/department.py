# Recovered from apps/employees/models/__pycache__/department.cpython-312.pyc
# Tool: pycdc (Decompyle++)
from django.db import models

class Department(models.Model):
    name = models.CharField(max_length = 100)
    max_concurrent_absences = models.IntegerField(default = 1)
    
    class Meta:
        db_table = 'department'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'

    
    def __str__(self):
        return self.name
