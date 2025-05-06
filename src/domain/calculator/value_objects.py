# Python imports
from dataclasses import dataclass
import pandas as pd

SELL_SIGNAL = 'sell'
BUY_SIGNAL = 'buy'
HOLD_SIGNAL = 'hold'

@dataclass
class ConservativeCalculatorIndicators:

    rsi: pd.Series
    ema: pd.Series

    def as_dict(self):
        return {
            'rsi': self.rsi,
            'ema': self.ema
        }

@dataclass
class BollingerBandsCalculatorIndicators:

    upper: pd.Series
    lower: pd.Series
    mavg: pd.Series

    def as_dict(self):
        return {
            'upper': self.upper,
            'lower': self.lower,
            'mavg': self.mavg
        }
