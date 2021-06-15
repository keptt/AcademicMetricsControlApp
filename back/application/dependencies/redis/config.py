import os
import fastapi_plugins


class AppSettings(fastapi_plugins.RedisSettings):
    api_name: str                   = str(__name__)
    redis_host: str                 = os.getenv('REDIS_HOST') or 'localhost'
    redis_port: int                 = os.getenv('REDIS_PORT') or 6379
    redis_password: str             = os.getenv('REDIS_PASSWORD') or None
    redis_connection_timeout: int   = os.getenv('REDIS_CONNECTION_TIMEOUT') or 2


depends_redis = fastapi_plugins.depends_redis

redis_config = AppSettings()

redis_plugin = fastapi_plugins.redis_plugin
