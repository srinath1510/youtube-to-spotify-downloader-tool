import os
import requests
from io import BytesIO
from PIL import Image

from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai

from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError, ID3, TIT2, TPE1, APIC
# TCON (genre), TDRC (date) are imported but not used in this version.


class MetadataProcessor:
    def __init__(self, llm_provider: str, api_key: str):
        self.llm_provider = llm_provider.lower()
        if self.llm_provider == "openai":
            self.llm_client = OpenAI(api_key=api_key)
            self.model = "gpt-4o" # Or "gpt-3.5-turbo"
        elif self.llm_provider == "claude":
            self.llm_client = Anthropic(api_key=api_key)
            self.model = "claude-3-opus-20240229" # Or other Claude models
        elif self.llm_provider == "gemini":
            genai.configure(api_key=api_key)
            self.llm_client = genai.GenerativeModel('gemini-1.5-pro') # Or 'gemini-1.5-flash', etc.
            self.model = 'gemini-1.5-pro'
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")

    def infer_metadata_with_llm(self, youtube_title: str) -> dict:
        """
        Uses an LLM to infer accurate Title and Artist from a YouTube video title.
        """
        prompt = (
            f"Given the YouTube video title '{youtube_title}', please extract the most likely song title and artist. "
            "For the 'title' field, remove any extraneous details such as 'Official Music Video', 'Official Visualizer', "
            "'Lyric Video', 'Audio', '4K', 'HD', 'Explicit', 'Remix', 'Live', 'Official Stream', 'Full Album', 'Mixtape', "
            "year numbers (e.g., '(2023)' or '[2023]'), or any text within parentheses or brackets that describes the video type "
            "or quality. Focus on the core song name. "
            "For the 'artist' field, identify the primary artist(s). If there are featured artists (e.g., 'ft.', 'feat.'), "
            "keep them as part of the 'title' field and *do not* include them in the 'artist' field unless they are a primary artist. "
            "Return the response as a JSON object with 'title' and 'artist' keys. "
            "If no clear artist or title is present after cleaning, use the original YouTube title for 'title' and 'Unknown' for 'artist'.\n\n"
            "Examples:\n"
            "Input: 'Lofi Girl - Coffee Shop Mix'\n"
            "Output: {{'title': 'Coffee Shop Mix', 'artist': 'Lofi Girl'}}\n\n"
            "Input: 'Joe Rogan Experience #1234 - Elon Musk'\n"
            "Output: {{'title': 'Joe Rogan Experience #1234 - Elon Musk', 'artist': 'Joe Rogan'}}\n\n"
            "Input: 'My original song - Amazing Tune by Me (Official Video)'\n"
            "Output: {{'title': 'Amazing Tune', 'artist': 'Me'}}\n\n"
            "Input: 'Playboi Carti - WASSUP/RATCHET ft. Lil Baby (Official Visualizer)'\n"
            "Output: {{'title': 'WASSUP/RATCHET ft. Lil Baby', 'artist': 'Playboi Carti'}}\n\n"
            "Input: 'Artist Name - Song Title (Lyric Video) [Explicit]'\n"
            "Output: {{'title': 'Song Title', 'artist': 'Artist Name'}}\n\n"
            f"Input: '{youtube_title}'"
        )
        try:
            import json # Import json locally as it's only used here
            if self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
            elif self.llm_provider == "claude":
                response = self.llm_client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text # Claude returns a list of content blocks
            elif self.llm_provider == "gemini":
                response = self.llm_client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
                )
                content = response.text # Gemini text attribute for generated content

            if not isinstance(content, str):
                print(f"Warning: LLM response content is not a string: {content}")
                content = str(content)

            # Attempt to parse JSON
            try:
                metadata = json.loads(content)
                if 'title' not in metadata or 'artist' not in metadata:
                    raise ValueError("LLM response missing 'title' or 'artist' keys.")
                metadata['title'] = self._clean_title_post_llm(metadata['title'])
                return metadata
            except json.JSONDecodeError as e:
                print(f"Error parsing LLM JSON response: {e}. Raw content: {content}")
                # Fallback if LLM doesn't return perfect JSON
                return {"title": youtube_title, "artist": "Unknown"}
        except Exception as e:
            print(f"Error calling LLM for metadata inference: {e}")
            return {"title": youtube_title, "artist": "Unknown"}
    
    def _clean_title_post_llm(self, title: str) -> str:
        """
        Applies a final cleanup to the title after LLM inference to remove common extraneous phrases.
        """
        # Define common patterns to remove (case-insensitive)
        patterns_to_remove = [
            r'\(?\s*(official\s*(music|lyric|visual)?\s*(video|audio|visualizer|stream))?\s*\)?',
            r'\[?\s*(official\s*(music|lyric|visual)?\s*(video|audio|visualizer|stream))?\s*\]?',
            r'\(?\s*(\d{4}|hd|4k|explicit|remix|live|full\s*album|mixtape)\s*\)?',
            r'\[?\s*(\d{4}|hd|4k|explicit|remix|live|full\s*album|mixtape)\s*\]?',
            r'\s*-\s*official\s*audio', # Specific edge case like "Song - Official Audio"
            r'\s*-\s*official\s*video',
            r'\s*\(?\s*(stream|version|lyrics?|clean|dirty|hq|full|uncensored)\s*\)?',
            r'\s*\[?\s*(stream|version|lyrics?|clean|dirty|hq|full|uncensored)\s*\]?',
            r'\s*\(?\s*ft\.?\s*.*\s*\)?', # If LLM leaves ft. in title, strip it
            r'\s*\[?\s*ft\.?\s*.*\s*\]?'
        ]

        cleaned_title = title
        for pattern in patterns_to_remove:
            cleaned_title = re.sub(pattern, '', cleaned_title, flags=re.IGNORECASE).strip()

        cleaned_title = re.sub(r'^[-\s\W]+|[-\s\W]+$', '', cleaned_title)

        return cleaned_title.strip() # Final strip

    def set_audio_metadata(self, file_path: str, title: str, artist: str, album_art_url: str = None):
        """
        Sets ID3 tags for MP3 files.
        """
        try:
            audio = MP3(file_path, ID3=ID3)
        except ID3NoHeaderError:
            audio = MP3(file_path)
            audio.add_tags()
            audio.save()
            audio = MP3(file_path, ID3=ID3)

        tags = audio.tags

        if tags is None:
            audio.add_tags()
            tags = audio.tags

        tags.clear()

        tags.add(TIT2(encoding=3, text=[title])) # Title (TIT2)
        tags.add(TPE1(encoding=3, text=[artist])) # Artist (TPE1)

        if album_art_url:
            image_data, image_format = self._fetch_and_process_image(album_art_url)
            if image_data:
                tags.add(
                    APIC(
                        encoding=3,  # UTF-8
                        mime=image_format,  # image/jpeg or image/png
                        type=3,  # 3 is for Front Cover
                        desc='Cover',
                        data=image_data
                    )
                )
        try:
            tags.save(v2_version=3) # Save with ID3v2.3 for broader compatibility
            print(f"Metadata set for '{file_path}': Title='{title}', Artist='{artist}'")
        except Exception as e:
            print(f"Error saving metadata to {file_path}: {e}")

    def _fetch_and_process_image(self, album_art_url: str) -> tuple[bytes | None, str | None]:
        """
        Fetches image data from a URL and processes it for embedding.
        Returns (image_data_bytes, mime_type) or (None, None) on failure.
        """
        if not album_art_url:
            return None, None

        try:
            response = requests.get(album_art_url)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            image_data = response.content

            img_byte_arr = BytesIO()
            img_format = None

            try:
                img = Image.open(BytesIO(image_data))
                if img.mode != 'RGB':
                    # Convert to RGB for broader compatibility
                    img = img.convert('RGB')

                # Determine the original image format and save accordingly, or default to JPEG
                if img.format == 'PNG':
                    img.save(img_byte_arr, format='png')
                    img_format = 'image/png'
                else: # Default to JPEG
                    img.save(img_byte_arr, format='jpeg')
                    img_format = 'image/jpeg'

                return img_byte_arr.getvalue(), img_format
            except Exception as img_e:
                print(f"Warning: Could not process image data from '{album_art_url}' for album art: {img_e}")
                return None, None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching album art from '{album_art_url}': {e}")
            return None, None
        except Exception as e:
            print(f"An unexpected error occurred while fetching/processing album art from '{album_art_url}': {e}")
            return None, None


    def extract_youtube_title_and_thumbnail(self, youtube_url: str) -> tuple[str, str]:
        """
        Extracts the YouTube video title and a high-quality thumbnail URL using yt-dlp.
        """
        import yt_dlp # Import locally as it's only used here
        ydl_opts = {
            'quiet': True,
            'extract_flat': True, # Only extract info, don't download
            'force_generic_extractor': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=False)
                title = info_dict.get('title', 'Unknown Title')
                thumbnails = info_dict.get('thumbnails', [])
                # Find the largest thumbnail
                thumbnail_url = None
                if thumbnails:
                    largest_thumbnail = sorted(thumbnails, key=lambda x: x.get('width', 0) * x.get('height', 0), reverse=True)
                    if largest_thumbnail:
                        thumbnail_url = largest_thumbnail[0].get('url')
                return title, thumbnail_url
        except Exception as e:
            print(f"Error extracting YouTube info: {e}")
            return "Unknown Title", None