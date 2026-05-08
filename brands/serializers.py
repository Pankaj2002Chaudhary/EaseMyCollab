from rest_framework import serializers
from .models import BrandProfile

class BrandProfileSerializer(serializers.ModelSerializer):
    # Reviews aur Average Rating se related saari fields aur methods hata di hain
    
    class Meta:
        model = BrandProfile
        fields = '__all__'