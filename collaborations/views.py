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