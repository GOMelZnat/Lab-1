
import requests


API_URL = "https://echoes.soferity.com/api/quotes/random"


def get_external_quote():
    """Получает случайную цитату на русском языке из Echoes."""

    try:
        response = requests.get(
            API_URL,
            params={"lang": "ru"},
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()

        text = data.get("quote", "").strip()
        author = data.get("author", "").strip()

        if not text:
            return None

        return {
            "text": text,
            "author": author or "Автор неизвестен",
            "category": "внешний источник",
            "source": "Echoes",
            "source_url": "https://echoes.soferity.com/",
        }

    except (requests.RequestException, ValueError):
        return None
