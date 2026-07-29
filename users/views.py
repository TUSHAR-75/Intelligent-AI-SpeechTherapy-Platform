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