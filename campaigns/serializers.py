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