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

class ApplyCampaignView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, campaign_id):

        influencer = request.user.influencerprofile

        # prevent duplicate
        if Application.objects.filter(campaign_id=campaign_id, influencer=influencer).exists():
            return Response({"error": "Already applied"})

        Application.objects.create(
            campaign_id=campaign_id,
            influencer=influencer
        )

        return Response({"message": "Applied successfully"})

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