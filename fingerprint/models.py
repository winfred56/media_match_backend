# from django.db import models
#
#
# # Create your models here.
# class AudioVideoFile(models.Model):
#     file_name = models.CharField(max_length=255)
#     source = models.CharField(max_length=255, null=True)
#     duration_seconds = models.FloatField()
#
#     def __str__(self):
#         return self.file_name
#
#
# class SegmentHash(models.Model):
#     audio_video_file = models.ForeignKey(AudioVideoFile, on_delete=models.CASCADE, related_name='segment_hashes')
#     hash_value = models.CharField(max_length=255)
#     start_time_seconds = models.FloatField(null=True)
#
#     def __str__(self):
#         return f"{self.audio_video_file.file_name} - {self.hash_value}"
#
#     class Meta:
#         unique_together = ("audio_video_file", "hash_value", "start_time_seconds")
#

from django.db import models


class AudioVideoFile(models.Model):
    file_name = models.CharField(max_length=255)
    source = models.CharField(max_length=255, null=True)
    duration_seconds = models.FloatField()

    def __str__(self):
        return self.file_name


class SegmentHash(models.Model):
    audio_video_file = models.ForeignKey(AudioVideoFile, on_delete=models.CASCADE)
    hash_value = models.CharField(max_length=255, null=True)
    features = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.audio_video_file.file_name} - {self.hash_value or self.features}"

    class Meta:
        unique_together = ("audio_video_file", "hash_value", "features")


class EndpointUsage(models.Model):
    endpoint = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    data = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.endpoint} - {self.timestamp} - {self.status}"
