Markdown

# Spotify Local File Saver

**Automate the tedious process of getting YouTube audio into your Spotify Local Files, complete with intelligent metadata tagging and album art!**

This tool helps you download audio from YouTube videos, convert them to MP3 or M4A, intelligently set metadata (like Title, Artist, and Album Art) using an LLM, and save them directly to a directory Spotify can access. No more manual conversions or metadata editing!

**What this tool does:**

* Downloads audio from a YouTube video link.
* Converts the audio to MP3 or M4A format (user selectable).
* Uses a powerful AI model (Gemini, OpenAI, or Claude) to accurately infer and set the song **Title**, **Artist**, and fetch **Album Art**.
* Places the processed audio file directly into your designated Spotify Local Files directory.

**What this tool DOES NOT do:**

* Directly play the song in Spotify after download. Due to Spotify's API limitations, there's no public way for an external tool to automatically command Spotify to play a newly added local file. You'll still need to open Spotify and select the track from your "Local Files."

---

## 🚀 Getting Started

Follow these steps to get the Spotify Local File Saver up and running on your machine.

### Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.8+**:
    * Download from [python.org](https://www.python.org/downloads/).
2.  **`ffmpeg`**: Essential for audio processing and conversion.
    * **macOS (Homebrew):** `brew install ffmpeg`
    * **Ubuntu/Debian:** `sudo apt update && sudo apt install ffmpeg`
    * **Windows:** Download the binaries from [ffmpeg.org](https://ffmpeg.org/download.html) and add the `/bin` directory to your system's PATH environment variable.
3.  **An LLM API Key**: Choose one of the following providers. This tool uses AI to intelligently extract metadata.
    * **Google Gemini (Recommended Free Tier):**
        * Go to [Google AI Studio](https://aistudio.google.com/app/apikey) to get your **GEMINI\_API\_KEY**. This offers a generous free tier for personal use.
    * **OpenAI:**
        * Go to [OpenAI API Keys](https://platform.openai.com/account/api-keys) to get your **OPENAI\_API\_KEY**.
    * **Anthropic (Claude):**
        * Go to [Anthropic Console](https://console.anthropic.com/settings/keys) to get your **ANTHROPIC\_API\_KEY**.

### Installation

1.  **Clone the Repository:**

    ```bash
    git clone [https://github.com/srinath1510/youtube-to-spotify-downloader-tool.git](https://github.com/srinath1510/youtube-to-spotify-downloader-tool.git)
    cd youtube-to-spotify-downloader-tool
    ```

2.  **Install Python Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Your API Key:**

    This tool requires an API key for the Large Language Model (LLM) you choose to use (Gemini, OpenAI, or Claude). **Your API key should be kept secret and never committed to version control.**

    We use the `python-dotenv` library to easily load your API key without hardcoding it.

    1.  **Create a `.env` file:**
        In the root directory of this project, create a new file named `.env`. You can simply copy the contents of `.env.example` into your new `.env` file.

        ```bash
        cp .env.example .env
        ```

    2.  **Add your API key:**
        Open the newly created `.env` file in a text editor. Uncomment (remove the `#`) the line for your chosen LLM provider and replace `"YOUR_API_KEY_HERE"` with your actual API key.

        **Example for Google Gemini:**

        ```
        # .env
        GEMINI_API_KEY="your_actual_gemini_api_key_goes_here"
        # OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
        # ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY_HERE"
        ```

        * **Google Gemini (Recommended Free Tier):**
            * Go to [Google AI Studio](https://aistudio.google.com/app/apikey) to get your **GEMINI\_API\_KEY**.
        * **OpenAI:**
            * Go to [OpenAI API Keys](https://platform.openai.com/account/api-keys) to get your **OPENAI\_API\_KEY**.
        * **Anthropic (Claude):**
            * Go to [Anthropic Console](https://console.anthropic.com/settings/keys) to get your **ANTHROPIC\_API\_KEY**.

        **Important:** The `.env` file is automatically ignored by Git, so your API key will not be accidentally uploaded to GitHub.

---

## ⚙️ Configure Spotify Local Files

This is a one-time setup step crucial for Spotify to recognize your new files.

1.  Open the Spotify desktop application.
2.  Go to **Settings** (click the gear icon).
3.  Scroll down to the **"Local Files"** section.
4.  Toggle **"Show Local Files"** on.
5.  Click **"ADD A SOURCE"** and select the directory where you want this tool to save your audio files. A common default is `~/Music/SpotifyLocalFiles` (on macOS/Linux) or a similar folder within your Music library on Windows. You can use this default or choose any folder you prefer.

    * **Note:** The tool will automatically create this directory if it doesn't exist when you run it.

---

## 🚀 Usage

Run the `main.py` script from your terminal.

```bash
python main.py <youtube_url> --llm_provider <provider> [--output_dir <path>] [--audio_format 