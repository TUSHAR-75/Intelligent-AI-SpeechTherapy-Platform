from collections import defaultdict
from exercises.models import SpeechAttempt

def recalculate_user_weak_phonemes(user_profile):
    """
    Analyzes the user's last 20 speech attempts to find phonemes
    where their average accuracy is below 80%.
    Updates the user_profile.target_phonemes list automatically.
    """
    # 1. Fetch the last 20 attempts for this user to get recent performance
    recent_attempts = SpeechAttempt.objects.filter(
        user=user_profile.user
    ).order_by('-created_at')[:20]

    if not recent_attempts:
        return []

    # 2. We use a defaultdict to group all scores by phoneme
    # Example state: {"R": [45.0, 55.0, 40.0], "S": [95.0, 100.0]}
    phoneme_history = defaultdict(list)
    total_overall_score = 0

    for attempt in recent_attempts:
        total_overall_score += attempt.overall_score
        
        # attempt.phoneme_scores is our JSON dictionary (e.g., {"R": 45.0, "T": 90.0})
        for phoneme, score in attempt.phoneme_scores.items():
            phoneme_history[phoneme].append(score)

    # 3. Calculate averages and identify the weak ones
    weak_phonemes = []
    for phoneme, scores in phoneme_history.items():
        avg_score = sum(scores) / len(scores)
        if avg_score < 80.0:  # 80% is our clinical threshold for "needs practice"
            weak_phonemes.append(phoneme)

    # 4. Update the User Profile metadata in the database
    user_profile.target_phonemes = weak_phonemes
    user_profile.overall_accuracy_score = total_overall_score / len(recent_attempts)
    user_profile.save()

    return weak_phonemes