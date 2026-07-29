# from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile


class UserProfileInline(admin.StackedInline):
    """Allows viewing and editing UserProfile directly inside the CustomUser admin view."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Details'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom Admin layout for our CustomUser model."""
    inlines = (UserProfileInline,)
    list_display = ('email', 'username', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'overall_accuracy_score', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__email', 'user__username')