from flask import Flask, redirect, render_template, request
from collections import deque
from tasks import download as celery_download, clean as celery_clean
import os
from werkzeug.exceptions import BadRequest
import yt_dlp as y
from collections import namedtuple
from yt_dlp.utils import DownloadError
import logging

logger = logging.Logger(__name__)

app = Flask(__name__)

in_progress = deque()

File = namedtuple("File", ["title", "promise"])

def has_failed(file: File):
    return isinstance(file.promise.result, DownloadError)

@app.route("/download", methods = ['POST'])
def download():
    if "videourl" not in request.form:
        raise BadRequest("Video inconnue")
    format = request.form.get("format")
    if format == "normal":
        format = None
    url = request.form["videourl"]
    with y.YoutubeDL() as ydl:
        title = ydl.extract_info(url, download=False, process=True)["title"]
    file = File(title, celery_download.delay(url, format))
    in_progress.appendleft(file)
    return redirect("/status", code=302)

@app.route("/status")
def status():
    return render_template('status.html.j2', in_progress=in_progress, has_failed=has_failed)

@app.route("/clean")
def clean():
    global in_progress
    logger.warn(f"Cleaning up the tasks")
    for task in in_progress:
        if task.promise.ready():
            logger.info(f"Getting result from task {task}")
            try:
                task.promise.get()
            except Exception as e:
                logger.error("Task failed with error %s", e, exc_info=1)
        else:
            logger.info(f"Killing task {task}")
            task.promise.revoke(terminate=True, signal='SIGKILL')
    in_progress = deque()  
    logger.warn(f"Calling cleanup task")
    celery_clean.delay().get()
    return redirect("/status", code=302)


@app.route("/")
def home():
    return redirect("/status", code=302)


if __name__ == "__main__":
    app.run()
