# Python imports
import pandas as pd
from binance.exceptions import BinanceAPIException
from typing import Optional
import math

# App imports
from src.adapters.exchange import Exchange
from src.adapters.redis import RedisAdapter
from src.adapters.telegram import TelegramAdapter
from src.conf.settings import (
    REDIS_BOT_TRADES_KEY,
    REDIS_BOT_STATE_KEY,
    INITIAL_ASSET,
)

# Local imports
from .exceptions import (
    AssetBalanceError,
    OrderPlacementError,
    HistoricalDataError,
    TradingError,
    AssetPriceError,
)
from .entities import TradingOrder

class TradingDomainServices:
    def __init__(
        self,
        exchange_client: Exchange,
        redis_client: RedisAdapter,
        telegram_adapter: TelegramAdapter,
    ):
        self.exchange_client = exchange_client
        self.redis_client = redis_client
        self.telegram_adapter = telegram_adapter

    def get_asset_balance(self, asset: str) -> float:
        """Get the balance of a specific asset"""
        try:
            balance = self.exchange_client.get_balance(asset=asset)
            return balance
        except BinanceAPIException as e:
            raise AssetBalanceError(f"Error fetching balance for {asset}: {e.message}")
        except Exception as e:
            raise TradingError(f"Unexpected error fetching balance for {asset}: {e}")

    def get_asset_price(self, asset: str) -> float:
        """Get the current price of a specific asset"""
        try:
            price = self.exchange_client.get_symbol_ticker(symbol=f"{asset}USDT")
            if not price:
                raise AssetPriceError(f"Price not found for {asset}")
            return float(price)
        except BinanceAPIException as e:
            raise AssetPriceError(f"Error fetching price for {asset}: {e.message}")
        except Exception as e:
            raise TradingError(f"Unexpected error fetching price for {asset}: {e}")

    def get_holding_price(self, asset: str) -> float:
        balance = self.get_asset_balance(asset)
        if balance > 0:
            holding_price = self.get_asset_price(asset) * balance
            return holding_price
        else:
            raise AssetBalanceError(f"No balance for {asset}")

    def get_historical_data(self, symbol: str, interval: str = '1h', lookback: int = 100) -> pd.DataFrame:
        try:
            return self.exchange_client.get_historical_data(
                symbol=symbol,
                interval=interval,
                lookback=lookback,
            )
        except BinanceAPIException as e:
            raise HistoricalDataError(f"Error fetching historical data for {symbol}: {e.message}")
        except Exception as e:
            raise TradingError(f"Unexpected error fetching historical data for {symbol}: {e}")

    async def place_order(
        self,
        order: TradingOrder
    ):
        """Place an order on the exchange"""
        quantity = round(order.quantity, 4)
        try:
            self.exchange_client.create_order(
                symbol=order.symbol,
                side=order.side,
                quantity=quantity,
            )
        except BinanceAPIException as e:
            raise OrderPlacementError(f"Error placing order for {order.symbol}: {e.message}")
        except Exception as e:
            raise TradingError(f"Unexpected error placing order for {order.symbol}: {e}")
        self.redis_client.push_record(
            REDIS_BOT_TRADES_KEY,
            order.as_dict(),
        )
        if "USDT" in order.symbol:
            await self.telegram_adapter.send_message(
                "Placing stop loss order...",
            )
        message = f"❗ Order placed: \n" +\
                    f"Symbol: {order.symbol}\n" +\
                    f"Side: {order.side}\n" +\
                    f"Quantity: {quantity}\n" +\
                    f"Price: {order.price}\n" +\
                    f"USD Amount: {order.usd_amount}\n" + \
                    f"Profit: {order.profit}\n"
        await self.telegram_adapter.send_message(message)

    def set_trading_state(self, asset: str, entry_price: Optional[float] = 0.0):
        """Set the current trading state"""
        trading_state = {
            "current_asset": asset,
            "entry_price": entry_price,
        }
        self.redis_client.set_state(REDIS_BOT_STATE_KEY, trading_state)

    def get_trading_state(self) -> dict:
        """Get the current trading state"""
        state = self.redis_client.get_state(REDIS_BOT_STATE_KEY)
        if not state:
            self.set_trading_state(INITIAL_ASSET)
            state = self.redis_client.get_state(REDIS_BOT_STATE_KEY)
        return state

    def wipe_trading_state(self):
        """Wipe the current trading state"""
        self.redis_client.clear_state(REDIS_BOT_STATE_KEY)