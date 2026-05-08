from rest_framework import serializers
from .models import InfluencerProfile

class InfluencerProfileSerializer(serializers.ModelSerializer):
    # Reviews, ReviewSerializer, aur saare methods hta diye hain
    
    class Meta:
        model = InfluencerProfile
        fields = '__all__'