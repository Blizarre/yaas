from celery import Celery
import logging
import youtube_dl as y
import os

VIDEO_DIR = os.environ["VIDEO_DIR"]
FILE_NAME_TEMPLATE = "%(title)s-%(id)s.%(ext)s"
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

logger = logging.Logger(__name__)

@app.task(bind=True)
def download(self, url: str, format: str):
    def progress_hook(data):
        if data.get("status") in ["downloading", "finished"]:
            self.update_state(state='PROGRESS',
                            meta=data)

    logger.info(f"Starting dl task for {url}")
    with y.YoutubeDL({
        'progress_hooks': [progress_hook],
        "outtmpl": os.path.join(VIDEO_DIR, FILE_NAME_TEMPLATE), 
        "restrictfilenames": True,
        "format": format,
    }) as ydl:
        ydl.download([url])
    logger.info(f"Finished dl task for {url} successfully")


@app.task()
def clean():
    logger.warn(f"Cleaning up the {VIDEO_DIR} directory")
    for file_name in os.listdir(VIDEO_DIR):
        logger.info(f"Removing {file_name}")
        os.remove(os.path.join(VIDEO_DIR, file_name))
