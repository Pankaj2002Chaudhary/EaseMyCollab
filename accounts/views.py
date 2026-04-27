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
    

import random
from django.core.mail import send_mail
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()

class SendOTPView(APIView):
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        username = request.data.get('username', '').strip()
        

        # 1. Check if email/username already exist
        if User.objects.filter(email=email).exists():
            return Response({"error": "Bhai, ye email pehle se registered hai!"}, status=400)
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "Ye username koi le chuka hai!"}, status=400)

        # 2. Generate and store OTP
        otp = str(random.randint(100000, 999999))
        cache.set(f'otp_{email}', otp, timeout=300) # 5 mins valid

        # 3. Send Mail
        try:
            send_mail(
                'Verify EaseMyCollab Account',
                f'Aapka registration OTP hai: {otp}',
                'noreply@easemycollab.com',
                [email],
                fail_silently=False,
            )
            return Response({"message": "OTP Sent, Please Check!"})
        except Exception:
            return Response({"error": "Email not sent."}, status=500)

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email', '').strip().lower() # Yahan bhi lower()
        otp_received = data.get('otp')
        
        # 1. Verify OTP from Cache
        stored_otp = cache.get(f'otp_{email}')
        
        if not stored_otp:
            return Response({"error": "OTP expire ho gaya ya bheja hi nahi gaya!"}, status=400)
            
        if stored_otp != otp_received:
            return Response({"error": "OTP galat hai, sahi se dekho!"}, status=400)

        # 2. Create User (Signals will handle Profiles)
        try:
            user = User.objects.create_user(
                username=data.get('username'),
                email=email,
                password=data.get('password'),
                role=data.get('role')
            )
            # Cleanup
            cache.delete(f'otp_{email}')
            return Response({"message": "Account created successfully!"})
        except Exception as e:
            return Response({"error": str(e)}, status=400)


from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)

        # 🔑 Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        })
    
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
    

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not User.objects.filter(email=email).exists():
            return Response({"error": "Bhai, ye email registered nahi hai!"}, status=404)

        otp = str(random.randint(100000, 999999))
        cache.set(f'reset_otp_{email}', otp, timeout=300) # 5 mins valid

        try:
            send_mail(
                'Password Reset OTP - EaseMyCollab',
                f'Aapka password reset OTP hai: {otp}',
                'noreply@easemycollab.com',
                [email],
                fail_silently=False,
            )
            return Response({"message": "OTP bhej diya gaya hai."})
        except:
            return Response({"error": "Email sending failed."}, status=500)

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp_received = request.data.get('otp')
        new_password = request.data.get('new_password')

        stored_otp = cache.get(f'reset_otp_{email}')
        if not stored_otp or stored_otp != otp_received:
            return Response({"error": "Invalid or expired OTP"}, status=400)

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        cache.delete(f'reset_otp_{email}')
        return Response({"message": "Password updated successfully!"})