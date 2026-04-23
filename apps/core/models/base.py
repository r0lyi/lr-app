"""Modelos abstractos con timestamps compartidos por varias apps."""

from django.db import models


class CreatedAtModel(models.Model):
    """Añade un timestamp de creacion inmutable al modelo hijo."""

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class TimeStampedModel(CreatedAtModel):
    """Extiende `CreatedAtModel` con la fecha de ultima actualizacion."""

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
