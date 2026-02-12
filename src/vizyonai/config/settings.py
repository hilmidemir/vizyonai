import os
from dotenv import load_dotenv

load_dotenv()

LMSTUDIO_BASE_URL = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
LMSTUDIO_MODEL = os.getenv("LMSTUDIO_MODEL", "qwen3-8b")

DOMAIN = os.getenv("DOMAIN", "electronics")

DATA_PRODUCTS_PATH = os.getenv("DATA_PRODUCTS_PATH", "data/products.csv")
DATA_PHONES_PATH = os.getenv("DATA_PHONES_PATH", "data/phone_specs.csv")
