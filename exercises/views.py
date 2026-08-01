

# MODULE 10:

from django.conf import settings
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser

from .models import TherapyExercise, SpeechAttempt
from .serializers import TherapyExerciseSerializer, SpeechAttemptSerializer
from .services import normalize_audio_for_ai
from .ai_engine import analyze_speech_attempt, analyze_phonemes
from .llm_service import generate_therapeutic_feedback

from users.services import recalculate_user_weak_phonemes, update_user_gamification

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class ExerciseListView(generics.ListAPIView):
    """
    GET /api/exercises/ - Returns available therapy exercises
    """
    queryset = TherapyExercise.objects.all()
    serializer_class = TherapyExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    # --- NEW CODE: CACHING ---
    # Cache the output of this view in server memory for 15 minutes (60 seconds * 15)
    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SpeechAttemptCreateView(generics.CreateAPIView):
    """
    POST /api/exercises/attempts/ 
    Accepts an audio file and an exercise ID, normalizes the audio,
    runs Whisper transcription, calculates phoneme scores, and saves the results.
    """
    queryset = SpeechAttempt.objects.all()
    serializer_class = SpeechAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        # 1. Save initial record
        attempt = serializer.save(user=self.request.user)
        raw_audio_path = attempt.audio_file.path
        
        # 2. Normalize the audio (16kHz Mono WAV)
        normalized_path = normalize_audio_for_ai(raw_audio_path)
        
        # 3. Update the database record to point to the clean normalized WAV file
        relative_wav_path = normalized_path.replace(settings.MEDIA_ROOT, "").lstrip("/\\")
        attempt.audio_file.name = relative_wav_path
        
        # 4. Run AI Analysis (Word-level transcription & phoneme breakdown)
        target_text = attempt.exercise.target_text
        is_interview = attempt.exercise.is_interview_mode  # <-- NEW: Grab interview mode status
        
        transcribed_text, accuracy_score = analyze_speech_attempt(
            normalized_path, 
            target_text
        )
        phoneme_scores = analyze_phonemes(target_text, transcribed_text)
        
        # --- NEW CODE: Generate LLM Feedback ---
        ai_feedback = generate_therapeutic_feedback(
            target_text, 
            transcribed_text, 
            phoneme_scores, 
            is_interview
        )
        
        # 5. Save final results to PostgreSQL
        attempt.transcribed_text = transcribed_text
        attempt.overall_score = accuracy_score
        attempt.phoneme_scores = phoneme_scores
        attempt.ai_feedback = ai_feedback  # <-- NEW: Save the LLM paragraph
        attempt.save()

        # --- Update Background Stats ---
        # Automatically update the user's AI profile based on this new attempt!
        recalculate_user_weak_phonemes(self.request.user.profile)
        # Award XP and update daily streak
        update_user_gamification(self.request.user.profile, accuracy_score)


class RecommendedExerciseListView(generics.ListAPIView):
    """
    GET /api/exercises/recommended/
    Returns exercises dynamically tailored to the user's weak phonemes.
    """
    serializer_class = TherapyExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_profile = self.request.user.profile
        weak_phonemes = user_profile.target_phonemes

        if not weak_phonemes:
            # If they have no weak phonemes (or are brand new), 
            # recommend random easy baseline exercises.
            return TherapyExercise.objects.filter(difficulty='EASY')[:5]

        # PostgreSQL JSONB querying magic!
        # We want to find any exercise where the exercise's target_phonemes array
        # overlaps with the user's weak_phonemes array.
        
        # Build an OR query dynamically: Q(target_phonemes__contains="R") | Q(...)
        query = Q()
        for phoneme in weak_phonemes:
            query |= Q(target_phonemes__contains=phoneme)

        # Return a unique set of matched exercises
        return TherapyExercise.objects.filter(query).distinct()[:10]





# # # # from django.shortcuts import render

# # # # # Create your views here.


# # from rest_framework import generics, permissions, status
# # from rest_framework.response import Response
# # from rest_framework.parsers import MultiPartParser, FormParser
# # from .models import TherapyExercise, SpeechAttempt
# # from .serializers import TherapyExerciseSerializer, SpeechAttemptSerializer
# # from .services import normalize_audio_for_ai

# # class ExerciseListView(generics.ListAPIView):
# #     """ GET /api/exercises/ - Returns available therapy exercises """
# #     queryset = TherapyExercise.objects.all()
# #     serializer_class = TherapyExerciseSerializer
# #     permission_classes = [permissions.IsAuthenticated]

