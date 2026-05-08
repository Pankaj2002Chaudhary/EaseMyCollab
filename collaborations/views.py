from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Collaboration
from campaigns.models import Application

class AcceptApplicationView(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, application_id):

        if Collaboration.objects.filter(application_id=application_id).exists():
            return Response({"error": "Already accepted"})

        Collaboration.objects.create(
            application_id=application_id,
            status="active",
            terms="Standard terms"
        )

        return Response({"message": "Collaboration created"})
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Review

class SubmitReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        campaign_id = request.data.get('campaign_id')
        target_user_id = request.data.get('target_user_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment')

        try:
            review = Review.objects.create(
                campaign_id=campaign_id,
                reviewer=request.user,
                target_user_id=target_user_id,
                rating=rating,
                comment=comment
            )
            return Response({"message": "Review submitted successfully!"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)