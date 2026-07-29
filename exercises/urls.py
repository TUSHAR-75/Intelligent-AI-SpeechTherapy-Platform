from django.urls import path
from .views import ExerciseListView, SpeechAttemptCreateView

urlpatterns = [
    path('', ExerciseListView.as_view(), name='exercise_list'),
    path('attempts/', SpeechAttemptCreateView.as_view(), name='speech_attempt_create'),
]