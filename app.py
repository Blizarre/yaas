from flask import Flask

from tasks import download as celery_download
import os
from werkzeug.exceptions import BadRequest
import youtube_dl as y
from collections import namedtuple
from youtube_dl.utils import DownloadError

app = Flask(__name__)

in_progress = {}

File = namedtuple("File", ["youtube_id", "title", "promise"])

@app.route("/download/<youtube_id>")
def download(youtube_id: str):
    if youtube_id in in_progress:
        raise BadRequest(f"Already downloading {youtube_id}")
    url = f'https://www.youtube.com/watch?v={youtube_id}'
    ydl_opts = {}
    with y.YoutubeDL(ydl_opts) as ydl:
        title = ydl.extract_info(url, download=False, process=True)["title"]
    file = File(youtube_id, title, celery_download.delay(url))
    in_progress[youtube_id] = file
    return title

@app.route("/status")
def status():
    ret = ""
    for youtube_id, infos in in_progress.items():
        info = infos.promise.info
        if isinstance(info, DownloadError):
            ret += (
                f'{youtube_id} {infos.title} - '
                f'Erreur'
            )
        else:
            ret += (
                f'{youtube_id} {infos.title} - '
                f'{"Termine" if infos.promise.ready() else "En cours"}, '
                f'{info.get("_percent_str")}%, Taille totale {info.get("_total_bytes_str")}<br/>'
            )
    return ret

if __name__ == "__main__":
    app.run()