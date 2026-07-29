from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile

# Safely fetch our CustomUser model without hardcoding its name
User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Translates the UserProfile database model into JSON data.
    """
    class Meta:
        model = UserProfile
        fields = ['role', 'date_of_birth', 'target_phonemes', 'overall_accuracy_score']
        # The accuracy score is calculated by our AI engine; users cannot manually edit it!
        read_only_fields = ['overall_accuracy_score']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Handles user signup. Validates data, hashes passwords securely, 
    and automatically generates a linked UserProfile.
    """
    # Include profile fields during registration
    role = serializers.ChoiceField(
        choices=UserProfile.UserRole.choices, 
        default=UserProfile.UserRole.PATIENT,
        write_only=True
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        min_length=8,
        help_text="Password must be at least 8 characters long."
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'role']

    def create(self, validated_data):
        """
        Override default save behavior to intercept the raw password, 
        hash it securely using PBKDF2, and create the linked profile.
        """
        # Extract the role from validated data before creating the user
        role = validated_data.pop('role', UserProfile.UserRole.PATIENT)
        
        # 1. Create the user object using Django's secure helper method
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        
        # 2. Automatically generate the UserProfile linked to this new user
        UserProfile.objects.create(user=user, role=role)
        
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Used when returning complete user account details along with profile metadata.
    """
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'profile']