# # # class SpeechAttemptCreateView(generics.CreateAPIView):
# # #     """ 
# # #     POST /api/exercises/attempts/ 
# # #     Accepts an audio file and an exercise ID.
# # #     """
# # #     queryset = SpeechAttempt.objects.all()
# # #     serializer_class = SpeechAttemptSerializer
# # #     permission_classes = [permissions.IsAuthenticated]
    
# # #     # CRITICAL: Tell DRF to accept file uploads, not just JSON
# # #     parser_classes = [MultiPartParser, FormParser]


# # # correction:

# # class SpeechAttemptCreateView(generics.CreateAPIView):
# #     queryset = SpeechAttempt.objects.all()
# #     serializer_class = SpeechAttemptSerializer
# #     permission_classes = [permissions.IsAuthenticated]
# #     parser_classes = [MultiPartParser, FormParser]

# #     def perform_create(self, serializer):
# #         # 1. Save initial record
# #         attempt = serializer.save(user=self.request.user)
# #         raw_audio_path = attempt.audio_file.path
        
# #         # 2. Normalize the audio (16kHz Mono WAV)
# #         normalized_path = normalize_audio_for_ai(raw_audio_path)
        
# #         # 3. CRITICAL FIX: Point the database record to the clean normalized WAV file
# #         # We strip the absolute path down to a relative path Django's FileField expects
# #         relative_wav_path = normalized_path.replace(settings.MEDIA_ROOT, "").lstrip("/\\")
# #         attempt.audio_file.name = relative_wav_path
        
# #         # 4. Run AI Analysis
# #         target_text = attempt.exercise.target_text
# #         transcribed_text, accuracy_score = analyze_speech_attempt(
# #             normalized_path, 
# #             target_text
# #         )
# #         phoneme_scores = analyze_phonemes(target_text, transcribed_text)
        
# #         # 5. Save final results
# #         attempt.transcribed_text = transcribed_text
# #         attempt.overall_score = accuracy_score
# #         attempt.phoneme_scores = phoneme_scores
# #         attempt.save()
# #     # def perform_create(self, serializer):
# #     #     # 1. Save the initial database record and tie it to the logged-in user
# #     #     attempt = serializer.save(user=self.request.user)
        
# #     #     # 2. Get the absolute file path of the saved audio
# #     #     raw_audio_path = attempt.audio_file.path
        
# #     #     # 3. Pass it to our processing pipeline
# #     #     # (In Module 5, we will pass this normalized path to Whisper!)
# #     #     normalized_path = normalize_audio_for_ai(raw_audio_path)
        
# #     #     # Optional: We could update the database to point to the new .wav file here,
# #     #     # but for now, we just ensure the pipeline successfully creates it.
# # # modeule6:

# # def perform_create(self, serializer):
# #         attempt = serializer.save(user=self.request.user)
# #         raw_audio_path = attempt.audio_file.path
# #         normalized_path = normalize_audio_for_ai(raw_audio_path)
        
# #         target_text = attempt.exercise.target_text
        
# #         # 1. Get Word-level Transcription & Score
# #         from .ai_engine import analyze_speech_attempt, analyze_phonemes
# #         transcribed_text, accuracy_score = analyze_speech_attempt(
# #             normalized_path, 
# #             target_text
# #         )
        
# #         # 2. Get Phoneme-level breakdown (e.g., {"R": 50.0, "T": 100.0})
# #         phoneme_scores = analyze_phonemes(target_text, transcribed_text)
        
# #         # 3. Save everything to PostgreSQL
# #         attempt.transcribed_text = transcribed_text
# #         attempt.overall_score = accuracy_score
# #         attempt.phoneme_scores = phoneme_scores # This saves seamlessly to our JSONField!
# #         attempt.save()

# # # module 5

# # from rest_framework import generics, permissions, status
# # from rest_framework.response import Response
# # from rest_framework.parsers import MultiPartParser, FormParser

# # from .models import TherapyExercise, SpeechAttempt
# # from .serializers import TherapyExerciseSerializer, SpeechAttemptSerializer
# # from .services import normalize_audio_for_ai
# # from .ai_engine import analyze_speech_attempt  # <-- IMPORT NEW AI ENGINE

# # class SpeechAttemptCreateView(generics.CreateAPIView):
# #     queryset = SpeechAttempt.objects.all()
# #     serializer_class = SpeechAttemptSerializer
# #     permission_classes = [permissions.IsAuthenticated]
# #     parser_classes = [MultiPartParser, FormParser]

