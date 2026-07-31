from g2p_en import G2p

# Initialize the G2P engine globally alongside Whisper
g2p = G2p()

import whisper
import jiwer
import logging

logger = logging.getLogger(__name__)

# Load the model into memory ONCE when the server starts.
# We use 'tiny' or 'base' for fast local development. 
# You can upgrade to 'small' or 'medium' for production.
print("Loading Whisper AI Model... this may take a moment on startup.")
whisper_model = whisper.load_model("base")

def analyze_speech_attempt(audio_path, target_text):
    """
    Transcribes the audio file and compares it to the target text.
    Returns the transcribed text and the calculated accuracy score (0-100).
    """
    try:
        # 1. Transcribe the audio using Whisper
        # We enforce English ('en') to prevent the AI from accidentally translating 
        # heavily accented English into another language.
        result = whisper_model.transcribe(audio_path, language='en')
        transcribed_text = result['text'].strip()

        # 2. Normalize both texts (lowercase, remove punctuation) for fair comparison
        # jiwer transforms handle standardizing the strings
        transformation = jiwer.Compose([
            jiwer.ToLowerCase(),
            jiwer.RemovePunctuation(),
            jiwer.RemoveMultipleSpaces(),
            jiwer.Strip(),
        ])
        
        clean_target = transformation(target_text)
        clean_transcription = transformation(transcribed_text)

        # 3. Calculate Word Error Rate (WER)
        # If texts are identical, WER is 0.0. If completely wrong, WER can be > 1.0.
        error_rate = jiwer.wer(clean_target, clean_transcription)
        
        # 4. Convert WER to an Accuracy Percentage (0 to 100)
        # We use max(0, ...) to ensure negative scores don't happen on terrible attempts
        accuracy_score = max(0.0, (1.0 - error_rate) * 100.0)

        return transcribed_text, round(accuracy_score, 2)

    except Exception as e:
        logger.error(f"AI Engine Error: {str(e)}")
        raise RuntimeError("Failed to analyze speech audio.")



def analyze_phonemes(target_text, transcribed_text):
    """
    Converts both texts to phonemes and calculates accuracy per phoneme.
    Returns a dictionary of phoneme scores.
    """
    # 1. Convert texts to lists of phonemes
    # g2p("hello") -> ['HH', 'AH0', 'L', 'OW1']
    # We filter out spaces and punctuation (which g2p leaves as strings)
    target_phonemes = [p for p in g2p(target_text) if p.isalpha()]
    spoken_phonemes = [p for p in g2p(transcribed_text) if p.isalpha()]

    # 2. Track occurrences and errors
    # We will build a dictionary: {"R": {"total": 2, "correct": 1}, ...}
    tracking = {phoneme: {"total": 0, "correct": 0} for phoneme in set(target_phonemes)}
    
    for phoneme in target_phonemes:
        tracking[phoneme]["total"] += 1
        # Simple heuristic alignment for MVP:
        # If the phoneme exists in the spoken text, we count it as correct 
        # and remove it from the spoken list to handle duplicates properly.
        if phoneme in spoken_phonemes:
            tracking[phoneme]["correct"] += 1
            spoken_phonemes.remove(phoneme)

    # 3. Calculate percentages
    phoneme_scores = {}
    for phoneme, stats in tracking.items():
        # Strip numbers (e.g., 'AH0' -> 'AH') which represent stress markers
        base_phoneme = ''.join([c for c in phoneme if not c.isdigit()])
        
        accuracy = (stats["correct"] / stats["total"]) * 100
        
        # If the base phoneme is already in our dict, average it out
        if base_phoneme in phoneme_scores:
            phoneme_scores[base_phoneme] = (phoneme_scores[base_phoneme] + accuracy) / 2
        else:
            phoneme_scores[base_phoneme] = accuracy

    # Round all scores
    for k in phoneme_scores:
        phoneme_scores[k] = round(phoneme_scores[k], 2)

    return phoneme_scores