from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, UserProfileView

from .views import UserAnalyticsDashboardView

urlpatterns = [
    # Authentication Endpoints
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile Endpoints
    path('me/', UserProfileView.as_view(), name='user_profile'),

    path('analytics/', UserAnalyticsDashboardView.as_view(), name='user_analytics'),
]