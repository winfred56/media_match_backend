from django.db import models


class AudioVideoFile(models.Model):
    file_name = models.CharField(max_length=255)
    source = models.CharField(max_length=255, null=True)
    duration_seconds = models.FloatField()

    def __str__(self):
        return self.file_name


class SegmentHash(models.Model):
    audio_video_file = models.ForeignKey(AudioVideoFile, on_delete=models.CASCADE)
    hash_value = models.CharField(max_length=1000, null=True)
    features = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['hash_value']),
            models.Index(fields=['audio_video_file']),
        ]

    def __str__(self):
        return f"{self.audio_video_file.file_name} - {self.hash_value or self.features}"

    class Meta:
        unique_together = ("audio_video_file", "hash_value", "features")
