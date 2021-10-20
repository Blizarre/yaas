from celery import Celery
import logging
import youtube_dl as y
import os

VIDEO_DIR = os.environ.get("VIDEO_DIR", ".")
FILE_NAME_TEMPLATE = "%(title)s-%(id)s.%(ext)s"
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

logger = logging.Logger(__name__)

@app.task
def download(url: str):
    logger.info(f"Starting dl task for {url}")
    with y.YoutubeDL({"outtmpl": os.path.join(VIDEO_DIR, FILE_NAME_TEMPLATE)}) as ydl:
        ydl.download([url])
    logger.info(f"Finished dl task for {url} successfully")
