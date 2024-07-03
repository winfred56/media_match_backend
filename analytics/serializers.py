from rest_framework import serializers

from analytics.models import EndpointUsage


class EndpointUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EndpointUsage
        fields = '__all__'
