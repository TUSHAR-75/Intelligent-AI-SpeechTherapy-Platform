from django.shortcuts import render

# # Create your views here.


from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserDetailSerializer
from .models import UserProfile

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    API endpoint that allows anonymous users to create an account.
    POST /api/users/register/
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    # Allow anyone (even unauthenticated visitors) to hit this endpoint
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for authenticated users to view or edit their own profile.
    GET /api/users/me/
    PATCH /api/users/me/
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Security feature: Instead of taking a UUID from the URL (which could allow 
        users to spy on each other), we force the endpoint to ONLY return the 
        profile of the user making the request (extracted from the JWT token).
        """
        return self.request.user


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from exercises.models import SpeechAttempt
from datetime import timedelta
from django.utils import timezone

class UserAnalyticsDashboardView(APIView):
    """
    GET /api/users/analytics/
    Returns aggregated time-series data for the frontend progress charts.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        thirty_days_ago = timezone.now() - timedelta(days=30)

        # THE MAGIC DATABASE QUERY:
        # 1. Filter: Only get this user's attempts from the last 30 days.
        # 2. Annotate (TruncDate): Strip the hours/minutes off 'created_at' so we can group by Day.
        # 3. Values: Group the database rows by this new 'date'.
        # 4. Annotate: Calculate the Average score and Count the total attempts for each grouped day.
        # 5. Order: Sort chronologically.
        
        daily_stats = SpeechAttempt.objects.filter(
            user=user,
            created_at__gte=thirty_days_ago
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            average_score=Avg('overall_score'),
            total_attempts=Count('id')
        ).order_by('date')

        # Format data perfectly for Recharts / Chart.js on the frontend
        chart_data = [
            {
                "date": stat['date'].strftime('%Y-%m-%d'),
                "average_score": round(stat['average_score'], 1),
                "total_attempts": stat['total_attempts']
            }
            for stat in daily_stats
        ]

        # Return Gamification stats + Chart Data
        return Response({
            "gamification": {
                "xp_points": user.profile.xp_points,
                "current_streak": user.profile.current_streak,
                "longest_streak": user.profile.longest_streak,
            },
            "chart_data": chart_data
        })