# Python imports
from typing import List
from attr import dataclass
from typing import Optional


SELL_DIRECTION = 'sell'
BUY_DIRECTION = 'buy'
MARKET_ORDER = 'market'
LIMIT_ORDER = 'limit'
STOP_ORDER = 'stop'

@dataclass
class AssetAnalysis:
    asset: str
    symbol: str
    price: float
    rsi: float
    ema: float
    lower_bb: float
    upper_bb: float
    mavg_bb: float
    trade_signal: Optional[str] = None
    trend_signal: Optional[str] = None

    def as_dict(self):
        return {
            'asset': self.asset,
            'symbol': self.symbol,
            'price': self.price,
            'rsi': self.rsi,
            'ema': self.ema,
            'lower_bb': self.lower_bb,
            'upper_bb': self.upper_bb,
            'mavg_bb': self.mavg_bb,
            'trade_signal': self.trade_signal,
            'trend_signal': self.trend_signal,
        }

@dataclass
class MarketAnalysis:
    markets: List[AssetAnalysis]

    def as_list(self):
        return [market.as_dict() for market in self.markets]

