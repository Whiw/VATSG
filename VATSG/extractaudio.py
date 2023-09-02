from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip


def extract_audio_from_video(input_video_path, output_audio_path):
    try:
        video_clip = VideoFileClip(input_video_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_audio_path)
        audio_clip.close()
        video_clip.close()
        print("Audio extracted successfully.")
    except Exception as e:
        print(f"Error: {e}")

def get_media_length_in_time(file_path):
    if is_audio(file_path):
        clip = AudioFileClip(file_path)
    else:
        clip = VideoFileClip(file_path)
    duration = int(clip.duration)
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes}:{seconds}"

def is_audio(file_path):
    audio_extensions = ['mp3', 'wav', 'aac']
    video_extensions = ['mp4', 'avi', 'mkv']

    extension = file_path.split('.')[-1].lower()

    if extension in audio_extensions:
        return True
    elif extension in video_extensions:
        return False