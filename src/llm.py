import windows_fix # <--- DODAJ TO NA SAMEJ GÓRZE
from crewai import Agent, LLM

# --- 1. KONFIGURACJA MÓZGU (SINGLETON) ---
# To jest kluczowe dla wydajności na laptopie.
# Łączymy się z Ollamą działającą w tle.
local_llm = LLM(
    model="ollama/qwen2.5-coder:14b", # Upewnij się, że masz ten model pobrany
    base_url="http://localhost:11434",
    temperature=0.2 # Niski, żeby nie zmyślał cen
)
