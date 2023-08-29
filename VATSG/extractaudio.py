from moviepy.video.io.VideoFileClip import VideoFileClip


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