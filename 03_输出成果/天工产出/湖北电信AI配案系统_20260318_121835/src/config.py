"""配置文件"""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/app")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
