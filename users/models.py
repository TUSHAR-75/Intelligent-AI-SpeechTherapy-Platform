# module 10:


import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    """
    Primary identity table subclassing Django's AbstractUser.
    Replaces auto-incrementing integer IDs with UUIDs for enhanced security.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, help_text="Required for authentication.")

    # We enforce email as the main login identifier instead of arbitrary usernames
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # --- THIS IS WHERE THE FIX BELONGS ---
    def __str__(self):
        return self.email

    @property
    def role(self):
        # Access role quickly from the related profile if it exists
        return getattr(self.profile, 'role', 'PATIENT')


class UserProfile(models.Model):
    """
    Stores domain-specific medical/therapy metadata tied to a CustomUser.
    Separated from CustomUser to follow the Single Responsibility Principle.
    """
    class UserRole(models.TextChoices):
        PATIENT = 'PATIENT', 'Patient / Learner'
        THERAPIST = 'THERAPIST', 'Speech Therapist / Clinician'
        ADMIN = 'ADMIN', 'Platform Administrator'

    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    role = models.CharField(
        max_length=20, 
        choices=UserRole.choices, 
        default=UserRole.PATIENT
    )
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Store list of phonemes the user struggles with (e.g., ["R", "S", "TH"])
    target_phonemes = models.JSONField(
        default=list, 
        blank=True,
        help_text="List of phonemes requiring therapeutic attention."
    )
    
    overall_accuracy_score = models.FloatField(
        default=0.0,
        help_text="Rolling average score calculated across all attempts (0.0 to 100.0)."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --- NEW GAMIFICATION FIELDS ---
    xp_points = models.IntegerField(default=0, help_text="Experience points earned through practice.")
    current_streak = models.IntegerField(default=0, help_text="Consecutive days practiced.")
    longest_streak = models.IntegerField(default=0)
    last_practice_date = models.DateField(null=True, blank=True)

    # --- RESTORED THE CORRECT PROFILE STRING ---
    def __str__(self):
        return f"Profile: {self.user.email} - Role: {self.role}"






# # from django.db import models

# # # Create your models here.

# from django.utils import timezone


# import uuid
# from django.db import models
# from django.contrib.auth.models import AbstractUser

# class CustomUser(AbstractUser):
#     """
#     Primary identity table subclassing Django's AbstractUser.
#     Replaces auto-incrementing integer IDs with UUIDs for enhanced security.
#     """
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     email = models.EmailField(unique=True, help_text="Required for authentication.")

#     # We enforce email as the main login identifier instead of arbitrary usernames
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

#     # when you need to convert instance into string eg. print(user)

#     def __str__(self):
#         return f"{self.email} ({self.get_role_display()})"

#     @property
#     def role(self):
#         # Access role quickly from the related profile if it exists
#         return getattr(self.profile, 'role', 'PATIENT')


# class UserProfile(models.Model):
#     """
#     Stores domain-specific medical/therapy metadata tied to a CustomUser.
#     Separated from CustomUser to follow the Single Responsibility Principle.
#     """
#     class UserRole(models.TextChoices):
#         PATIENT = 'PATIENT', 'Patient / Learner'
#         THERAPIST = 'THERAPIST', 'Speech Therapist / Clinician'
#         ADMIN = 'ADMIN', 'Platform Administrator'

#     user = models.OneToOneField(
#         CustomUser, 
#         on_delete=models.CASCADE, 
#         related_name='profile'
#     )
#     role = models.CharField(
#         max_length=20, 
#         choices=UserRole.choices, 
#         default=UserRole.PATIENT
#     )
#     date_of_birth = models.DateField(null=True, blank=True)
    
#     # Store list of phonemes the user struggles with (e.g., ["R", "S", "TH"])
#     target_phonemes = models.JSONField(
#         default=list, 
#         blank=True,
#         help_text="List of phonemes requiring therapeutic attention."
#     )
    
#     overall_accuracy_score = models.FloatField(
#         default=0.0,
#         help_text="Rolling average score calculated across all attempts (0.0 to 100.0)."
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     # --- NEW GAMIFICATION FIELDS ---
#     xp_points = models.IntegerField(default=0, help_text="Experience points earned through practice.")
#     current_streak = models.IntegerField(default=0, help_text="Consecutive days practiced.")
#     longest_streak = models.IntegerField(default=0)
#     last_practice_date = models.DateField(null=True, blank=True)

#     # def __str__(self):
#     #     return f"Profile: {self.user.email} - Role: {self.role}"
#     # def __str__(self):
#     #     # We can just use the property you defined below it!
#     #     return f"{self.email} ({self.role})"

#     def __str__(self):
#         return self.email





