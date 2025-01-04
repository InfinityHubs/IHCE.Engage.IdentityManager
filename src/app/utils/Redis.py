import redis
from src.config import AppConfigs

class RedisClientConnector:
    def __init__(self):
        self.client = None

    def connect(self):
        """Initialize the Redis connection."""
        try:
            self.client = redis.Redis(
                host=AppConfigs.REDIS_HOST,
                port=AppConfigs.REDIS_PORT,
                password=AppConfigs.REDIS_PASSWORD,
                username=AppConfigs.REDIS_USERNAME,
                decode_responses=True,
            )
            self.client.ping()  # Check connection
            print("Redis connected successfully.")
        except redis.ConnectionError as e:
            print("Failed to connect to Redis:", e)
            raise e

    async def add(self, key: str, value: str, expire: int = None):
        """Set a key-value pair in Redis."""
        self.client.set(name=key, value=value, ex=expire)

    async def fetch(self, key: str):
        """Get a value from Redis by key."""
        return self.client.get(name=key)

    async def remove(self, key: str):
        """Delete a key from Redis."""
        self.client.delete(key)

# Create a shared RedisService instance
RedisClient = RedisClientConnector()
