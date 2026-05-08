from rest_framework import serializers
from django.db.models import Avg
from .models import BrandProfile
from collaborations.models import Review # Import your review model

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.ReadOnlyField(source='reviewer.username')
    class Meta:
        model = Review
        fields = ['reviewer_name', 'rating', 'comment', 'created_at']

class BrandProfileSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = BrandProfile
        fields = '__all__' # Isme reviews aur average_rating automatically add ho jayenge SerializerMethodField ki wajah se

    def get_reviews(self, obj):
        reviews = Review.objects.filter(target_user=obj.user)
        return ReviewSerializer(reviews, many=True).data

    def get_average_rating(self, obj):
        avg = Review.objects.filter(target_user=obj.user).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0