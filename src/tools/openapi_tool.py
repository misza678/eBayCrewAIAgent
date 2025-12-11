import os
from crewai_tools import JSONSearchTool

# Ustalanie ścieżki do pliku JSON (żeby działało niezależnie od tego skąd odpalasz skrypt)
# Zakładam, że ebay_openapi.json leży w głównym katalogu projektu
base_dir = os.path.dirname(os.path.abspath(__file__)) # katalog tools/
project_root = os.path.dirname(os.path.dirname(os.path.dirname(base_dir))) # 3 poziomy w górę do roota
json_path = os.path.join(project_root, 'ebay_openapi.json')

# Konfiguracja narzędzia pod lokalny model (Ollama)
json_tool = JSONSearchTool(
    json_path=json_path,
    config={
        "llm": {
            "provider": "ollama",
            "config": {
                "model": "qwen2.5-coder:14b", # Twój model z llm.py
            },
        },
        "embedder": {
            "provider": "huggingface", # Używamy lokalnego embeddera
            "config": {
                "model": "sentence-transformers/all-MiniLM-L6-v2",
            },
        },
    }
)