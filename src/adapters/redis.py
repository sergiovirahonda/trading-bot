# Python imports
import json
from datetime import (
    datetime,
    timezone,
)
import redis

class RedisAdapter:
    def __init__(
        self,
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True,
    ):
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=decode_responses,
        )

    def set_state(self, key: str, mapping: dict):
        self.redis.hset(key, mapping=mapping)

    def get_state(self, key: str):
        state = self.redis.hgetall(key)
        if not state:
            return None
        return {k: float(v) if v.replace('.', '', 1).isdigit() else v for k, v in state.items()}

    def clear_state(self, key: str):
        self.redis.delete(key)

    def push_record(self, key: str, record: dict):
        self.redis.lpush(key, json.dumps(record))

    def get_records(self, key: str, limit: int = 50):
        raw_records = self.redis.lrange(key, 0, limit - 1)
        return [json.loads(record) for record in raw_records]

    def set_bot_state(self, symbol: str, entry_price: float):
        entry_time = datetime.now(timezone.utc).isoformat()
        self.redis.hset("bot:state", mapping={
            "current_symbol": symbol,
            "entry_price": entry_price,
            "entry_time": entry_time
        })

    def get_bot_state(self):
        state = self.redis.hgetall("bot:state")
        if not state:
            return None
        return {
            "current_symbol": state.get("current_symbol"),
            "entry_price": float(state.get("entry_price")),
            "entry_time": state.get("entry_time")
        }

    def clear_bot_state(self):
        self.redis.delete("bot:state")

    def add_trade(self, symbol: str, side: str, qty: float, price: float, notes: str = None):
        trade = {
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "price": price,
            "quote_amount": qty * price,
            "notes": notes or ""
        }
        self.redis.lpush("bot:trades", json.dumps(trade))

    def get_trade_history(self, limit: int = 50):
        raw_trades = self.redis.lrange("bot:trades", 0, limit - 1)
        return [json.loads(trade) for trade in raw_trades]

    def clear_trade_history(self):
        self.redis.delete("bot:trades")