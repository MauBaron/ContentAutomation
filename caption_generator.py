import whisper_timestamped as whisper
from moviepy.editor import TextClip, CompositeVideoClip
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class CaptionPhrase:
    text: str
    start_time: float
    end_time: float

def group_words_into_phrases(words: List[Dict[str, Any]], target_words_per_phrase: int = 5) -> List[CaptionPhrase]:
    """
    Group words into natural phrases for captioning.
    Uses a combination of timing and number of words to create natural breaks.
    """
    phrases = []
    current_words = []
    current_start = 0
    
    for word in words:
        text = word["text"].strip()
        start = word["start"]
        end = word["end"]
        
        # Start a new phrase if:
        # 1. This is the first word
        # 2. We've reached our target word count
        # 3. There's a significant pause (> 0.7s)
        # 4. The current phrase would be too long to read
        if (not current_words or 
            len(current_words) >= target_words_per_phrase or
            (start - current_words[-1]["end"] > 0.7) or
            (end - current_start > 4.0)):
            
            if current_words:
                # Create a phrase from accumulated words
                phrase_text = " ".join(w["text"].strip() for w in current_words)
                phrases.append(CaptionPhrase(
                    text=phrase_text,
                    start_time=current_words[0]["start"],
                    end_time=current_words[-1]["end"]
                ))
            current_words = []
            current_start = start
        
        current_words.append(word)
    
    # Don't forget the last phrase
    if current_words:
        phrase_text = " ".join(w["text"].strip() for w in current_words)
        phrases.append(CaptionPhrase(
            text=phrase_text,
            start_time=current_words[0]["start"],
            end_time=current_words[-1]["end"]
        ))
    
    return phrases

def create_caption_clips(phrases: List[CaptionPhrase], 
                        video_size: tuple,
                        fontsize: int = 45) -> List[TextClip]:
    """
    Create a list of TextClips for each phrase with proper timing and styling.
    """
    caption_clips = []
    bounded_width = int(video_size[0] * 0.8)  # Bound the text to 80% of the video width

    for phrase in phrases:
        # Create text clip with automatic text wrapping using the caption method
        clip = (TextClip(phrase.text, 
                        fontsize=fontsize,
                        color='white',
                        method='caption',
                        size=(bounded_width, None))
                .set_position('center')  # Center both horizontally and vertically
                .set_start(phrase.start_time)
                .set_duration(phrase.end_time - phrase.start_time))

        caption_clips.append(clip)

    return caption_clips

def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe audio file using Whisper and return the result.
    """
    audio = whisper.load_audio(audio_path)
    model = whisper.load_model("base")  # Use base model for faster processing
    result = whisper.transcribe(model, audio, language="en")
    return result

def generate_caption_clips(audio_path: str, video_size: tuple) -> List[TextClip]:
    """
    Main function to generate caption clips from an audio file.
    """
    # Get transcription with timestamps
    result = transcribe_audio(audio_path)
    
    # Extract all words with their timestamps
    words = []
    for segment in result["segments"]:
        if "words" in segment:
            words.extend(segment["words"])
    
    # Group words into natural phrases
    phrases = group_words_into_phrases(words)
    
    # Create caption clips
    return create_caption_clips(phrases, video_size) 