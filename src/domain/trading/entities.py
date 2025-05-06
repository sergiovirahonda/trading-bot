# Python imports
from dataclasses import dataclass
from datetime import (
    datetime,
    timezone,
)
import uuid

@dataclass
class TradingOrder:
    """Class representing a trading order"""
    id: uuid.UUID
    timestamp: str
    symbol: str
    side: str
    quantity: float
    usd_amount: float
    profit: float

    def as_dict(self):
        return {
            'id': str(self.id),
            'timestamp': self.timestamp,
            'symbol': self.symbol,
            'side': self.side,
            'quantity': self.quantity,
            'usd_amount': self.usd_amount,
            'profit': self.profit,
        }


class TradingOrderFactory:
    """Factory class for creating trading orders"""
    @staticmethod
    def create_order(
        symbol: str,
        side: str,
        quantity: float,
        usd_amount: float,
        profit: float,
    ) -> TradingOrder:
        return TradingOrder(
            id=uuid.uuid4(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            symbol=symbol,
            side=side,
            quantity=quantity,
            usd_amount=usd_amount,
            profit=profit,
        )


