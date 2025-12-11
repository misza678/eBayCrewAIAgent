from crewai_tools import JSONSearchTool

# Ścieżka do Twojego pliku OpenAPI
# Upewnij się, że plik jest w katalogu projektu
json_tool = JSONSearchTool(
    json_path='./ebay_openapi.json',
    config={
        "llm": {
            "provider": "ollama",  # Ważne dla lokalnego modelu
            "config": {
                "model": "llama3:latest", # Twój model
            },
        },
        "embedder": {
            "provider": "huggingface", # Lokalny embedder (nie wymaga OpenAI)
            "config": {
                "model": "sentence-transformers/all-MiniLM-L6-v2",
            },
        },
    }
)