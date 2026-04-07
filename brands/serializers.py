from rest_framework import serializers
from .models import BrandProfile

class BrandProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandProfile
        fields = '__all__'