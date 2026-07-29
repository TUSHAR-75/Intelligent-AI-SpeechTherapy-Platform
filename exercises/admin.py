# from django.contrib import admin

# # Register your models here.
from django.contrib import admin
from .models import TherapyExercise, SpeechAttempt


@admin.register(TherapyExercise)
class TherapyExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'created_at')
    list_filter = ('difficulty',)
    search_fields = ('title', 'target_text')


@admin.register(SpeechAttempt)
class SpeechAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'exercise', 'overall_score', 'created_at')
    list_filter = ('exercise', 'created_at')
    search_fields = ('user__email', 'transcribed_text')