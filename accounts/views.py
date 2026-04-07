from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegisterSerializer

class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"})

        return Response(serializer.errors)
    

from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)

        # 🔑 Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        })
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from brands.models import BrandProfile
from influencers.models import InfluencerProfile
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. Check karo URL mein user_id hai ya nahi
        user_id = request.query_params.get('user_id')
        
        if user_id:
            # Kisi specific user ki profile (Influencer profile from dashboard)
            target_user = get_object_or_404(User, id=user_id)
        else:
            # Apni khud ki profile (Normal profile tab)
            target_user = request.user

        # 2. Role check karke data return karo
        if target_user.role == "brand":
            profile, _ = BrandProfile.objects.get_or_create(user=target_user)
            data = {
                "id": target_user.id,
                "role": "brand",
                "is_owner": (target_user == request.user), # Ye frontend ko batayega ki Edit button dikhana hai ya nahi
                "name": profile.name,
                "industry": profile.industry,
                "website": profile.website,
                "bio": profile.bio,
                "instagram": profile.instagram_url,
                "youtube": profile.youtube_url,
            }
        else:
            profile, _ = InfluencerProfile.objects.get_or_create(user=target_user)
            data = {
                "id": target_user.id,
                "role": "influencer",
                "is_owner": (target_user == request.user),
                "name": profile.full_name,
                "industry": profile.niche,
                "bio": profile.bio,
                "instagram": profile.instagram_url,
                "youtube": profile.youtube_url,
            }

        return Response(data)

    def post(self, request):
        # POST hamesha request.user pe chalega, taaki koi dusre ki profile update na kar sake
        user = request.user

        if user.role == "brand":
            profile, _ = BrandProfile.objects.get_or_create(user=user)
            profile.name = request.data.get("name", profile.name)
            profile.industry = request.data.get("industry", profile.industry)
            profile.website = request.data.get("website", profile.website)
            profile.bio = request.data.get("bio", profile.bio)
            profile.instagram_url = request.data.get("instagram", profile.instagram_url)
            profile.youtube_url = request.data.get("youtube", profile.youtube_url)
            profile.save()
        else:
            profile, _ = InfluencerProfile.objects.get_or_create(user=user)
            profile.full_name = request.data.get("name", profile.full_name)
            profile.niche = request.data.get("industry", profile.niche)
            profile.bio = request.data.get("bio", profile.bio)
            profile.instagram_url = request.data.get("instagram", profile.instagram_url)
            profile.youtube_url = request.data.get("youtube", profile.youtube_url)
            profile.save()

        return Response({"message": "Profile updated successfully"})