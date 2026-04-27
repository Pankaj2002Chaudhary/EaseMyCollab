from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Campaign
from .serializers import CampaignSerializer
from brands.models import BrandProfile
class CreateCampaignView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CampaignSerializer(data=request.data)
        
        if request.user.role != 'brand':
            return Response({"error": "Only brands can create campaigns"})
        
        if serializer.is_valid():
            brand=BrandProfile.objects.get(user=request.user)
            serializer.save(brand=brand)
            return Response({"message": "Campaign created successfully"})

        return Response(serializer.errors)
    
class CampaignListView(APIView):

    def get(self, request):
        campaigns = Campaign.objects.all()
        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data)
    
from .models import Application

from django.shortcuts import get_object_or_404
from influencers.models import InfluencerProfile # Isse import zaroori hai

class ApplyCampaignView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, campaign_id):
        # 1. Check karo user influencer hai ya nahi
        if request.user.role != 'influencer':
            return Response({"error": "Only influencers can apply for campaigns"}, status=400)

        # 2. PROFILE SAFETY CHECK (Yahan galti thi)
        # Agar profile nahi bani hogi, toh ye line use turant bana degi
        influencer, created = InfluencerProfile.objects.get_or_create(user=request.user)

        # 3. Campaign check karo ki valid hai ya nahi
        campaign = get_object_or_404(Campaign, id=campaign_id)

        # 4. Prevent duplicate application
        if Application.objects.filter(campaign=campaign, influencer=influencer).exists():
            return Response({"error": "You have already applied for this campaign"}, status=400)

        # 5. Application create karo
        Application.objects.create(
            campaign=campaign,
            influencer=influencer,
            status='pending' # Default status hamesha pending rakho
        )

        return Response({"message": "Applied successfully!"}, status=201)

from .serializers import ApplicationSerializer;
class ViewApplicantsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, campaign_id):

        applications = Application.objects.filter(campaign_id=campaign_id)
        serializer = ApplicationSerializer(applications, many=True)

        return Response(serializer.data)
    
class MyCampaignsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'brand':
            return Response({"error": "Unauthorized"})

        campaigns = Campaign.objects.filter(
            brand=request.user.brandprofile
        )

        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data)
    
class DeleteCampaignAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        campaign = Campaign.objects.get(id=id)

        if campaign.brand != request.user.brandprofile:
            return Response({"error": "Not allowed"})

        campaign.delete()
        return Response({"message": "Deleted"})
    
# campaigns/views.py mein ye class add karein
class InfluencerApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Check if user is influencer
            influencer = request.user.influencerprofile
            # Applications fetch karo with campaign and brand details
            applications = Application.objects.filter(influencer=influencer).select_related('campaign__brand')
            
            data = []
            for app in applications:
                data.append({
                    "id": app.id,
                    "campaign_title": app.campaign.title,
                    "brand_name": app.campaign.brand.name, # Brand ka name
                    "brand_user_id": app.campaign.brand.user.id, # Profile link ke liye
                    "status": app.status,
                    "budget": app.campaign.budget_range,
                    "applied_at": app.applied_at.strftime("%d %b, %Y")
                })
            return Response(data)
        except Exception as e:
            return Response({"error": "Influencer profile not found"}, status=404)
        

class UpdateApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, application_id):
        try:
            # Application ko id se dhoondo
            application = Application.objects.get(id=application_id)
            
            # Status fetch karo frontend se
            new_status = request.data.get("status") # 'accepted' ya 'rejected'
            
            if new_status in ['accepted', 'rejected']:
                application.status = new_status
                application.save()  # <--- YE LINE SABSE ZAROORI HAI
                return Response({"message": "Status updated successfully"})
            
            return Response({"error": "Invalid status"}, status=400)
        except Application.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
        
from .models import Application, Review

class PostReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        app_id = request.data.get("application_id")
        rating = request.data.get("rating")
        comment = request.data.get("comment", "")

        try:
            # 1. Application dhoondo
            application = Application.objects.get(id=app_id)

            # 2. Check karo application accepted hai ya nahi
            if application.status != 'accepted':
                return Response({"error": "You can only review accepted collaborations"}, status=400)

            # 3. Check karo ki kya review pehle hi diya ja chuka hai
            if Review.objects.filter(application=application, reviewer=request.user).exists():
                return Response({"error": "Review already submitted"}, status=400)

            # 4. Decide karo reviewee kaun hai
            # Agar Brand review de raha hai toh reviewee Influencer hoga, and vice versa
            if request.user == application.campaign.brand.user:
                reviewee = application.influencer.user
            else:
                reviewee = application.campaign.brand.user

            # 5. Review create karo
            Review.objects.create(
                application=application,
                reviewer=request.user,
                reviewee=reviewee,
                rating=rating,
                comment=comment
            )
            return Response({"message": "Review submitted successfully!"}, status=201)

        except Application.DoesNotExist:
            return Response({"error": "Application not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)