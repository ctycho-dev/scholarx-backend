# from redis.asyncio import Redis, ConnectionError, ConnectionPool
# from app.core.config import settings
# from tenacity import retry, wait_fixed, stop_after_delay


# pool = ConnectionPool.from_url(
#     settings.REDIS_URL,
#     max_connections=10,
#     retry_on_timeout=True,
#     socket_keepalive=True,
#     health_check_interval=30
# )

# # Create Redis client using the pool
# redis_client = Redis(connection_pool=pool, encoding="utf-8", decode_responses=True)

# # Initialize the Redis client
# redis_client = Redis(host=settings.redis_host, port=settings.redis_port)


# @retry(wait=wait_fixed(2), stop=stop_after_delay(30), reraise=True)
# async def connect_to_redis():
#     """Ensure the Redis client can connect."""
#     try:
#         await redis_client.ping()  # Asynchronous ping
#         return redis_client
#     except ConnectionError as e:
#         raise RuntimeError(f"Could not connect to Redis: {e}") from e


# async def get_redis_client():
#     """Get Redis client with a retry mechanism."""
#     try:
#         return await connect_to_redis()
#     except ConnectionError as e:
#         raise RuntimeError(f"Could not connect to Redis: {e}") from e
