from rest_framework import serializers
from .models import AudioVideoFile, SegmentHash


class AudioVideoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioVideoFile
        fields = '__all__'


class SegmentHashSerializer(serializers.ModelSerializer):
    class Meta:
        model = SegmentHash
        fields = '__all__'