# #     def perform_create(self, serializer):
# #         # 1. Save the file to the database
# #         attempt = serializer.save(user=self.request.user)
# #         raw_audio_path = attempt.audio_file.path
        
# #         # 2. Normalize the audio (16kHz Mono WAV)
# #         normalized_path = normalize_audio_for_ai(raw_audio_path)
        
# #         # 3. Run the AI Analysis
# #         target_text = attempt.exercise.target_text
# #         transcribed_text, accuracy_score = analyze_speech_attempt(
# #             normalized_path, 
# #             target_text
# #         )
        
# #         # 4. Save the AI results back to the database
# #         attempt.transcribed_text = transcribed_text
# #         attempt.overall_score = accuracy_score
# #         attempt.save()
        
# #         # Optional: We will handle granular phoneme-level scoring in Module 6!



# # clean code:
# from users.services import recalculate_user_weak_phonemes

# from django.conf import settings
# from rest_framework import generics, permissions
# from rest_framework.parsers import MultiPartParser, FormParser

# from .models import TherapyExercise, SpeechAttempt
# from .serializers import TherapyExerciseSerializer, SpeechAttemptSerializer
# from .services import normalize_audio_for_ai
# from .ai_engine import analyze_speech_attempt, analyze_phonemes

# from users.services import update_user_gamification

# from .llm_service import generate_therapeutic_feedback


# class ExerciseListView(generics.ListAPIView):
#     """
#     GET /api/exercises/ - Returns available therapy exercises
#     """
#     queryset = TherapyExercise.objects.all()
#     serializer_class = TherapyExerciseSerializer
#     permission_classes = [permissions.IsAuthenticated]


# class SpeechAttemptCreateView(generics.CreateAPIView):
#     """
#     POST /api/exercises/attempts/ 
#     Accepts an audio file and an exercise ID, normalizes the audio,
#     runs Whisper transcription, calculates phoneme scores, and saves the results.
#     """
#     queryset = SpeechAttempt.objects.all()
#     serializer_class = SpeechAttemptSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser]

#     def perform_create(self, serializer):
#         # 1. Save initial record
#         attempt = serializer.save(user=self.request.user)
#         raw_audio_path = attempt.audio_file.path
        
#         # 2. Normalize the audio (16kHz Mono WAV)
#         normalized_path = normalize_audio_for_ai(raw_audio_path)
        
#         # 3. Update the database record to point to the clean normalized WAV file
#         relative_wav_path = normalized_path.replace(settings.MEDIA_ROOT, "").lstrip("/\\")
#         attempt.audio_file.name = relative_wav_path
        
#         # 4. Run AI Analysis (Word-level transcription & phoneme breakdown)
#         target_text = attempt.exercise.target_text
#         transcribed_text, accuracy_score = analyze_speech_attempt(
#             normalized_path, 
#             target_text
#         )
#         phoneme_scores = analyze_phonemes(target_text, transcribed_text)
        
#         # 5. Save final results to PostgreSQL
#         attempt.transcribed_text = transcribed_text
#         attempt.overall_score = accuracy_score
#         attempt.phoneme_scores = phoneme_scores
#         attempt.save()
#         # --- NEW CODE ---
#         # Automatically update the user's AI profile based on this new attempt!
#         recalculate_user_weak_phonemes(self.request.user.profile)
#         # --- NEW CODE ---
#         # Award XP and update daily streak
#         update_user_gamification(self.request.user.profile, accuracy_score)


# from django.db.models import Q

# class RecommendedExerciseListView(generics.ListAPIView):
#     """
#     GET /api/exercises/recommended/
#     Returns exercises dynamically tailored to the user's weak phonemes.
#     """
#     serializer_class = TherapyExerciseSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user_profile = self.request.user.profile
#         weak_phonemes = user_profile.target_phonemes

#         if not weak_phonemes:
#             # If they have no weak phonemes (or are brand new), 
#             # recommend random easy baseline exercises.
#             return TherapyExercise.objects.filter(difficulty='EASY')[:5]

#         # PostgreSQL JSONB querying magic!
#         # We want to find any exercise where the exercise's target_phonemes array
#         # overlaps with the user's weak_phonemes array.
        
#         # Build an OR query dynamically: Q(target_phonemes__contains="R") | Q(...)
#         query = Q()
#         for phoneme in weak_phonemes:
#             query |= Q(target_phonemes__contains=phoneme)

#         # Return a unique set of matched exercises
#         return TherapyExercise.objects.filter(query).distinct()[:10]
