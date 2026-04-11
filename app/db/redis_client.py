import os
from dotenv import load_dotenv
import redis.asyncio as redis

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize the async Redis client
# decode_responses=True ensures we get normal Python strings back, not raw bytes
cache = redis.from_url(REDIS_URL, decode_responses=True)