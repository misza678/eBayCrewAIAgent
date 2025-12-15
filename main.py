import sys
import os
from dotenv import load_dotenv
load_dotenv()
# 1. Fix dla Windowsa (jeśli go używasz, zostaw)
try:
    import windows_fix
except ImportError:
    pass # Ignoruj jeśli pliku nie ma, ale lepiej go mieć

# 2. Dodanie ścieżki src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.crew import EbaySniperCrew

def run():
    print("🚀 Uruchamiam CrewAI (Nowa Struktura)...")
    print("Wpisz jaki przedmiot chcesz znaleźć na eBay (np. 'znajdź mi laptopa do 300 euro'):\n")
    
    # Pobranie danych od użytkownika
    user_input = input("👉 Twoje zapytanie: ")
    
    inputs = {
        'search_query': user_input 
    }
    
    # Uruchomienie
    result = EbaySniperCrew().crew().kickoff(inputs=inputs)
    
    print("\n\n########################")
    print("## WYNIK KOŃCOWY ##")
    print("########################\n")
    print(result)

if __name__ == "__main__":
    run()