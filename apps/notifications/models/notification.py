# Recovered from apps/notifications/models/__pycache__/notification.cpython-312.pyc
# Tool: pycdc (Decompyle++)
from django.db import models
from django.conf import settings
from apps.core.models import CreatedAtModel

class Notification(CreatedAtModel):
    
    class Type(models.TextChoices):
        VACATION_INFO = ('info', 'Mensaje general')
        VACATION_REQUEST_STATUS = ('vacation_request_status', 'Vacation request status')
        VACATION_REQUEST_SUBMISSION = ('vacation_request_submission', 'Vacation request submission')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'notifications')
    notification_type = models.CharField(max_length = 40, choices = Type.choices, default = Type.VACATION_INFO)
    vacation_request = models.ForeignKey('vacations.VacationRequest', on_delete = models.SET_NULL, related_name = 'notifications', blank = True, null = True)
    previous_status_name = models.CharField(max_length = 50, blank = True, null = True)
    message = models.TextField()
    is_read = models.BooleanField(default = False)
    sent_at = models.DateTimeField(auto_now_add = True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = [
            '-sent_at']
        indexes = [
            models.Index(fields = [
                'user',
                'is_read',
                'sent_at'], name = 'notif_user_read_sent_idx')]

    
    def __str__(self):
        return f'''Notificación para {self.user} — leída: {self.is_read}'''
