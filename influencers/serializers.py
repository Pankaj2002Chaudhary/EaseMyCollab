from rest_framework import serializers
from .models import InfluencerProfile

class InfluencerSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfluencerProfile
        fields = '__all__'