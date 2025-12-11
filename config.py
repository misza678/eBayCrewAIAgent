import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-coder:14b")
    OPENAPI_FILE = os.getenv("OPENAPI_FILE", "data/ebay_openapi.json")
    
    # eBay Credentials
    EBAY_APP_ID = os.getenv("EBAY_APP_ID")
    EBAY_CERT_ID = os.getenv("EBAY_CERT_ID")
    EBAY_ENV = os.getenv("EBAY_ENV", "SANDBOX")

    # Dynamiczne URL w zależności od środowiska
    if EBAY_ENV == "SANDBOX":
        EBAY_API_URL = "https://api.sandbox.ebay.com"
    else:
        EBAY_API_URL = "https://api.ebay.com"

settings = Config()