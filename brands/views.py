from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BrandProfile

class BrandProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile, created = BrandProfile.objects.get_or_create(user=request.user)

        profile.name = request.data.get('name')
        profile.industry = request.data.get('industry')
        profile.website = request.data.get('website')
        profile.bio = request.data.get('bio')
        profile.instagram_url = request.data.get('instagram_url')
        profile.youtube_url = request.data.get('youtube_url')

        profile.save()

        return Response({"message": "Brand profile saved"})
    
