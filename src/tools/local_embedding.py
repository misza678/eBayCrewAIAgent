# src/tools/local_embedding.py

class OllamaEmbedding:
    """
    Wrapper dla lokalnych embeddingów (Ollama).
    Zwraca embedding w formacie listy floatów dla tekstu.
    """

    def __init__(self, model_name="ollama/embedding-model"):
        self.model_name = model_name
        # tutaj możesz zainicjalizować klienta Ollama, jeśli jest API lokalne

    def __call__(self, input):
        # na razie przykład zwracający losowe embeddingi (dummy)
        # później podłącz rzeczywisty lokalny model Ollama
        if isinstance(input, str):
            input = [input]
        return [[0.0] * 768 for _ in input]  # przykładowy embedding 768-d
