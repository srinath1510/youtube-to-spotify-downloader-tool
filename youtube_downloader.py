import yt_dlp
import os

class YouTubeDownloader:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def download_audio(self, youtube_url: str) -> str:
        """
        Downloads audio from a YouTube URL and returns the path to the downloaded file.
        yt-dlp can handle conversion directly.
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3', # or 'm4a'
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'ignoreerrors': True, # To continue if some videos in a playlist fail
            'progress_hooks': [self._download_progress_hook],
            'quiet': False # Set to True for less verbose output
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=True)
                # yt-dlp renames the file after conversion, so we need to get the final path
                # This might require inspecting the postprocessor output or using a simpler outtmpl and then renaming.
                # A common pattern is to get the 'filepath' from the info_dict after postprocessing
                # However, for 'FFmpegExtractAudio', the new filename is usually title.ext
                # Let's simplify and rely on the outtmpl naming convention for the purpose of this example.
                # The actual file will be <title>.mp3 after conversion.
                original_filename = ydl.prepare_filename(info_dict)
                final_filename_base = os.path.splitext(original_filename)[0]
                final_audio_path = f"{final_filename_base}.mp3" # Assuming mp3 conversion

                if not os.path.exists(final_audio_path):
                     print(f"Warning: Expected file {final_audio_path} not found after download/conversion. yt-dlp might have named it differently or failed.")
                     # Fallback: try to find any new .mp3 in the output_dir that matches part of the title
                     for f in os.listdir(self.output_dir):
                         if info_dict.get('title') and info_dict['title'].lower() in f.lower() and f.endswith('.mp3'):
                             final_audio_path = os.path.join(self.output_dir, f)
                             print(f"Found potentially matching file: {final_audio_path}")
                             break
                     if not os.path.exists(final_audio_path):
                         raise FileNotFoundError(f"Could not locate the downloaded audio file for {youtube_url}")


                print(f"Downloaded and converted audio to: {final_audio_path}")
                return final_audio_path
        except yt_dlp.DownloadError as e:
            print(f"Error downloading YouTube video: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred during download: {e}")
            raise

    def _download_progress_hook(self, d):
        if d['status'] == 'downloading':
            print(f"Downloading: {d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']}")
        elif d['status'] == 'finished':
            print("Download complete.")
        elif d['status'] == 'error':
            print(f"Download error: {d['error']}")
