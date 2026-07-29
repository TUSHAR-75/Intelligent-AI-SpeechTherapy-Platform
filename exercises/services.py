import os
from pydub import AudioSegment
from django.conf import settings

def normalize_audio_for_ai(file_path):
    """
    Takes an uploaded audio file of any format (webm, mp3, ogg, m4a),
    and converts it to 16kHz, Mono, WAV format required by Whisper/Wav2Vec2.
    
    Returns the file path of the new normalized audio.
    """
    try:
        # Load the audio file (pydub automatically detects the input format)
        audio = AudioSegment.from_file(file_path)
        
        # 1. Set to Mono (1 channel)
        audio = audio.set_channels(1)
        
        # 2. Set Frame Rate (Sample Rate) to 16,000 Hz
        audio = audio.set_frame_rate(16000)
        
        # Define output path (replace original extension with .wav)
        base_name = os.path.splitext(file_path)[0]
        output_path = f"{base_name}_normalized.wav"
        
        # Export as standard PCM WAV
        audio.export(output_path, format="wav")
        
        return output_path
        
    except Exception as e:
        raise ValueError(f"Failed to process audio file: {str(e)}")