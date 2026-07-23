from rest_framework import serializers
from .models import Campaign, Application

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'
        extra_kwargs = {
            'brand' : {'required' : False}
        }


# campaigns/serializers.py
from rest_framework import serializers
from .models import Application

class ApplicationSerializer(serializers.ModelSerializer):
    # In fields ko add karo taaki frontend pe 'undefined' na aaye
    influencer_name = serializers.ReadOnlyField(source='influencer.full_name')
    influencer_user_id = serializers.ReadOnlyField(source='influencer.user.id')

    class Meta:
        model = Application
        fields = ['id', 'influencer_name', 'influencer_user_id', 'status', 'applied_at']

# campaigns/serializers.py — input validation for the AI campaign generator
class CampaignAIGenerateSerializer(serializers.Serializer):
    key_points = serializers.CharField()   # brand ke 3-4 rough points
    brand_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    category = serializers.CharField(max_length=255, required=False, allow_blank=True)
    platform = serializers.CharField(max_length=100, required=False, allow_blank=True)
    budget = serializers.CharField(max_length=100, required=False, allow_blank=True)