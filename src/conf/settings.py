# Python imports
import os

# Exchange settings
API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')
API_URL = os.environ.get('API_URL', 'https://testnet.binance.vision/api')

# Redis settings
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_DB = os.environ.get('REDIS_DB', 0)
REDIS_BOT_STATE_KEY = os.environ.get('REDIS_BOT_STATE_KEY', 'bot:state')
REDIS_BOT_TRADES_KEY = os.environ.get('REDIS_BOT_TRADES_KEY', 'bot:trades')

# App settings
ASSET_WATCHLIST = os.environ.get('ASSET_WATCHLIST', 'ETHUSDT,BTCUSDT,SOLUSDT,TAOUSDT').split(',')
INITIAL_ASSET = os.environ.get('INITIAL_ASSET', 'ETH')
INTERVAL = os.environ.get('INTERVAL', '5m')
LOOKBACK = os.environ.get('LOOKBACK', '100')
RSI_BUY_THRESHOLD = os.environ.get('RSI_BUY_THRESHOLD', 30)
RSI_SELL_THRESHOLD = os.environ.get('RSI_SELL_THRESHOLD', 70)
STOP_LOSS_PCT = os.environ.get('STOP_LOSS_PCT', 0.95)

# Telegram settings
TELEGRAM_API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')