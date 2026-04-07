from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import InfluencerProfile

class InfluencerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Agar URL mein user_id hai, toh wo profile dikhao, warna khud ki
        user_id = request.query_params.get('user_id')
        target_user = request.user if not user_id else \
                      type('User', (), {'id': user_id}) # Dummy object to handle logic

        try:
            # Check if it's an Influencer or Brand profile request
            # Note: You might need to import BrandProfile here
            from brands.models import BrandProfile
            
            # Logic to decide which data to send
            # If user_id is provided, we fetch that specific user's profile
            if user_id:
                # Try finding in Influencer first, then Brand
                inf = InfluencerProfile.objects.filter(user_id=user_id).first()
                if inf:
                    return Response({
                        "name": inf.full_name, "industry": inf.niche, 
                        "bio": inf.bio, "instagram": inf.instagram_url,
                        "youtube": inf.youtube_url, "is_owner": False
                    })
                
                brand = BrandProfile.objects.filter(user_id=user_id).first()
                if brand:
                    return Response({
                        "name": brand.name, "industry": brand.industry, 
                        "bio": brand.bio, "website": brand.website, "is_owner": False
                    })
            
            # Default: Return current user's profile
            profile, _ = InfluencerProfile.objects.get_or_create(user=request.user)
            return Response({
                "name": profile.full_name, "industry": profile.niche,
                "bio": profile.bio, "instagram": profile.instagram_url,
                "youtube": profile.youtube_url, "is_owner": True
            })
        except:
            return Response({"error": "Profile not found"}, status=404)

    def post(self, request):
        profile, created = InfluencerProfile.objects.get_or_create(user=request.user)
        # ... your existing save logic ...
        profile.full_name = request.data.get('name')
        profile.niche = request.data.get('industry')
        profile.bio = request.data.get('bio')
        profile.instagram_url = request.data.get('instagram_url')
        profile.youtube_url = request.data.get('youtube_url')
        profile.save()
        return Response({"message": "Influencer profile saved"})