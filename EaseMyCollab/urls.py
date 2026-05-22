from django.urls import path
from django.contrib import admin
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static

# --- Backend API Views ---
from accounts.views import (
    SendRegistrationOTPView,
    VerifyRegistrationOTPView,
    ForgotPasswordView,
    ResetPasswordView,
    LoginView,
    ProfileView
)
from campaigns.views import (
    CreateCampaignView,
    CampaignListView,
    ApplyCampaignView,
    ViewApplicantsView,
    MyCampaignsAPI,
    DeleteCampaignAPI,
    InfluencerApplicationsView,
    UpdateApplicationStatusView,
    PostReviewView,
)
from collaborations.views import AcceptApplicationView

# --- Frontend HTML Views ---
from campaigns.views_frontend import create_campaign_page
from accounts.views_frontend import profile_page, login_page, home_page, register_page

# Local Frontend Views
def brand_dashboard(request):
    return render(request, 'brand/dashboard.html')

def influencer_dashboard(request):
    return render(request, 'influencer/dashboard.html')
from accounts import views_frontend
# --- URL Patterns ---
urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    
    # --- Authentication API ---
    path('api/register/send-otp/', SendRegistrationOTPView.as_view(), name='register_send_otp'),
    path('api/register/verify-otp/', VerifyRegistrationOTPView.as_view(), name='register_verify_otp'),
    path('api/login/', LoginView.as_view(), name='login_api'),
    path('forgot-password/', views_frontend.forgot_password_page, name='forgot_password_page'),
    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password_api'),
    path('api/reset-password/', ResetPasswordView.as_view(), name='reset_password_api'),
    
    # --- Campaigns API ---
    path('api/campaigns/', CampaignListView.as_view()),
    path('api/create-campaign/', CreateCampaignView.as_view()),
    path('api/my-campaigns/', MyCampaignsAPI.as_view()),
    path('api/delete-campaign/<int:id>/', DeleteCampaignAPI.as_view()),
    
    # --- Applications, Reviews & Profiles API ---
    path('api/apply/<int:campaign_id>/', ApplyCampaignView.as_view()), 
    path('api/applicants/<int:campaign_id>/', ViewApplicantsView.as_view()),
    path('api/accept-application/<int:application_id>/', AcceptApplicationView.as_view()),
    path('api/influencer/my-applications/', InfluencerApplicationsView.as_view()),
    path('api/profile/', ProfileView.as_view(), name='profile_api'), 
    path('api/application/<int:application_id>/update/', UpdateApplicationStatusView.as_view()),
    path('api/post-review/', PostReviewView.as_view(), name='post_review_api'),
    
    # --- Frontend Pages (Renders HTML Templates) ---
    path('', home_page, name='home'),
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register_page'),
    path('profile/', profile_page, name='profile_page'),
    path('create-campaign/', create_campaign_page, name='create_campaign_page'),
    path('dashboard/', brand_dashboard, name='brand_dashboard'),
    path('influencer/dashboard/', influencer_dashboard, name='influencer_dashboard'),
]

# Serving Static & Media files safely during local development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)