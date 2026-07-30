# # from django.shortcuts import render

# # # Create your views here.


# from rest_framework import generics, permissions, status
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser, FormParser
# from .models import TherapyExercise, SpeechAttempt
# from .serializers import TherapyExerciseSerializer, SpeechAttemptSerializer
# from .services import normalize_audio_for_ai

# class ExerciseListView(generics.ListAPIView):
#     """ GET /api/exercises/ - Returns available therapy exercises """
#     queryset = TherapyExercise.objects.all()
#     serializer_class = TherapyExerciseSerializer
#     permission_classes = [permissions.IsAuthenticated]

# class SpeechAttemptCreateView(generics.CreateAPIView):
#     """ 
#     POST /api/exercises/attempts/ 
#     Accepts an audio file and an exercise ID.
#     """
#     queryset = SpeechAttempt.objects.all()
#     serializer_class = SpeechAttemptSerializer
#     permission_classes = [permissions.IsAuthenticated]
    
#     # CRITICAL: Tell DRF to accept file uploads, not just JSON
#     parser_classes = [MultiPartParser, FormParser]

#     def perform_create(self, serializer):
#         # 1. Save the initial database record and tie it to the logged-in user
#         attempt = serializer.save(user=self.request.user)
        
#         # 2. Get the absolute file path of the saved audio
#         raw_audio_path = attempt.audio_file.path
        
#         # 3. Pass it to our processing pipeline
#         # (In Module 5, we will pass this normalized path to Whisper!)
#         normalized_path = normalize_audio_for_ai(raw_audio_path)
        
#         # Optional: We could update the database to point to the new .wav file here,
#         # but for now, we just ensure the pipeline successfully creates it.


# module 5

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import TherapyExercise, SpeechAttempt
from .serializers import TherapyExerciseSerializer, SpeechAttemptSerializer
from .services import normalize_audio_for_ai
from .ai_engine import analyze_speech_attempt  # <-- IMPORT NEW AI ENGINE

class SpeechAttemptCreateView(generics.CreateAPIView):
    queryset = SpeechAttempt.objects.all()
    serializer_class = SpeechAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        # 1. Save the file to the database
        attempt = serializer.save(user=self.request.user)
        raw_audio_path = attempt.audio_file.path
        
        # 2. Normalize the audio (16kHz Mono WAV)
        normalized_path = normalize_audio_for_ai(raw_audio_path)
        
        # 3. Run the AI Analysis
        target_text = attempt.exercise.target_text
        transcribed_text, accuracy_score = analyze_speech_attempt(
            normalized_path, 
            target_text
        )
        
        # 4. Save the AI results back to the database
        attempt.transcribed_text = transcribed_text
        attempt.overall_score = accuracy_score
        attempt.save()
        
        # Optional: We will handle granular phoneme-level scoring in Module 6!