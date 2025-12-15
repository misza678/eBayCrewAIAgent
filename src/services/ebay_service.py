import requests
import base64
import logging
import json
import os
from dotenv import load_dotenv

# --- 1. POPRAWIONY IMPORT MODELI ---
from src.models.schemas import SearchCriteria

# Ładujemy zmienne z pliku .env
load_dotenv()

# Konfiguracja loggera (żebyś widział co się dzieje w konsoli)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EbayService:
    def __init__(self):
        self.token = None
        # Pobieramy konfigurację bezpośrednio z .env
        self.base_url = os.getenv("EBAY_API_URL", "https://api.ebay.com").rstrip("/")
        self.app_id = os.getenv("EBAY_APP_ID")
        self.cert_id = os.getenv("EBAY_CERT_ID")
        self.env = os.getenv("EBAY_ENV", "PROD")
        
        self.target_country = "DE" 
        self.currency = "EUR"

        # Sprawdzenie czy klucze są ustawione
        if not self.app_id or not self.cert_id:
            logger.warning("⚠️ Brak kluczy EBAY_APP_ID lub EBAY_CERT_ID w pliku .env!")

    def _get_access_token(self):
        logger.info("🔑 Pobieranie tokenu dostępu eBay...")
        auth_url = f"{self.base_url}/identity/v1/oauth2/token"
        credentials = f"{self.app_id}:{self.cert_id}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}

        try:
            response = requests.post(auth_url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            self.token = response.json()["access_token"]
            logger.info("✅ Token pobrany pomyślnie.")
            return self.token
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Błąd autoryzacji: {e}")
            if response:
                logger.error(f"Treść błędu: {response.text}")
            raise e

    def search_items(self, criteria: SearchCriteria):
        """
        Pobiera oferty na podstawie kryteriów.
        """
        if not self.token:
            self._get_access_token()

        endpoint = f"{self.base_url}/buy/browse/v1/item_summary/search"
        
        # 1. Budowanie filtrów API
        filters = []
        
        # Cena
        if criteria.max_price:
            filters.append(f"price:[..{criteria.max_price}]")
            
        # Stan
        condition_map = {
            "New": "NEW",
            "Used": "USED",
            "ForParts": "FOR_PARTS_OR_NOT_WORKING"
        }
        cond_code = condition_map.get(criteria.condition, "FOR_PARTS_OR_NOT_WORKING") 
        filters.append(f"condition:{{{cond_code}}}")
        
        # Typ oferty
        if criteria.listing_type == "FixedPrice":
            filters.append("buyingOptions:{FIXED_PRICE}")
        elif criteria.listing_type == "Auction":
            filters.append("buyingOptions:{AUCTION}")

        # Kraj dostawy (Tylko na PROD)
        if self.env == "PROD":
             filters.append(f"deliveryCountry:{self.target_country}")

        params = {
            "q": criteria.query,
            "filter": ",".join(filters),
            "limit": 50, 
            "sort": "price"
        }

        logger.info(f"🔍 Szukam: {criteria.query} | Filtry: {params['filter']}")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_DE" if self.target_country == "DE" else "EBAY_US"
        }

        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=10)

            # Debugowanie
            # print(f"\n🔵 [DEBUG] URL: {response.url}")

            response.raise_for_status()
            data = response.json()
            
            # print("\n📦 [DEBUG] SUROWY JSON Z EBAY (fragment):")
            # print(str(data)[:500] + "...") 

            items = []
            if "itemSummaries" in data:
                for item in data["itemSummaries"]:
                    # Wyciąganie kosztu wysyłki
                    shipping_cost = 0.0
                    try:
                        shipping_opts = item.get("shippingOptions", [])
                        if shipping_opts:
                            shipping_cost = float(shipping_opts[0].get("shippingCost", {}).get("value", 0))
                    except:
                        pass

                    # Wyciąganie feedbacku
                    seller_feedback = 0.0
                    try:
                        seller_feedback = float(item.get("seller", {}).get("feedbackPercentage", 0))
                    except:
                        pass

                    # Budowanie obiektu
                    items.append({
                        "title": item.get("title"),
                        "price": float(item.get("price", {}).get("value", 0)),
                        "currency": item.get("price", {}).get("currency"),
                        "shipping_cost": shipping_cost,
                        "total_price": float(item.get("price", {}).get("value", 0)) + shipping_cost,
                        "seller_feedback": seller_feedback,
                        "condition": item.get("condition"),
                        "url": item.get("itemWebUrl")
                    })
            
            logger.info(f"✅ Znaleziono {len(items)} ofert.")
            return items

        except Exception as e:
            logger.error(f"❌ Błąd API: {e}")
            return []