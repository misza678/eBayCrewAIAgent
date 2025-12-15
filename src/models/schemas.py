from pydantic import BaseModel, Field
from typing import List, Optional

# --- 1. MODELE DO WYSZUKIWANIA (Dla EbayService i Toola) ---

class SearchCriteria(BaseModel):
    """Kryteria wyszukiwania przekazywane do serwisu eBay."""
    query: str = Field(..., description="Słowo kluczowe, np. 'Makita DHP453'")
    min_price: Optional[float] = Field(default=None, description="Cena minimalna")
    max_price: Optional[float] = Field(default=None, description="Cena maksymalna")
    condition: str = Field(default="ForParts", description="Stan: 'New', 'Used', 'ForParts'")
    sort_order: str = Field(default="price", description="Sortowanie: 'price', 'newlyListed'")
    listing_type: str = Field(default="FixedPrice", description="Typ: 'FixedPrice' lub 'Auction'")

# (Opcjonalnie, jeśli stary kod tego używa, zostawiamy)
class EbayApiRequest(BaseModel):
    endpoint: str
    params: dict
    explanation: str

# --- 2. MODELE DO ANALIZY (Dla Agenta Analityka) ---

class DealVerdict(BaseModel):
    """Ocena pojedynczej oferty."""
    item_title: str = Field(default="Nieznany przedmiot", description="Tytuł przedmiotu")
    price: float = Field(default=0.0, description="Cena")
    is_bundle: bool = Field(default=False, description="Czy to zestaw?")
    price_per_unit: float = Field(default=0.0, description="Cena za sztukę")
    is_good_deal: bool = Field(default=False, description="Czy warto kupić?")
    reasoning: str = Field(default="Brak uzasadnienia", description="Krótkie podsumowanie")
    
    # Pola szczegółowe
    decision_basis: str = Field(default="Brak danych", description="Szczegóły decyzji")
    math_breakdown: str = Field(default="-", description="Wyliczenia")

class Item(BaseModel):
    title: str
    price: str
    currency: str
    url: str
    condition: str
    # Tylko jedno pole dot. reputacji - procenty jako float
    seller_percentage: float 

class SourcingResult(BaseModel):
    items: List[Item]
    total_items: int

class DealList(BaseModel):
    """Lista ocenionych ofert."""
    deals: List[DealVerdict] = Field(default_factory=list)