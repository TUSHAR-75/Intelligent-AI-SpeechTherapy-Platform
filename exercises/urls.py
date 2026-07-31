# from django.urls import path
# from .views import ExerciseListView, SpeechAttemptCreateView

# urlpatterns = [
#     path('', ExerciseListView.as_view(), name='exercise_list'),
#     path('attempts/', SpeechAttemptCreateView.as_view(), name='speech_attempt_create'),
# ]

# //module7

from django.urls import path
from .views import (
    ExerciseListView, 
    SpeechAttemptCreateView,
    RecommendedExerciseListView # <-- Import new view
)

urlpatterns = [
    path('', ExerciseListView.as_view(), name='exercise_list'),
    
    # IMPORTANT: Put /recommended/ BEFORE /attempts/ to prevent routing conflicts
    path('recommended/', RecommendedExerciseListView.as_view(), name='exercise_recommended'),
    
    path('attempts/', SpeechAttemptCreateView.as_view(), name='speech_attempt_create'),
]