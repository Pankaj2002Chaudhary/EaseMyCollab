import os
import random
import requests

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Avg

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer
from .models import User
from brands.models import BrandProfile
from influencers.models import InfluencerProfile
from campaigns.models import Review

User = get_user_model()


# ─────────────────────────────────────────────
# HELPER: Send email via Brevo HTTP API
# (No SMTP — works on Render free tier. SendGrid's free
# plan expired, switched to Brevo: 300 emails/day free, forever)
# ─────────────────────────────────────────────
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_otp_email(to_email, subject, body):
    api_key = os.getenv('BREVO_API_KEY')
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "sender": {"email": settings.DEFAULT_FROM_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": body,
    }
    response = requests.post(BREVO_API_URL, headers=headers, json=payload, timeout=15)
    if response.status_code >= 400:
        # Same behavior as before: raise so the calling view's try/except
        # logs "CRITICAL EMAIL ERROR" with the real reason.
        raise Exception(f"Brevo API error {response.status_code}: {response.text[:300]}")
    return response.status_code


# ─────────────────────────────────────────────
# REGISTER (Direct, no OTP — legacy)
# ─────────────────────────────────────────────
class RegisterView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'influencer')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role
            )
            return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {"detail": "Please provide both username and password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# ─────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('user_id')

        if user_id:
            target_user = get_object_or_404(User, id=user_id)
        else:
            target_user = request.user

        is_owner = (target_user == request.user)

        try:
            reviews_received = Review.objects.filter(reviewee=target_user)
            avg_rating = reviews_received.aggregate(Avg('rating'))['rating__avg'] or 0
            total_reviews = reviews_received.count()
            latest_reviews = []
            for r in reviews_received.order_by('-created_at')[:5]:
                latest_reviews.append({
                    "reviewer": r.reviewer.username,
                    "rating": r.rating,
                    "comment": r.comment,
                    "date": r.created_at.strftime("%d %b %Y")
                })
        except Exception:
            avg_rating, total_reviews, latest_reviews = 0, 0, []

        if target_user.role == "brand":
            profile, _ = BrandProfile.objects.get_or_create(user=target_user)
            data = {
                "id": target_user.id,
                "role": "brand",
                "is_owner": is_owner,
                "name": profile.name or target_user.username,
                "industry": profile.industry,
                "website": profile.website,
                "bio": profile.bio,
                "instagram": profile.instagram_url,
                "youtube": profile.youtube_url,
                "avg_rating": round(avg_rating, 1),
                "total_reviews": total_reviews,
                "reviews": latest_reviews,
            }
        else:
            profile, _ = InfluencerProfile.objects.get_or_create(user=target_user)
            data = {
                "id": target_user.id,
                "role": "influencer",
                "is_owner": is_owner,
                "name": profile.full_name or target_user.username,
                "industry": profile.niche,
                "bio": profile.bio,
                "instagram": profile.instagram_url,
                "youtube": profile.youtube_url,
                "avg_rating": round(avg_rating, 1),
                "total_reviews": total_reviews,
                "reviews": latest_reviews,
            }

        return Response(data)

    def post(self, request):
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


# ─────────────────────────────────────────────
# OTP REGISTRATION — Step 1: Send OTP
# ─────────────────────────────────────────────
class SendRegistrationOTPView(APIView):
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        role = request.data.get('role', 'influencer')

        if not email or not username or not password:
            return Response(
                {"error": "Username, email, and password are required!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response({"error": "Bhai, ye email pehle se registered hai!"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Ye username koi le chuka hai!"}, status=status.HTTP_400_BAD_REQUEST)

        otp = str(random.randint(100000, 999999))

        cache.set(f'reg_{email}', {
            "username": username,
            "email": email,
            "password": password,
            "role": role,
            "otp": otp
        }, timeout=300)

        try:
            print(f"Triggering OTP email toward: {email}")
            send_otp_email(
                email,
                'Verify Your EaseMyCollab Account',
                f'Aapka registration OTP hai: {otp}. It is valid for 5 minutes.'
            )
            return Response({"message": "OTP Sent successfully! Please check your email."}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"CRITICAL EMAIL ERROR: {str(e)}")
            return Response(
                {"error": "Email sending failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ─────────────────────────────────────────────
# OTP REGISTRATION — Step 2: Verify OTP
# ─────────────────────────────────────────────
class VerifyRegistrationOTPView(APIView):
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        otp_received = request.data.get('otp', '').strip()

        cached_data = cache.get(f'reg_{email}')

        if not cached_data:
            return Response(
                {"error": "OTP expired ya details invalid hain. Please click resend."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if cached_data['otp'] != otp_received:
            return Response({"error": "Galat OTP dala hai aapne!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(
                username=cached_data['username'],
                email=cached_data['email'],
                password=cached_data['password'],
                role=cached_data['role']
            )
            cache.delete(f'reg_{email}')
            return Response({"message": "Registration successful! Your account is active."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─────────────────────────────────────────────
# FORGOT PASSWORD — Step 1: Send OTP
# ─────────────────────────────────────────────
class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email', '').strip().lower()

        if not User.objects.filter(email=email).exists():
            return Response({"error": "Bhai, ye email registered nahi hai!"}, status=status.HTTP_404_NOT_FOUND)

        otp = str(random.randint(100000, 999999))
        cache.set(f'reset_otp_{email}', otp, timeout=300)

        try:
            send_otp_email(
                email,
                'Password Reset OTP - EaseMyCollab',
                f'Aapka password reset OTP hai: {otp}. Valid for 5 minutes.'
            )
            return Response({"message": "Password reset OTP bhej diya gaya hai."}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Forgot Password Email Error: {str(e)}")
            return Response(
                {"error": "Email sending failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ─────────────────────────────────────────────
# FORGOT PASSWORD — Step 2: Reset Password
# ─────────────────────────────────────────────
class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        otp_received = request.data.get('otp', '').strip()
        new_password = request.data.get('new_password', '')

        if not new_password:
            return Response({"error": "New password cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        stored_otp = cache.get(f'reset_otp_{email}')
        if not stored_otp or stored_otp != otp_received:
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        cache.delete(f'reset_otp_{email}')
        return Response({"message": "Password updated successfully!"}, status=status.HTTP_200_OK)