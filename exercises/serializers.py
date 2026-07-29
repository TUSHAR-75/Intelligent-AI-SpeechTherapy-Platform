from rest_framework import serializers
from .models import TherapyExercise, SpeechAttempt

class TherapyExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TherapyExercise
        fields = ['id', 'title', 'target_text', 'target_phonemes', 'difficulty']

class SpeechAttemptSerializer(serializers.ModelSerializer):
    # We will only require the exercise ID and the audio file from the user
    class Meta:
        model = SpeechAttempt
        fields = ['id', 'exercise', 'audio_file', 'transcribed_text', 'overall_score', 'created_at']
        read_only_fields = ['id', 'transcribed_text', 'overall_score', 'created_at']