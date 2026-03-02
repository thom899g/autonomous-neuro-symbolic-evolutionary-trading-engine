"""
Data ingestion module with robust error handling and multiple data sources.
Implements retry logic, rate limiting, and data validation.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
import ccxt
import yfinance as yf
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    """Structured market data container with validation"""
    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Validate data on initialization"""
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if any(val <= 0 for val in [self.open, self.high, self.low, self.close, self.volume]):
            raise ValueError("Price and volume must be positive")
        if self.high < self.low:
            raise ValueError("High cannot be less than low")
        if self.metadata is None:
            self.metadata = {}

class DataSource(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', 
                         limit: int = 100) -> List[MarketData]:
        """Fetch OHLCV data"""
        pass
    
    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """Validate symbol format for this source"""
        pass