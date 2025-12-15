import sys
import os

# --- FIX ŚCIEŻEK (Zostawiamy to dla pewności) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.append(project_root)
# -----------------------------------------------

from typing import Type, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict

# --- POPRAWIONE IMPORTY ---
# Usunęliśmy ".ebay_sniper" ze ścieżki, bo Twoje foldery są bezpośrednio w src
from src.services.ebay_service import EbayService
from src.models.schemas import SearchCriteria
# --- 1. INPUT SCHEMA ---
class EbaySearchInput(BaseModel):
    """Parametry wejściowe dla narzędzia wyszukiwania eBay."""
    query: str = Field(..., description="Słowo kluczowe wyszukiwania, np. 'Makita DHP453 damaged'.")
    max_price: Optional[float] = Field(None, description="Maksymalna cena w walucie lokalnej.")
    condition: str = Field("ForParts", description="Stan: 'ForParts' (domyślne), 'Used', 'New'.")
    origin_country: str = Field("DE", description="Kod kraju (ISO), np. 'DE'.")
    listing_type: str = Field("FixedPrice", description="Typ: 'FixedPrice' lub 'Auction'.")
    min_seller_feedback: float = Field(90.0, description="Minimalny % pozytywnych opinii (0-100).")

# --- 2. KLASA NARZĘDZIA ---
class EbaySearchTool(BaseTool):
    name: str = "Search eBay Offers"
    description: str = (
        "Zaawansowana wyszukiwarka ofert na eBay. "
        "Pozwala filtrować po cenie, stanie, kraju i reputacji sprzedawcy. "
        "Zwraca listę ofert do dalszej analizy."
    )
    args_schema: Type[BaseModel] = EbaySearchInput
    
    # Konfiguracja Pydantic
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Wstrzykujemy serwis
    ebay_service: EbayService = Field(default_factory=EbayService)

    def _run(self, query: str, max_price: float = None, condition: str = "ForParts", 
             origin_country: str = "DE", listing_type: str = "FixedPrice", 
             min_seller_feedback: float = 90.0):
        
        # KROK A: Tłumaczenie parametrów
        criteria = SearchCriteria(
            query=query,
            max_price=max_price,
            condition=condition,
            sort_order="price",
            listing_type=listing_type
        )
        
        # Ustawienie kraju w serwisie
        self.ebay_service.target_country = origin_country
        
        # KROK B: Pobranie danych
        try:
            raw_results = self.ebay_service.search_items(criteria)
        except Exception as e:
            return f"Błąd podczas łączenia z eBay API: {str(e)}"
        
        if not raw_results:
            return f"Nie znaleziono ofert dla '{query}' w kraju {origin_country}."


        # KROK D: Formatowanie wyniku
        if not raw_results:
            return f"Znaleziono {len(raw_results)} ofert, ale żadna nie ma feedbacku > {min_seller_feedback}%."

        output_text = f"Znaleziono {len(raw_results)} ofert (Kraj: {origin_country}, Stan: {condition}):\n"
        
        # Ograniczamy do 10, żeby nie zapchać kontekstu LLM
        for item in raw_results:
            price = item.get('total_price', item.get('price'))
            title = item.get('title')
            link = item.get('url')
            feedback = item.get('seller_feedback', 'N/A')
            output_text += f"- {title} | Cena: {price} {self.ebay_service.currency} | Feedback: {feedback}% | Link: {link}\n"
            
        return output_text