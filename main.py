import os
import glob
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, vfx
import random
import sys
from caption_generator import generate_caption_clips
import time

# TikTok recommended resolution
VERTICAL_WIDTH = 1080
VERTICAL_HEIGHT = 1920

def load_audio(audio_filename):
    # Use the provided audio_filename to locate the file in the AudioAssets folder
    audio_path = os.path.join('AudioAssets', audio_filename)
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f'Audio file {audio_path} not found')
    print(f'Using audio file: {audio_path}')
    audio = AudioFileClip(audio_path)
    return audio

def load_video_assets():
    # Look for common video file extensions in VideoAssets folder
    video_extensions = ('*.mp4', '*.mov', '*.avi', '*.mkv')
    video_files = []
    for ext in video_extensions:
        video_files.extend(glob.glob(os.path.join('VideoAssets', ext)))
    if not video_files:
        raise FileNotFoundError('No video files found in VideoAssets')
    random.shuffle(video_files)  # Randomize the order of the video files
    print(f'Found {len(video_files)} video files.')
    return video_files

def resize_clip_vertical(clip):
    """
    Resize and crop the clip to vertical format while maintaining aspect ratio.
    This ensures the video fills the vertical space without distortion.
    """
    # Get the original size
    w, h = clip.size
    
    # Calculate target size maintaining aspect ratio
    target_ratio = VERTICAL_WIDTH / VERTICAL_HEIGHT
    current_ratio = w / h
    
    if current_ratio > target_ratio:
        # Video is too wide, scale based on height
        new_height = VERTICAL_HEIGHT
        new_width = int(new_height * current_ratio)
        resized = clip.resize(height=new_height)
        # Crop the excess width from the center
        x_center = new_width // 2
        x1 = x_center - (VERTICAL_WIDTH // 2)
        return resized.crop(x1=x1, y1=0, x2=x1+VERTICAL_WIDTH, y2=VERTICAL_HEIGHT)
    else:
        # Video is too tall, scale based on width
        new_width = VERTICAL_WIDTH
        new_height = int(new_width / current_ratio)
        resized = clip.resize(width=new_width)
        # Crop the excess height from the center
        y_center = new_height // 2
        y1 = y_center - (VERTICAL_HEIGHT // 2)
        return resized.crop(x1=0, y1=y1, x2=VERTICAL_WIDTH, y2=y1+VERTICAL_HEIGHT)

def process_video_clip(video_path):
    # Load the video asset
    clip = VideoFileClip(video_path)
    # Create a 5-second clip
    subclip_duration = min(5.0, clip.duration)
    base_clip = clip.subclip(0, subclip_duration)
    
    # Resize to vertical format
    resized_clip = resize_clip_vertical(base_clip)
    
    # Apply fade-in and fade-out of 1.2 seconds each
    processed_clip = resized_clip.fx(vfx.fadein, 1.2).fx(vfx.fadeout, 1.2)
    return processed_clip

def calculate_needed_clips(target_duration):
    # Each clip is 5 seconds
    clip_duration = 5
    # Add 1 to round up and ensure we have enough coverage
    return int(target_duration / clip_duration) + 1

def create_video_sequence(video_paths, target_duration):
    processed_clips = []
    total_duration = 0
    
    # Process only enough clips to reach target duration
    for video_path in video_paths:
        try:
            clip = process_video_clip(video_path)
            processed_clips.append(clip)
            total_duration += clip.duration
            
            # If we have enough clips, stop processing more
            if total_duration >= target_duration:
                break
                
        except Exception as e:
            print(f'Error processing {video_path}: {e}')
            continue
            
    if not processed_clips:
        raise ValueError('No video clips could be processed.')
        
    # Concatenate clips and handle any excess duration
    final_sequence = concatenate_videoclips(processed_clips)
    if final_sequence.duration > target_duration:
        final_sequence = final_sequence.subclip(0, target_duration)
        
    return final_sequence

def main():
    # Ask for user input
    print("\nEnter the audio filenames separated by commas (e.g., audio1.mp3, audio2.mp3):")
    user_input = input().strip()
    
    # Split the input and clean up whitespace
    audio_files = [filename.strip() for filename in user_input.split(',')]
    
    if not audio_files or audio_files[0] == '':
        print("No audio files provided. Exiting...")
        sys.exit(1)
    
    print(f"\nProcessing {len(audio_files)} audio files:")
    for filename in audio_files:
        print(f"- {filename}")
    
    # Start timing the total process
    total_start_time = time.time()
    
    for audio_filename in audio_files:
        try:
            # Start timing this video
            video_start_time = time.time()
            
            print(f"\nProcessing {audio_filename}...")
            
            # Load audio using the provided filename
            audio = load_audio(audio_filename)
            
            # Use the actual audio duration
            target_duration = audio.duration
            print(f"Video duration will be {target_duration:.2f} seconds")
            
            # Load video assets paths and calculate needed clips
            video_files = load_video_assets()
            needed_clips = calculate_needed_clips(target_duration)
            print(f"Will process {needed_clips} video clips for this audio")
            
            # Create video sequence with only the needed clips
            final_video = create_video_sequence(video_files[:needed_clips * 2], target_duration)

            # Generate caption clips
            print("Generating captions from audio...")
            audio_path = os.path.join('AudioAssets', audio_filename)
            caption_clips = generate_caption_clips(audio_path, (VERTICAL_WIDTH, VERTICAL_HEIGHT))

            # Combine video with captions
            final_output = CompositeVideoClip([final_video] + caption_clips, size=(VERTICAL_WIDTH, VERTICAL_HEIGHT))

            # Set the audio
            final_output = final_output.set_audio(audio)

            # Create output directory
            output_dir = os.path.join('OutputVideos')
            os.makedirs(output_dir, exist_ok=True)
            
            # Create the output path using a timestamp to ensure uniqueness
            timestamp = int(time.time())
            output_path = os.path.join(output_dir, f'video_{timestamp}.mp4')
            
            print(f"Rendering final video as {output_path}...")
            final_output.write_videofile(output_path, fps=24, audio_codec='aac')
            
            # Calculate and display time taken for this video
            video_end_time = time.time()
            video_duration = video_end_time - video_start_time
            minutes = int(video_duration // 60)
            seconds = int(video_duration % 60)
            print(f"\nCompleted {audio_filename} in {minutes} minutes and {seconds} seconds")
            
        except Exception as e:
            print(f"Error processing {audio_filename}: {e}")
            continue
    
    # Calculate and display total time taken
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    total_minutes = int(total_duration // 60)
    total_seconds = int(total_duration % 60)
    print(f"\nTotal processing time: {total_minutes} minutes and {total_seconds} seconds")

if __name__ == '__main__':
    main() 