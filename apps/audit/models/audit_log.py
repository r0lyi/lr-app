
from django.db import models
from django.conf import settings
from apps.core.models import CreatedAtModel

class AuditLog(CreatedAtModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.PROTECT, related_name = 'audit_logs')
    action = models.CharField(max_length = 50)
    resource_type = models.CharField(max_length = 50)
    resource_id = models.BigIntegerField()
    description = models.TextField(blank = True, null = True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Log de auditoría'
        verbose_name_plural = 'Logs de auditoría'
        ordering = [
            '-created_at']
        indexes = [
            models.Index(fields = [
                'resource_type',
                'resource_id',
                'created_at'], name = 'audit_resource_created_idx')]

    
    def __str__(self):
        return f'''{self.action} | {self.resource_type}:{self.resource_id}'''
