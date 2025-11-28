import redis
import json
import redis.exceptions


class RedisCache:
    """Redis setup for caching"""

    def __init__(self, host: str, port: int):
        self.r = redis.Redis(host=host, port=port, decode_responses=True)

    async def set(
        self, key: str, value, exp_seconds: int = 31622400, indexes: list[str] = []
    ):
        """This method sets a key with the values in the cache"""
        try:
            json_value = json.dumps(value)
            self.r.set(key, json_value, ex=exp_seconds)
            if indexes:
                for index in indexes:
                    self.r.sadd(index, key)  # Add the key to the index
        except redis.exceptions.ConnectionError as e:
            print(f"Redis Connection Error: {e}")

    async def get(self, key: str):
        """Gets a cached value from the Redis cache"""
        try:
            json_value = self.r.get(key)
            if json_value:
                return json.loads(json_value)
        except redis.exceptions.ConnectionError as e:
            print(f"Redis Connection Error: {e}")
            return None

    async def delete(self, key: str, index: str = None):
        """Deletes a cached value"""
        try:
            self.r.delete(key)
            if index:
                self.r.srem(index, key)  # Remove the key from the index
        except redis.exceptions.ConnectionError as e:
            print(f"Redis Connection Error: {e}")

    async def get_index(self, indexes: list[str]) -> list:
        """Gets all the items saved in an index"""
        output = []
        try:
            for index in indexes:
                keys = self.r.smembers(index)
                if keys:
                    for key in keys:
                        value = await self.get(key)
                        output.append(value)
            return output
        except redis.exceptions.ConnectionError as e:
            print(f"Redis Connection Error: {e}")
            return []

    async def delete_indexgroup(self, index: str):
        """deletes all the values belonging to keys in an index"""
        try:
            keys = self.r.smembers(index)
            if keys:
                for key in keys:
                    self.r.delete(key)
                self.r.delete(index)
        except redis.exceptions.ConnectionError as e:
            print(f"Redis Connection Error: {e}")


redis_cache = RedisCache(host="localhost", port=6379)
