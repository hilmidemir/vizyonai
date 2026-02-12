from openai import OpenAI
from vizyonai.config.settings import LMSTUDIO_BASE_URL

def get_client() -> OpenAI:
    return OpenAI(base_url=LMSTUDIO_BASE_URL, api_key="lm-studio", timeout=8.0)
