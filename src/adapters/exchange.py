# Python imports
import pandas as pd
from binance.client import Client
from decimal import Decimal

class Exchange:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        api_url: str,
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_url = api_url

    def get_client(self) -> Client:
        """Return a Binance client instance"""
        client=  Client(
            api_key=self.api_key,
            api_secret=self.api_secret,
            testnet=True,
            requests_params={'timeout': 20},
        )
        client.API_URL = self.api_url
        self.client = client
        return client

    def get_historical_data(self, symbol: str, interval: str = '1h', lookback: int = 100) -> pd.DataFrame:
        """Fetch historical klines (time series) and return DataFrame"""
        columns = [
            'timestamp',
            'open',
            'high',
            'low',
            'close',
            'volume',
            'close_time',
            'quote_asset_volume',
            'number_of_trades',
            'taker_buy_base',
            'taker_buy_quote',
            'ignore',
        ]
        klines = self.client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=lookback,
        )
        df = pd.DataFrame(klines, columns=columns)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        return df

    def create_order(self, symbol: str, side: str, quantity: float):
        """Create a test order"""
        self.client.create_test_order(
            symbol=symbol,
            side=side,
            type=Client.ORDER_TYPE_MARKET,
            quantity=Decimal(quantity).quantize(Decimal('0.01'), rounding='ROUND_DOWN'),
        )

    def get_balance(self, asset: str) -> float:
        balance = self.client.get_asset_balance(
            asset=asset,
        )
        return float(balance['free']) if balance else 0.0

    def get_symbol_ticker(self, symbol: str) -> float:
        """Get the current price of a specific asset"""
        price = self.client.get_symbol_ticker(symbol=symbol)
        price = price.get('price')
        if not price:
            raise ValueError(f"Price not found for {symbol}")
        return float(price) if price else 0.0
