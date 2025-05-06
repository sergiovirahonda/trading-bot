# Python imports
import time
import sys
import asyncio
import traceback

# App imports
from src.conf.logger import Trace
from src.adapters.exchange import Exchange
from src.adapters.redis import RedisAdapter
from src.adapters.telegram import TelegramAdapter
from src.conf.settings import (
    API_KEY,
    API_SECRET,
    API_URL,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    ASSET_WATCHLIST,
    TELEGRAM_API_TOKEN,
    TELEGRAM_CHAT_ID,
)
from src.domain.calculator.value_objects import (
    SELL_SIGNAL,
)
from src.domain.calculator.services import IndicatorCalculatorDomainServices
from src.domain.trading.entities import TradingOrderFactory
from src.domain.trading.services import TradingDomainServices
from src.application.trading.services import TradingApplicationServices
from src.application.calculator.services import IndicatorCalculatorApplicationServices

# Logger initialization
logger = Trace(__name__).logger

# Initialize Redis and Exchange clients
redis_client = RedisAdapter(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
)

# Initialize Exchange client
exchange = Exchange(
    api_key=API_KEY,
    api_secret=API_SECRET,
    api_url=API_URL,
)

client = exchange.get_client()

# Initialize Telegram adapter
telegram = TelegramAdapter(
    api_token=TELEGRAM_API_TOKEN,
    chat_id=TELEGRAM_CHAT_ID,
)

# Domain services
trading_domain_services = TradingDomainServices(
    exchange_client=exchange,
    redis_client=redis_client,
    telegram_adapter=telegram,
)
indicator_calculator_domain_services = IndicatorCalculatorDomainServices()

# Application services
indicator_calculator_app_services = IndicatorCalculatorApplicationServices(
    indicator_calculator_domain_services=indicator_calculator_domain_services,
)
trading_app_services = TradingApplicationServices(
    calculator_indicator_app_services=indicator_calculator_app_services,
    trading_domain_services=trading_domain_services,
)

# trading_app_services.wipe_current_asset()

async def main():
    logger.info("Starting trading bot...")
    current_asset = trading_app_services.get_current_asset()
    logger.info(f"Current asset: {current_asset}")
    if current_asset.get("asset") == "USDT":
        logger.info("Current asset is USDT. No action taken.")
        sys.exit(0)
    if not current_asset.get("entry_price"):
        logger.info("Entry price not set. Fetching current asset price...")
        entry_price = trading_app_services.get_asset_price(current_asset.get("current_asset"))
        trading_app_services.set_current_asset(current_asset.get("current_asset"), entry_price=entry_price)
        logger.info(f"Entry price set for {current_asset.get('current_asset')}: {entry_price}")
        current_asset = trading_app_services.get_current_asset()
        logger.info(f"Current asset updated: {current_asset}")
    else:
        logger.info(f"Entry price already set for {current_asset.get('current_asset')}: {current_asset.get('entry_price')}")

    short_term_hd = trading_app_services.get_historical_data(
        symbol=f"{current_asset.get('current_asset')}USDT",
        interval="5m",
        lookback=288,
    )
    long_term_hd = trading_app_services.get_historical_data(
        symbol=f"{current_asset.get('current_asset')}USDT",
        interval="1h",
        lookback=168,
    )
    logger.info("Historical data fetched successfully.")
    current_close_price = short_term_hd['close'].iloc[-1]
    logger.info(f"Current close price: {current_close_price}")
    # Percentage change
    entry_price = current_asset.get("entry_price")
    change_pct = ((current_close_price - entry_price) / entry_price) * 100
    logger.info(f"Percentage change: {change_pct}%")
    # Apply trend indicators
    short_term_trend_indicators = indicator_calculator_app_services.apply_trend_indicators(
        close_prices=short_term_hd['close'],
    )
    long_term_trend_indicators = indicator_calculator_app_services.apply_trend_indicators(
        close_prices=long_term_hd['close'],
    )
    logger.info("Trend indicators applied successfully.")
    # Apply Bollinger Bands indicators
    short_term_trade_indicators = indicator_calculator_app_services.apply_bollinger_bands_indicators(
        close_prices=short_term_hd['close'],
    )
    long_term_trade_indicators = indicator_calculator_app_services.apply_bollinger_bands_indicators(
        close_prices=long_term_hd['close'],
    )
    logger.info("Bollinger Bands indicators applied successfully.")
    # Evaluate trading decision
    short_term_decision = indicator_calculator_app_services.evaluate_trading_decision(
        entry_price=current_asset.get("entry_price"),
        close_prices=short_term_hd['close'],
        trend_indicators=short_term_trend_indicators,
        trade_indicators=short_term_trade_indicators,
    )
    long_term_decision = indicator_calculator_app_services.evaluate_trading_decision(
        entry_price=current_asset.get("entry_price"),
        close_prices=long_term_hd['close'],
        trend_indicators=long_term_trend_indicators,
        trade_indicators=long_term_trade_indicators,
    )
    logger.info("Trading decision evaluated successfully.")
    logger.info(f"Short-term decision: {short_term_decision}")
    logger.info(f"Long-term decision: {long_term_decision}")

    if short_term_decision == SELL_SIGNAL and long_term_decision == SELL_SIGNAL:
        logger.info("Both short-term and long-term decisions indicate selling.")

        market_analysis = trading_app_services.analyze_markets(
            watchlist=ASSET_WATCHLIST,
        )
        logger.info(f"Market analysis: {market_analysis}")
        best_market = indicator_calculator_app_services.get_best_market_opportunity(
            market_analysis=market_analysis,
        )
        if best_market:
            if best_market.asset == current_asset.get("current_asset"):
                logger.info("No action taken. Current asset is the best market opportunity.")
                return
            logger.info(f"Best market opportunity found: {best_market.asset}")
            # Get trading intent
            trading_intent = trading_app_services.get_trade_intent(
                base_asset=current_asset.get("current_asset"),
                quote_asset=best_market.asset,
            )
            logger.info(f"Trade intent: {trading_intent.as_dict()}")
            # Perform calculations for placing an order
            equivalent_volume = trading_app_services.get_equivalent_volume(
                origin_asset=trading_intent.origin,
                target_asset=trading_intent.quote,
            )
            logger.info(f"Equivalent volume calculated: {equivalent_volume}")
            current_holding_value = trading_app_services.get_current_asset_holding_value()
            current_balance = trading_app_services.get_asset_balance(
                asset=current_asset.get("current_asset"),
            )
            order = TradingOrderFactory.create_order(
                symbol=trading_intent.symbol,
                side=trading_intent.side,
                quantity=equivalent_volume,
                usd_amount=current_holding_value,
                profit=(best_market.price * equivalent_volume) - (entry_price * current_balance)
            )
            logger.info(f"Placing order: {order.as_dict()}")
            await trading_app_services.place_order(order=order)
            logger.info(f"Order placed successfully: {order.as_dict()}")
            trading_app_services.set_current_asset(best_market.asset, entry_price=best_market.price)
        else:
            logger.info("No suitable market found for buying.")
            logger.info("Implementing stop loss strategy.")
            stop_loss_order = await trading_app_services.stop_loss()
            logger.info(f"Stop loss order placed: {stop_loss_order.as_dict()}")
            trading_app_services.set_current_asset("USDT", entry_price=stop_loss_order.usd_amount)
            sys.exit(0)

    else:
        logger.info("Market conditions not met for selling. No action taken.")
        logger.info("Trading bot stopping.")

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception:
            logger.error(traceback.format_exc())
            continue
        logger.info("-------------------------------")
        time.sleep(180)
        logger.info("Waking up...")