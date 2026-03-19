# Recovered from apps/employees/models/__pycache__/employee.cpython-312.pyc
# Tool: pycdc (Decompyle++)
from django.db import models
from django.conf import settings
from apps.core.models import CreatedAtModel
from .department import Department

class Employee(CreatedAtModel):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'employee_profile')
    department = models.ForeignKey(Department, on_delete = models.SET_NULL, null = True, blank = True, related_name = 'employees')
    first_name = models.CharField(max_length = 100)
    last_name = models.CharField(max_length = 100)
    phone = models.CharField(max_length = 20, blank = True, null = True)
    hire_date = models.DateField()
    available_days = models.IntegerField(default = 0)
    taken_days = models.IntegerField(default = 0)
    
    class Meta:
        db_table = 'employee'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    
    def __str__(self):
        return f'''{self.first_name} {self.last_name}'''
