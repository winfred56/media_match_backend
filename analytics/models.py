from django.db import models


# Create your models here.
class EndpointUsage(models.Model):
    endpoint = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    data = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.endpoint} - {self.timestamp} - {self.status}"
