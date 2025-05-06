class AssetBalanceError(Exception):
    """Exception raised when an asset balance cannot be obtained."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class AssetPriceError(Exception):
    """Exception raised when an asset price cannot be obtained."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class HistoricalDataError(Exception):
    """Exception raised when historical data cannot be obtained."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class OrderPlacementError(Exception):
    """Exception raised when an order cannot be placed."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class TradingError(Exception):
    """General exception for trading errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
