# src/tools/local_json_tool.py
import json
from pydantic import BaseModel
from crewai.tools import BaseTool

class LocalJSONTool(BaseTool):
    name: str = "Local JSON Search Tool"
    description: str = "Searches inside a local JSON file without using embeddings or external APIs."

    # Pydantic fields
    json_path: str
    data: dict = {}

    def __init__(self, **kwargs):
        # Pydantic wymaga, żeby wszystkie pola były przekazane przez __init__
        super().__init__(**kwargs)
        # Wczytujemy JSON
        self.data = self._load_json(self.json_path)

    def _load_json(self, path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Cannot load JSON: {e}"}

    def _search(self, obj, query: str, results: list):
        """Recursive search inside dict/list"""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if query.lower() in str(k).lower() or query.lower() in str(v).lower():
                    results.append({k: v})
                self._search(v, query, results)
        elif isinstance(obj, list):
            for item in obj:
                self._search(item, query, results)

    def _run(self, query: str) -> str:
        """Method required by BaseTool"""
        results: list = []
        self._search(self.data, query, results)
        if not results:
            return "No results found."
        return json.dumps(results[:10], indent=2, ensure_ascii=False)
