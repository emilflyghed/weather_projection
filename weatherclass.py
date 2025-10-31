import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout


class WeatherReport:
    """Fetches live weather data and stores the latest response to data.json."""

    url = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self,city: str, *, units: str = "metric", data_file: str = "data.json") -> None:
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise RuntimeError("Missing API_KEY in environment or .env file.")

        self.city = city
        self.units = units
        self.data_path = Path(data_file)

    def fetch_and_store(self, *, city: Optional[str] = None) -> Dict[str, Any]:
        query_city = city or self.city
        params = {"q": query_city, "appid": self.api_key, "units": self.units}

        try:
            response = requests.get(self.url, params=params, timeout=10)
            response.raise_for_status()

        except Timeout:
            raise TimeoutError("Weather API request timed out")

        except ConnectionError:
            raise ConnectionError("Network connection error — check your internet")

        except HTTPError as http_err:
            # Return specific OpenWeather errors if possible
            try:
                details = response.json().get("message", "Unknown API error")
            except Exception:
                details = str(http_err)
            raise ValueError(f"API returned error: {details}")

        except RequestException:
            raise RuntimeError("Unexpected error during API request")

        # Parse JSON safely
        try:
            weather_payload = response.json()
        except json.JSONDecodeError:
            raise ValueError("Received invalid JSON from weather API")

        record = {
            "city": query_city,
            "units": self.units,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "data": weather_payload,
        }

        # Store to file — also wrapped
        try:
            self._write_data(record)
        except OSError:
            raise OSError("Could not write data to JSON file")
        except TypeError:
            raise TypeError("Invalid data format when writing JSON")

        return record

    def _write_data(self, record: Dict[str, Any]) -> None:
        """Write single latest weather record to JSON"""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        with self.data_path.open("w", encoding="utf-8") as file_handle:
            json.dump(record, file_handle, indent=2)
