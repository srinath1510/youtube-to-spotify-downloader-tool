import os
from config import Config
from youtube_downloader import YouTubeDownloader
from metadata_processor import MetadataProcessor
import shutil

class Orchestrator:
    def __init__(self, llm_provider: str, output_dir: str = None):
        self.config = Config()
        self.llm_provider = llm_provider
        self.api_key = self.config.get_llm_api_key(llm_provider)
        self.output_dir = output_dir if output_dir else self.config.default_output_dir
        self.config.ensure_output_dir_exists(self.output_dir)

        self.downloader = YouTubeDownloader(output_dir=self.output_dir)
        self.metadata_processor = MetadataProcessor(llm_provider=llm_provider, api_key=self.api_key)

    def save_youtube_to_spotify_local(self, youtube_url: str):
        print(f"Starting process for YouTube URL: {youtube_url}")
        downloaded_file_path = None
        try:
            # 1. Extract YouTube info (title and thumbnail for LLM and art)
            youtube_title, thumbnail_url = self.metadata_processor.extract_youtube_title_and_thumbnail(youtube_url)
            if not youtube_title:
                raise ValueError("Could not extract YouTube title.")
            print(f"Extracted YouTube Title: '{youtube_title}'")
            if thumbnail_url:
                print(f"Extracted Thumbnail URL: {thumbnail_url}")

            # 2. Download and convert audio
            downloaded_file_path = self.downloader.download_audio(youtube_url)
            print(f"Audio downloaded to: {downloaded_file_path}")

            # 3. Infer metadata using LLM
            print("Inferring metadata using LLM...")
            inferred_metadata = self.metadata_processor.infer_metadata_with_llm(youtube_title)
            title = inferred_metadata.get('title')
            artist = inferred_metadata.get('artist')
            print(f"Inferred Metadata: Title='{title}', Artist='{artist}'")

            # 4. Set metadata on the downloaded file
            print("Setting ID3 tags...")
            self.metadata_processor.set_audio_metadata(downloaded_file_path, title, artist, thumbnail_url)
            print("Metadata successfully set.")

            # Note: Spotify needs time to pick up new files.
            print("\nProcess complete!")
            print(f"File saved to: {downloaded_file_path}")
            print("Please open Spotify, navigate to 'Local Files', and the new track should appear shortly.")
            print("You might need to restart Spotify or wait a few minutes for it to rescan.")

        except Exception as e:
            print(f"\nAn error occurred during the process: {e}")
            print("Please ensure your API key is correct and the YouTube URL is valid.")
            # Clean up partial downloads if any
            if downloaded_file_path and os.path.exists(downloaded_file_path):
                os.remove(downloaded_file_path)
                print(f"Cleaned up partial file: {downloaded_file_path}")