# Python imports
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from ta.volatility import BollingerBands
from typing import Optional

# App imports
from src.domain.trading.value_objects import (
    AssetAnalysis,
    MarketAnalysis,
)

# App imports
from .value_objects import (
    BollingerBandsCalculatorIndicators,
    ConservativeCalculatorIndicators,
    SELL_SIGNAL,
    BUY_SIGNAL,
    HOLD_SIGNAL,
)

class IndicatorCalculatorDomainServices:

    def __init__(self):
        pass

    def evaluate_trading_decision(
        self,
        entry_price: float,
        close_prices: pd.Series,
        trend_indicators: ConservativeCalculatorIndicators,
        trade_indicators: BollingerBandsCalculatorIndicators,
    ) -> str:
        trend_signal = self.get_trend_signal(
            close_price=close_prices.iloc[-1],
            indicators=trend_indicators,
        )
        trade_signal = self.get_bollinger_bands_signals(
            close_price=close_prices.iloc[-1],
            indicators=trade_indicators,
        )
        current_price = close_prices.iloc[-1]
        change  = ((current_price - entry_price) / entry_price) * 100
        # If entry price is 2% lower than the current price, take profit
        if change > 2:
            return SELL_SIGNAL
        # If entry price is 1% higher than the current price, evaluate stop loss
        elif change < -1:
            # if trend signal is sell and trade signal is sell, stop loss
            if trend_signal == SELL_SIGNAL and trade_signal == SELL_SIGNAL:
                return SELL_SIGNAL
            # if trend signal is buy and trade signal is buy, hold
            elif trend_signal == BUY_SIGNAL and trade_signal == BUY_SIGNAL:
                return HOLD_SIGNAL
            # if trend signal is hold and trade signal is hold, stop loss
            elif trend_signal == HOLD_SIGNAL and trade_signal == HOLD_SIGNAL:
                return SELL_SIGNAL
            else:
                return SELL_SIGNAL
        # If the price is within 2% of the entry price, evaluate holding
        elif -1 <= change < 2:
            # if trend signal is buy and trade signal is buy, hold
            if trend_signal == BUY_SIGNAL and trade_signal == BUY_SIGNAL:
                return HOLD_SIGNAL
            # if trend signal is sell and trade signal is sell, take profit
            elif trend_signal == SELL_SIGNAL and trade_signal == SELL_SIGNAL:
                return SELL_SIGNAL
            # if trend signal is hold and trade signal is hold, hold
            elif trend_signal == HOLD_SIGNAL and trade_signal == HOLD_SIGNAL:
                return HOLD_SIGNAL
            else:
                return HOLD_SIGNAL

    def apply_trend_indicators(self, close_prices: pd.Series) -> ConservativeCalculatorIndicators:
        return ConservativeCalculatorIndicators(
            rsi=RSIIndicator(close=close_prices, window=14).rsi(),
            ema=EMAIndicator(close=close_prices, window=200).ema_indicator(),
        )

    def apply_bollinger_bands_indicators(self, close_prices: pd.Series) -> BollingerBandsCalculatorIndicators:
        bb = BollingerBands(close=close_prices, window=20, window_dev=1.5)
        indicators = BollingerBandsCalculatorIndicators(
            upper=bb.bollinger_hband(),
            lower=bb.bollinger_lband(),
            mavg=bb.bollinger_mavg(),
        )
        return indicators

    def get_trend_signal(
        self,
        close_price: float,
        indicators: ConservativeCalculatorIndicators,
    ) -> str:
        latest_rsi = indicators.rsi.iloc[-1]
        latest_ema = indicators.ema.iloc[-1]
        if latest_rsi < 40 and close_price > latest_ema:
            return BUY_SIGNAL
        elif latest_rsi > 60 and close_price < latest_ema:
            return SELL_SIGNAL
        else:
            return HOLD_SIGNAL

    def get_bollinger_bands_signals(
        self,
        close_price: float,
        indicators: BollingerBandsCalculatorIndicators,
    ) -> str:
        latest_upper = indicators.upper.iloc[-1]
        latest_lower = indicators.lower.iloc[-1]
        if close_price < latest_lower:
            return BUY_SIGNAL
        elif close_price > latest_upper:
            return SELL_SIGNAL
        else:
            return HOLD_SIGNAL

    def get_market_signals(
        self,
        market_analysis: MarketAnalysis,
    ) -> MarketAnalysis:
        for market in market_analysis.markets:
            trend_indicators = self.apply_trend_indicators(pd.Series(market.price))
            trend_signal = self.get_trend_signal(market.price, trend_indicators)
            market.trend_signal = trend_signal
            trade_indicators = self.apply_bollinger_bands_indicators(pd.Series(market.price))
            trade_signal = self.get_bollinger_bands_signals(market.price, trade_indicators)
            market.trade_signal = trade_signal
        return market_analysis

    def assess_asset_market(
        self,
        asset_analysis: AssetAnalysis,
    ) -> str:
        if asset_analysis.trade_signal == BUY_SIGNAL and asset_analysis.trend_signal in [BUY_SIGNAL, HOLD_SIGNAL]:
            return BUY_SIGNAL
        elif asset_analysis.trade_signal == SELL_SIGNAL and asset_analysis.trend_signal in [SELL_SIGNAL, HOLD_SIGNAL]:
            return SELL_SIGNAL
        else:
            return HOLD_SIGNAL
        

    def get_best_market_opportunity(
        self,
        market_analysis: MarketAnalysis,
    ) -> Optional[AssetAnalysis]:
        buy_markets = []
        for market in market_analysis.markets:
            if market.trade_signal in [BUY_SIGNAL, HOLD_SIGNAL] and market.trend_signal in [BUY_SIGNAL, HOLD_SIGNAL]:
                buy_markets.append(market)
        if buy_markets:
            best_market = min(
                buy_markets,
                key=lambda x: x.rsi,
            )
            return best_market

        