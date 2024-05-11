from rest_framework import serializers
from .models import AudioVideoFile, SegmentHash


class SegmentHashSerializer(serializers.ModelSerializer):
    class Meta:
        model = SegmentHash
        fields = ['hash_value', 'start_time_seconds']


class AudioVideoFileSerializer(serializers.ModelSerializer):
    # Retrieves all hashes for a particular file
    segment_hashes = SegmentHashSerializer(many=True, read_only=True)

    class Meta:
        model = AudioVideoFile
        fields = ['id', 'file_name', 'source', 'duration_seconds', 'segment_hashes']
