from django.db import models


# Create your models here.
from django.db import models

from fingerprint.models import AudioVideoFile


class EndpointUsage(models.Model):
    endpoint = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    data = models.TextField(null=True, blank=True)
    matched_file = models.ForeignKey(AudioVideoFile, null=True, on_delete=models.SET_NULL)

    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['endpoint']),
        ]

    def __str__(self):
        return f"{self.endpoint} - {self.timestamp} - {self.status}"

