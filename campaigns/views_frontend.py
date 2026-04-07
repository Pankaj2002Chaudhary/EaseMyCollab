from django.shortcuts import render

def create_campaign_page(request):
    return render(request, 'campaigns/create_campaign.html')