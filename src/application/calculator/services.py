# Python imports
import pandas as pd
from typing import Optional

# App imports
from src.domain.trading.value_objects import (
    AssetAnalysis,
    MarketAnalysis,
)
from src.domain.calculator.value_objects import (
    BollingerBandsCalculatorIndicators,
    ConservativeCalculatorIndicators,
)
from src.domain.calculator.services import IndicatorCalculatorDomainServices

class IndicatorCalculatorApplicationServices:
    def __init__(self, indicator_calculator_domain_services: IndicatorCalculatorDomainServices):
        self.icds = indicator_calculator_domain_services

    def evaluate_trading_decision(
        self,
        entry_price: float,
        close_prices: pd.Series,
        trend_indicators: ConservativeCalculatorIndicators,
        trade_indicators: BollingerBandsCalculatorIndicators,
    ) -> str:
        return self.icds.evaluate_trading_decision(
            entry_price=entry_price,
            close_prices=close_prices,
            trend_indicators=trend_indicators,
            trade_indicators=trade_indicators,
        )

    def apply_trend_indicators(
        self,
        close_prices: pd.Series,
    ) -> ConservativeCalculatorIndicators:
        return self.icds.apply_trend_indicators(close_prices)

    def apply_bollinger_bands_indicators(
        self,
        close_prices: pd.Series,
    ) -> BollingerBandsCalculatorIndicators:
        return self.icds.apply_bollinger_bands_indicators(close_prices)

    def get_trend_signal(self, close_price: float, indicators: ConservativeCalculatorIndicators) -> str:
        return self.icds.get_trend_signal(close_price, indicators)

    def get_bollinger_bands_signals(
        self,
        close_price: float,
        indicators: BollingerBandsCalculatorIndicators,
    ) -> str:
        return self.icds.get_bollinger_bands_signals(close_price, indicators)

    def assess_asset_market(
        self,
        asset_analysis: AssetAnalysis,
    ) -> str:
        return self.icds.assess_asset_market(asset_analysis)

    def get_best_market_opportunity(self, market_analysis: MarketAnalysis) -> Optional[AssetAnalysis]:
        return self.icds.get_best_market_opportunity(market_analysis)