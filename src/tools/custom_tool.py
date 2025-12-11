import os
# 1. Ustawiamy fałszywy klucz, żeby Pydantic nie krzyczał przy starcie.
# To musi być PRZED inicjalizacją JSONSearchTool.
os.environ["OPENAI_API_KEY"] = "NA"

from crewai_tools import JSONSearchTool

# 2. Ustalanie ścieżki do pliku w src/data/
# __file__ to ścieżka do tego pliku (src/tools/openapi_tool.py)
current_dir = os.path.dirname(os.path.abspath(__file__)) 
src_dir = os.path.dirname(current_dir) # wychodzimy do src/
json_path = os.path.join(src_dir, 'data', 'ebay_openapi.json') # wchodzimy do data/

# Sprawdzenie dla pewności (pomoże w debugowaniu)
if not os.path.exists(json_path):
    # Jeśli nie znajdzie, spróbujmy nazwy lite, jeśli taką stworzyłeś
    json_path_lite = os.path.join(src_dir, 'data', 'ebay_browse_lite.json')
    if os.path.exists(json_path_lite):
        json_path = json_path_lite
    else:
        raise FileNotFoundError(f"CRITICAL: Nie znaleziono pliku JSON. Szukano w: {json_path}")

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