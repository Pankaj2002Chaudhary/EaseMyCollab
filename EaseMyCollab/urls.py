"""
URL configuration for EaseMyCollab project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]
# from django.urls import path
# from accounts.views import RegisterView
# from campaigns.views import (
#     CreateCampaignView,
#     CampaignListView,
#     ApplyCampaignView,
#     ViewApplicantsView,
#     MyCampaignsAPI,
#     DeleteCampaignAPI,
#     InfluencerApplicationsView,
# )
# from collaborations.views import AcceptApplicationView
# from accounts.views import LoginView
# from campaigns.views_frontend import create_campaign_page
# from accounts.views_frontend import profile_page, login_page,home_page, register_page
# from django.shortcuts import render
# from brands.views import BrandProfileView
# from influencers.views import InfluencerProfileView
# from accounts.views import ProfileView
# from django.contrib import admin
# def brand_dashboard(request):
#     return render(request, 'brand/dashboard.html')

# urlpatterns = [
#     path('api/register/', RegisterView.as_view()),
#     path('admin/', admin.site.urls),
#     path('api/campaigns/', CampaignListView.as_view()),
#     path('api/create-campaign/', CreateCampaignView.as_view()),

#     path('apply/<int:campaign_id>/', ApplyCampaignView.as_view()),
#     path('api/applicants/<int:campaign_id>/', ViewApplicantsView.as_view()),

#     path('accept/<int:application_id>/', AcceptApplicationView.as_view()),
#     path('api/login/', LoginView.as_view(), name='login'),
#     path('api/my-campaigns/', MyCampaignsAPI.as_view()),
#     path('delete-campaign/<int:id>/', DeleteCampaignAPI.as_view()),
#     # path('api/brand-profile/', BrandProfileView.as_view()),
#     # path('api/influencer-profile/', InfluencerProfileView.as_view()),
#     path('api/profile/', ProfileView.as_view()),
#     # campaigns/urls.py
#     path('api/influencer/my-applications/', InfluencerApplicationsView.as_view()),

#     # influencers/urls.py (ya jahan bhi profile view hai)
#     # path('api/profile/', InfluencerProfileView.as_view()),

#     path('login/', login_page),
#     path('register/', register_page),
#     path('',home_page, name='home'),
#     path('create-campaign/', create_campaign_page),
#     path('dashboard/', brand_dashboard),
#     path('profile/', profile_page),

# ]


from django.urls import path
from django.contrib import admin
from django.shortcuts import render
from accounts.views import RegisterView, LoginView, ProfileView
from campaigns.views import (
    CreateCampaignView,
    CampaignListView,
    ApplyCampaignView,
    ViewApplicantsView,
    MyCampaignsAPI,
    DeleteCampaignAPI,
    InfluencerApplicationsView,
    UpdateApplicationStatusView
)
from collaborations.views import AcceptApplicationView
from campaigns.views_frontend import create_campaign_page
from accounts.views_frontend import profile_page, login_page, home_page, register_page

# Frontend Views (Jinhe alag file me nahi dala unhe yahi define kar rahe hain)
def brand_dashboard(request):
    return render(request, 'brand/dashboard.html')

def influencer_dashboard(request):
    return render(request, 'influencer/dashboard.html') # Naya Template

urlpatterns = [
    # --- Auth & Admin ---
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view()),
    path('api/login/', LoginView.as_view(), name='login'),
    
    # --- API Endpoints ---
    path('api/campaigns/', CampaignListView.as_view()),
    path('api/create-campaign/', CreateCampaignView.as_view()),
    path('api/my-campaigns/', MyCampaignsAPI.as_view()),
    path('api/delete-campaign/<int:id>/', DeleteCampaignAPI.as_view()),
    
    # --- Applications & Dashboard API ---
    path('api/apply/<int:campaign_id>/', ApplyCampaignView.as_view()), # API prefix add kiya safety ke liye
    path('api/applicants/<int:campaign_id>/', ViewApplicantsView.as_view()),
    path('api/accept-application/<int:application_id>/', AcceptApplicationView.as_view()),
    path('api/influencer/my-applications/', InfluencerApplicationsView.as_view()),
    path('api/profile/', ProfileView.as_view()), # Common Profile API
    path('api/application/<int:application_id>/update/', UpdateApplicationStatusView.as_view()),

    # --- Frontend Pages (HTML) ---
    path('', home_page, name='home'),
    path('login/', login_page, name='login_page'),
    path('register/', register_page),
    path('profile/', profile_page),
    path('create-campaign/', create_campaign_page),
    path('dashboard/', brand_dashboard),
    path('influencer/dashboard/', influencer_dashboard), # Naya Route
]