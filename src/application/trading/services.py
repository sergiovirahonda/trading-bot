# Python imports
import pandas as pd
import uuid
from typing import Optional

# App imports
from src.domain.trading.entities import TradingOrder, TradingOrderFactory
from src.domain.trading.value_objects import (
    SELL_DIRECTION,
    MarketAnalysis,
    AssetAnalysis,
)
from src.domain.trading.services import TradingDomainServices
from src.application.calculator.services import IndicatorCalculatorApplicationServices

class TradingApplicationServices:

    def __init__(self,
        calculator_indicator_app_services: IndicatorCalculatorApplicationServices,
        trading_domain_services: TradingDomainServices,

    ):
        self.calculator_indicator_app_services = calculator_indicator_app_services
        self.trading_domain_services = trading_domain_services

    def analyze_market(
        self,
        symbol: str,
    ) -> AssetAnalysis:
        hd = self.trading_domain_services.get_historical_data(
            symbol=symbol,
            interval='5m',
            lookback=200,
        )
        trend_indicators = self.calculator_indicator_app_services.apply_trend_indicators(
            close_prices=hd['close'],
        )
        trend_signal = self.calculator_indicator_app_services.get_trend_signal(
            close_price=hd['close'].iloc[-1],
            indicators=trend_indicators,
        )
        latest_rsi = trend_indicators.rsi.iloc[-1]
        latest_ema = trend_indicators.ema.iloc[-1]
        bb_indicators = self.calculator_indicator_app_services.apply_bollinger_bands_indicators(
            close_prices=hd['close'],
        )
        latest_bb_lower = bb_indicators.lower.iloc[-1]
        latest_bb_upper = bb_indicators.upper.iloc[-1]
        latest_bb_mavg = bb_indicators.mavg.iloc[-1]
        trade_signal = self.calculator_indicator_app_services.get_bollinger_bands_signals(
            close_price=hd['close'].iloc[-1],
            indicators=bb_indicators,
        )
        asset_analysis = AssetAnalysis(
            asset=symbol[:-4],
            symbol=symbol,
            price=float(hd['close'].iloc[-1]),
            rsi=float(latest_rsi),
            ema=float(latest_ema),
            trend_signal=trend_signal,
            lower_bb=float(latest_bb_lower),
            upper_bb=float(latest_bb_upper),
            mavg_bb=float(latest_bb_mavg),
            trade_signal=trade_signal,
        )
        return asset_analysis

    def analyze_markets(
        self,
        watchlist: list,
    ) -> MarketAnalysis:
        results = []
    
        for symbol in watchlist:
            try:
                asset_analysis = self.analyze_market(symbol)
                results.append(asset_analysis)
            except Exception as e:
                print(f"Error analyzing market {symbol}: {e}")
        return MarketAnalysis(markets=results)

    def get_asset_balance(self, asset: str) -> float:
        """Get the balance of a specific asset"""
        return self.trading_domain_services.get_asset_balance(asset)

    def get_historical_data(self, symbol: str, interval: str = '1h', lookback: int = 100) -> pd.DataFrame:
        return self.trading_domain_services.get_historical_data(
            symbol=symbol,
            interval=interval,
            lookback=lookback,
        )
    
    async def place_order(
        self,
        order: TradingOrder,
    ) -> TradingOrder:
        """Place an order on the exchange"""
        await self.trading_domain_services.place_order(order)
        return order

    def get_current_asset(self) -> Optional[dict]:
        trading_state = self.trading_domain_services.get_trading_state()

        if trading_state:
            return trading_state

    def set_current_asset(self, asset: str, entry_price: Optional[float] = None):
        self.trading_domain_services.set_trading_state(asset, entry_price=entry_price)

    def wipe_current_asset(self):
        self.trading_domain_services.wipe_trading_state()

    def get_asset_price(self, asset: str) -> float:
        """Get the current price of a specific asset"""
        return self.trading_domain_services.get_asset_price(asset)

    def get_current_asset_holding_value(self) -> float:
        current_asset = self.get_current_asset()
        asset = current_asset.get("current_asset")
        return self.trading_domain_services.get_holding_price(asset)

    def get_asset_balance(self, asset: str) -> float:
        """Get the balance of a specific asset"""
        return self.trading_domain_services.get_asset_balance(asset)

    def get_equivalent_volume(
        self,
        origin_asset: str,
        target_asset: str,
    ) -> float:
        current_asset_holding_price = self.trading_domain_services.get_holding_price(f"{origin_asset}")
        target_asset_price = self.trading_domain_services.get_asset_price(f"{target_asset}")
        equivalent_volume = current_asset_holding_price / target_asset_price
        return equivalent_volume

    async def stop_loss(
        self,
    ) -> TradingOrder:
        """Implement stop loss strategy"""
        current_asset = self.get_current_asset()
        if current_asset == "USDT":
            raise ValueError("Stop loss cannot be applied to USDT.")
        current_holding_value = self.get_current_asset_holding_value()
        current_balance = self.get_asset_balance(current_asset.get("current_asset"))
        entry_price = current_asset.get("entry_price")
        order = TradingOrderFactory.create_order(
            symbol=f"{current_asset}USDT",
            side=SELL_DIRECTION,
            quantity=current_holding_value,
            usd_amount=current_holding_value,
            profit=current_holding_value - (entry_price * current_balance),
        )
        # Place the order
        await self.place_order(order)
        return order
