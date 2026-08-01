import os
import requests
import logging

logger = logging.getLogger(__name__)

def generate_therapeutic_feedback(target_text, transcribed_text, phoneme_scores, is_interview):
    """
    Constructs a dynamic prompt and calls an LLM API to generate human-like feedback.
    """
    # 1. Isolate the phonemes the user failed (score < 80%)
    failed_phonemes = [p for p, score in phoneme_scores.items() if score < 80.0]
    failed_str = ", ".join(failed_phonemes) if failed_phonemes else "None! Perfect pronunciation."

    # 2. Contextual System Prompting
    # We alter the persona based on whether this is an interview or clinical therapy.
    if is_interview:
        persona = "You are a senior tech recruiter and communication coach."
        focus = "Focus on confidence, clarity, and pacing."
    else:
        persona = "You are an empathetic, professional speech therapist."
        focus = f"Focus on articulation. The user struggled with these phonemes: {failed_str}."

    # 3. Construct the exact prompt structure
    prompt = f"""
    {persona}
    
    The user was asked to say: "{target_text}"
    The AI heard the user say: "{transcribed_text}"
    
    {focus}
    
    Write a short, encouraging 2-sentence feedback message to the user. 
    Acknowledge what they did well, and give one physical tip (e.g., tongue placement, breathing) on how to improve.
    Keep it warm and professional. Do not output anything other than the feedback.
    """

    # 4. API Call to your LLM of choice (Example using a generic REST payload)
    # Note: For production, you would use an official SDK like `openai` or `google-generativeai`.
    try:
        # Pseudo-code for an API call. You would inject your specific provider's URL and API key here.
        # response = requests.post(
        #     "https://api.your-open-source-llm-provider.com/v1/completions",
        #     headers={"Authorization": f"Bearer {os.getenv('LLM_API_KEY')}"},
        #     json={"prompt": prompt, "max_tokens": 100, "temperature": 0.7}
        # )
        # return response.json()["choices"][0]["text"].strip()
        
        # For our immediate local development, we return a smart mocked response:
        if not failed_phonemes:
            return "Fantastic job! Your articulation was crystal clear and confident. Keep up the great work."
        
        return f"Good effort! I noticed some slight blurring on the {failed_str} sounds. Next time, try slowing down slightly and pressing your tongue a bit firmer against the roof of your mouth for those consonants."

    except Exception as e:
        logger.error(f"LLM Generation failed: {str(e)}")
        return "Great effort! Check your phoneme breakdown chart to see exactly where you can improve next time."