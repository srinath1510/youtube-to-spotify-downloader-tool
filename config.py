import os

class Config:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.default_output_dir = os.path.expanduser("~/Music/SpotifyLocalFiles")

    def get_llm_api_key(self, llm_provider: str):
        if llm_provider.lower() == "openai":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set.")
            return self.openai_api_key
        elif llm_provider.lower() == "claude":
            if not self.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
            return self.anthropic_api_key
        elif llm_provider.lower() == "gemini":
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set.")
            return self.gemini_api_key
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}. Choose 'openai', 'claude', or 'gemini'.")
    
    def ensure_output_dir_exists(self, path: str):
        os.makedirs(path, exist_ok=True)