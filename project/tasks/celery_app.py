from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

app = Celery(
    broker=f'redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}',
    backend=f'redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}'
)
