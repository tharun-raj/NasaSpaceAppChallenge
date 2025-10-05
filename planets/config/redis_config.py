import os
from dotenv import load_dotenv
import redis
from redis.exceptions import RedisError

load_dotenv()

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis.from_url(redis_host)

def test_redis_connection():
    try:
        if r.ping():
            print("uccessfully connected to Redis!")
            return True
    except RedisError as e:
        print(f"Failed to connect to Redis: {e}")
        return False

# Test connection on import
test_redis_connection()