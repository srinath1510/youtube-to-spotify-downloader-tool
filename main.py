import argparse
import os
from dotenv import load_dotenv

load_dotenv()

from orchestrator import Orchestrator
from config import Config

def main():
    parser = argparse.ArgumentParser(
        description="Save YouTube video audio to Spotify Local Files with automated metadata."
    )
    parser.add_argument(
        "youtube_url",
        help="The URL of the YouTube video"
    )
    parser.add_argument(
        "--output_dir",
        default=None,
        help=f"Optional: Directory where Spotify local files are configured. Defaults to '{Config().default_output_dir}'."
    )
    parser.add_argument(
        "--llm_provider",
        choices=['openai', 'claude', 'gemini'],
        required=True,
        help="Specify the LLM provider to use (openai or claude)."
    )

    args = parser.parse_args()

    if args.llm_provider == 'openai' and not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set it before running the script (e.g., export OPENAI_API_KEY='your_key').")
        return
    if args.llm_provider == 'claude' and not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Please set it before running the script (e.g., export ANTHROPIC_API_KEY='your_key').")
        return
    if args.llm_provider == 'gemini' and not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set it before running the script (e.g., export GEMINI_API_KEY='your_key').")
        return


    saver = Orchestrator(
        llm_provider=args.llm_provider,
        output_dir=args.output_dir
    )

    saver.save_youtube_to_spotify_local(args.youtube_url)

if __name__ == "__main__":
    main()