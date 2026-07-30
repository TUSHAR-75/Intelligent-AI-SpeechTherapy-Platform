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