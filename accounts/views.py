from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegisterSerializer

# class RegisterView(APIView):

#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)

#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "User registered successfully"})

#         return Response(serializer.errors)
    

# import random
# from django.core.mail import send_mail
# from django.core.cache import cache
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.contrib.auth import get_user_model

# User = get_user_model()

# import random

# from django.conf import settings
# from django.core.cache import cache
# from django.core.mail import send_mail

# from rest_framework.views import APIView
# from rest_framework.response import Response

# from .models import User


# class SendOTPView(APIView):
#     def post(self, request):
#         email = request.data.get('email', '').strip().lower()
#         username = request.data.get('username', '').strip()

#         if User.objects.filter(email=email).exists():
#             return Response(
#                 {"error": "Bhai, ye email pehle se registered hai!"},
#                 status=400
#             )

#         if User.objects.filter(username=username).exists():
#             return Response(
#                 {"error": "Ye username koi le chuka hai!"},
#                 status=400
#             )

#         otp = str(random.randint(100000, 999999))

#         cache.set(f'otp_{email}', otp, timeout=300)

#         try:
#             send_mail(
#                 'Verify EaseMyCollab Account',
#                 f'Aapka registration OTP hai: {otp}',
#                 settings.EMAIL_HOST_USER,
#                 [email],
#                 fail_silently=False,
#             )

#             return Response({"message": "OTP Sent, Please Check!"})

#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=500
#             )
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'influencer')

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Direct User Creation (No OTP)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role
            )
            return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class LoginView(APIView):
    """Secure clean login API providing validation tokens for EaseMyCollab"""
    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response({"detail": "Please provide both username and password."}, status=status.HTTP_400_BAD_REQUEST)

        # Django authenticate uses password hashing systems automatically
        user = authenticate(username=username, password=password)

        if user is not None:
            # Generate JWT tokens
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
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from brands.models import BrandProfile
from influencers.models import InfluencerProfile
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

from django.db.models import Avg
from campaigns.models import Review # Import check kar lena sahi hai na

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('user_id')
        
        # Decide target user
        if user_id:
            target_user = get_object_or_404(User, id=user_id)
        else:
            target_user = request.user

        # Is current user viewing their own profile?
        is_owner = (target_user == request.user)

        # Rating Logic with Error Safety
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
            # Agar Review table nahi bani toh crash na ho
            avg_rating, total_reviews, latest_reviews = 0, 0, []

        if target_user.role == "brand":
            profile, _ = BrandProfile.objects.get_or_create(user=target_user)
            data = {
                "id": target_user.id,
                "role": "brand",
                "is_owner": is_owner, # Ye True hoga toh Edit button aayega
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
    
import random
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer

User = get_user_model()

class SendRegistrationOTPView(APIView):
    """Step 1: Validate details and send an OTP to email without creating the user yet."""
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        role = request.data.get('role', 'influencer')

        if not email or not username or not password:
            return Response({"error": "Username, email, and password are required!"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Bhai, ye email pehle se registered hai!"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Ye username koi le chuka hai!"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate 6 digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Structure the registration payload to save in cache temporary
        user_data = {
            "username": username,
            "email": email,
            "password": password,
            "role": role,
            "otp": otp
        }
        
        # Save payload in cache for 5 minutes (300 seconds)
        cache.set(f'reg_{email}', user_data, timeout=300)

        try:
            send_mail(
                'Verify Your EaseMyCollab Account',
                f'Aapka registration OTP hai: {otp}. It is valid for 5 minutes.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({"message": "OTP Sent successfully! Please check your email."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Email sending failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyRegistrationOTPView(APIView):
    """Step 2: Check OTP from cache. If matched, create the User record in DB."""
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        otp_received = request.data.get('otp', '').strip()

        cached_data = cache.get(f'reg_{email}')
        
        if not cached_data:
            return Response({"error": "OTP expired ya details invalid hain. Please click resend."}, status=status.HTTP_400_BAD_REQUEST)

        if cached_data['otp'] != otp_received:
            return Response({"error": "Galat OTP dala hai aapne!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # OTP matches! Create user now
            user = User.objects.create_user(
                username=cached_data['username'],
                email=cached_data['email'],
                password=cached_data['password'],
                role=cached_data['role']
            )
            
            # Clean cache after successful registration
            cache.delete(f'reg_{email}')
            
            return Response({"message": "Registration successful! Your account is active."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ForgotPasswordView(APIView):
    """Step 1 for Forgot Password: Check if email exists, cache OTP."""
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        
        if not User.objects.filter(email=email).exists():
            return Response({"error": "Bhai, ye email registered nahi hai!"}, status=status.HTTP_404_NOT_FOUND)

        otp = str(random.randint(100000, 999999))
        cache.set(f'reset_otp_{email}', otp, timeout=300) # Valid for 5 mins

        try:
            send_mail(
                'Password Reset OTP - EaseMyCollab',
                f'Aapka password reset OTP hai: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({"message": "Password reset OTP bhej diya gaya hai."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Email sending failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordView(APIView):
    """Step 2 for Forgot Password: Match OTP and set new password safely."""
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        otp_received = request.data.get('otp', '').strip()
        new_password = request.data.get('new_password', '')

        if not new_password:
            return Response({"error": "New password cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        stored_otp = cache.get(f'reset_otp_{email}')
        if not stored_otp or stored_otp != otp_received:
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # Update Password securely using set_password
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        # Evict cache key
        cache.delete(f'reset_otp_{email}')
        return Response({"message": "Password updated successfully!"}, status=status.HTTP_200_OK)