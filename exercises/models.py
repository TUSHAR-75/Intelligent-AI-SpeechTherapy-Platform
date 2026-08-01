# from django.db import models

# # Create your models here.
import uuid
from django.db import models
# from django.conf import User , settings
from django.conf import settings

class DifficultyLevel(models.TextChoices):
    BEGINNER = 'EASY', 'Beginner'
    INTERMEDIATE = 'MEDIUM', 'Intermediate'
    ADVANCED = 'HARD', 'Advanced'


class TherapyExercise(models.Model):
    """
    Represents a prompt sentence or phrase designed to target specific phonemes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    target_text = models.TextField(help_text="The exact sentence/phrase the user must speak.")
    
    # Array of phonemes present in this sentence, e.g., ["R", "L"]
    target_phonemes = models.JSONField(
        default=list, 
        help_text="Phonemes tested in this exercise."
    )
    difficulty = models.CharField(
        max_length=10, 
        choices=DifficultyLevel.choices, 
        default=DifficultyLevel.BEGINNER
    )
    created_at = models.DateTimeField(auto_now_add=True)

    is_interview_mode = models.BooleanField(
        default=False, 
        help_text="If True, this is a professional interview question rather than a clinical phoneme test."
    )



    def __str__(self):
        return f"[{self.difficulty}] {self.title}"


class SpeechAttempt(models.Model):
    """
    Tracks an individual audio submission recorded by a user for an exercise.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'users.CustomUser', 
        on_delete=models.CASCADE, 
        related_name='speech_attempts'
    )
    exercise = models.ForeignKey(
        TherapyExercise, 
        on_delete=models.CASCADE, 
        related_name='attempts'
    )
    
    # Audio file persistence path
    audio_file = models.FileField(upload_to='audio_recordings/%Y/%m/%d/')
    
    # AI Engine Outputs
    transcribed_text = models.TextField(blank=True, null=True, help_text="Whisper output.")
    overall_score = models.FloatField(default=0.0, help_text="Calculated accuracy (0-100%).")
    
    # Detailed phoneme breakdown output: e.g., {"R": 85.5, "TH": 42.0}
    phoneme_scores = models.JSONField(default=dict, blank=True)
    
    # created_at = models.DateTimeField(auto_now_add=True)

    ai_feedback = models.TextField(
        blank=True, 
        null=True, 
        help_text="Actionable LLM-generated feedback based on the acoustic analysis."
    )

    # --- UPDATED FIELD ---
    # db_index=True tells PostgreSQL to build a background B-Tree index for this column
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Attempt by {self.user.email} on {self.exercise.title} - Score: {self.overall_score}%"