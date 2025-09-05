from decimal import Decimal
import httpx
import logging
import datetime
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)


class CurrencyService:
    def __init__(self, cache_duration_minutes: int = 30):
        self.cache_duration = cache_duration_minutes * 60
        self.chached_rate: Optional[float] = None
        self.cache_time: Optional[datetime.datetime] = None
        self.cache_lock = asyncio.Lock()

    def _is_cache_valid(self) -> bool:
        if self.chached_rate is None or self.cache_time is None:
            return False
        return datetime.datetime.now() - self.cache_time < datetime.timedelta(
            seconds=self.cache_duration
        )

    async def get_usd_rate(self) -> Decimal:
        now = datetime.datetime.now()
        async with self.cache_lock:
            try:
                if self._is_cache_valid():
                    return self.chached_rate  # type: ignore

                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        "https://www.cbr-xml-daily.ru/daily_json.js"
                    )
                    response.raise_for_status()
                    data = response.json()
                self.chached_rate = Decimal(data["Valute"]["USD"]["Value"])  # type: ignore
                self.cache_time = now
                return self.chached_rate  # type: ignore
            except Exception as e:
                logger.error(f"Error getting USD rate: {e}")
                raise


currency_service = CurrencyService()
