import json
import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Any
from dotenv import load_dotenv

load_dotenv()

# Pobieramy domyślną wartość z .env (np. 98.0)
DEFAULT_MIN_PERCENTAGE = float(os.getenv("MIN_SELLER_FEEDBACK", 95.0))

class ReputationFilterInput(BaseModel):
    items: Any = Field(..., description="List of items from eBay search")
    # Zmieniamy nazwę argumentu na bardziej precyzyjną
    min_percentage: float = Field(DEFAULT_MIN_PERCENTAGE, description="Minimum feedback percentage (e.g. 98.0)")

class ReputationFilterTool(BaseTool):
    name: str = "reputation_filter"
    description: str = "Filters items by seller feedback PERCENTAGE."
    args_schema: type[BaseModel] = ReputationFilterInput

    def _run(self, items: Any, min_percentage: float = DEFAULT_MIN_PERCENTAGE) -> str:
        if isinstance(items, str):
            try:
                items = json.loads(items)
            except json.JSONDecodeError:
                return "Error: Invalid JSON."
        
        if not isinstance(items, list):
             return "Error: Items must be a list."

        print(f"🔧 FILTER: Odrzucam sprzedawców poniżej {min_percentage}% pozytywów...")

        filtered = []
        for item in items:
            try:
                seller_data = item.get("seller", {})
                
                # Pobieramy PROCENTY (API zwraca to jako string np. "99.8")
                percent_str = seller_data.get("feedbackPercentage", "0.0")
                
                # Konwersja na float
                try:
                    percentage = float(percent_str)
                except ValueError:
                    percentage = 0.0

                # Logika filtrowania po PROCENTACH
                if percentage >= min_percentage:
                    # Spłaszczamy obiekt - zostawiamy tylko to co ważne
                    flat_item = {
                        "title": item.get("title"),
                        "price": item.get("price"),
                        "currency": item.get("currency"),
                        "url": item.get("url"),
                        "condition": item.get("condition"),
                        # Zapisujemy jako float, żeby Pydantic miał łatwiej
                        "seller_percentage": percentage 
                    }
                    filtered.append(flat_item)
            except Exception as e:
                continue

        print(f"✅ FILTER: Zostało {len(filtered)} ofert (z {len(items)}).")
        return json.dumps(filtered)