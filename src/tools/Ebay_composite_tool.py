import os
import requests
import json
import base64
import logging
from crewai.tools import BaseTool
from pathlib import Path
from dotenv import load_dotenv

# Konfiguracja ścieżek i loggera
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Domyślny próg z .env
DEFAULT_MIN_PERCENTAGE = float(os.getenv("MIN_SELLER_FEEDBACK", 98.0))

class EbayCompositeTool(BaseTool):
    name: str = "search_and_filter_ebay"
    description: str = (
        "Searches eBay AND automatically filters out bad sellers. "
        "Input must be a JSON with a 'query' key (string). "
        "Example: {'query': 'Makita DHR243', 'min_percentage': 95.0}"
    )

    def _get_access_token(self) -> str:
        """
        Generuje świeży token OAuth2 (Client Credentials) używając App ID i Cert ID.
        """
        app_id = os.getenv("EBAY_APP_ID")
        cert_id = os.getenv("EBAY_CERT_ID")
        base_url = os.getenv("EBAY_API_URL", "https://api.ebay.com").rstrip("/")

        if not app_id or not cert_id:
            raise ValueError("❌ Brak EBAY_APP_ID lub EBAY_CERT_ID w pliku .env")

        auth_url = f"{base_url}/identity/v1/oauth2/token"
        credentials = f"{app_id}:{cert_id}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials", 
            "scope": "https://api.ebay.com/oauth/api_scope"
        }

        try:
            # logger.info("🔑 Generowanie nowego tokena eBay...")
            response = requests.post(auth_url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            token = response.json()["access_token"]
            return token
        except Exception as e:
            logger.error(f"❌ Błąd autoryzacji eBay: {e}")
            raise e

    def _run(self, query: str, min_percentage: float = DEFAULT_MIN_PERCENTAGE) -> str:
        # 1. Safety Check na input od LLM (gdyby wysłał słownik)
        if isinstance(query, dict):
            if "description" in query:
                query = query["description"]
            else:
                query = str(query)

        # 2. Pobranie świeżego tokena
        try:
            ebay_token = self._get_access_token()
        except Exception as e:
            return f"Error generating token: {str(e)}"

        # 3. Konfiguracja zapytania
        url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        headers = {
            "Authorization": f"Bearer {ebay_token}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_DE" # Zmień na EBAY_PL lub EBAY_US w razie potrzeby
        }
        
        # Proste parametry wyszukiwania
        params = {
            "q": query,
            "limit": "20",
            "sort": "price" # Sortujemy od najtańszych
        }

        try:
            print(f"🔍 COMPOSITE: Szukam '{query}' (Market: DE) i filtruję < {min_percentage}%...")
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                return f"eBay API Error: {response.status_code} - {response.text}"

            data = response.json()
            items = data.get("itemSummaries", [])
            
            if not items:
                return "No items found."

            # 4. Filtrowanie i Spłaszczanie (Flattening)
            filtered_items = []
            for item in items:
                try:
                    seller = item.get("seller", {})
                    percent_str = seller.get("feedbackPercentage", "0")
                    try:
                        percentage = float(percent_str)
                    except ValueError:
                        percentage = 0.0

                    # Warunek filtracji
                    if percentage >= min_percentage:
                        # Budujemy obiekt pasujący do Twojego modelu Pydantic (SourcingResult)
                        flat_item = {
                            "title": item.get("title"),
                            "price": item.get("price", {}).get("value"),
                            "currency": item.get("price", {}).get("currency"),
                            "url": item.get("itemWebUrl"),
                            "condition": item.get("condition"),
                            "seller_percentage": percentage
                        }
                        filtered_items.append(flat_item)
                except Exception:
                    continue

            print(f"✅ COMPOSITE: Znaleziono {len(items)}, po filtrze zostało {len(filtered_items)}.")
            
            # Zwracamy JSON string
            return json.dumps(filtered_items)

        except Exception as e:
            return f"Error during search: {str(e)}"