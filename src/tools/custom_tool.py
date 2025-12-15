import os
from pathlib import Path
# 1. Ustawiamy fałszywy klucz, żeby Pydantic nie krzyczał przy starcie.
# To musi być PRZED inicjalizacją JSONSearchTool.
os.environ["OPENAI_API_KEY"] = "NA"

from crewai_tools import JSONSearchTool

# Ustalanie ścieżki:
# 1. Pobieramy ścieżkę do TEGO pliku (src/tools/openapi_tool.py)
current_file = Path(__file__).resolve()
# 2. Wychodzimy dwa poziomy w górę do katalogu 'src'
src_dir = current_file.parent.parent
# 3. Wchodzimy do 'data' i wskazujemy plik
json_path = src_dir / 'data' / 'ebay_openapi.json'

# Debug: Wypisz ścieżkę, żebyś widział gdzie szuka
print(f"DEBUG: Szukam pliku JSON tutaj: {json_path}")

if not json_path.exists():
    # Fallback: sprawdź czy nie ma wersji lite
    json_path = src_dir / 'data' / 'ebay_browse_lite.json'
    if not json_path.exists():
        raise FileNotFoundError(f"CRITICAL: Nie znaleziono pliku JSON w: {json_path}")

# 3. Inicjalizacja narzędzia
json_tool = JSONSearchTool(
    json_path=json_path,
    config={
        "llm": {
            "provider": "ollama",
            "config": {
                "model": "qwen2.5-coder:14b",
            },
        },
        "embedder": {
            "provider": "huggingface",
            "config": {
                "model": "sentence-transformers/all-MiniLM-L6-v2",
            },
        },
    }
)