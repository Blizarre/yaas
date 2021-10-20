from flask import Flask, redirect

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
    return redirect("/status", code=302)

@app.route("/status")
def status():
    ret = ""
    for youtube_id, infos in in_progress.items():
        result = infos.promise.result
        info = infos.promise.info

        ret += (
            f'{youtube_id} {infos.title} - '
            f'{"Termine" if infos.promise.ready() else "En cours"}, '
        )

        if isinstance(result, DownloadError):
            ret += f'Erreur'
        elif info is not None:
            ret += f'{info.get("_percent_str")}%, Taille totale {info.get("_total_bytes_str")}'
        ret += '<br/>'
    return ret

if __name__ == "__main__":
    app.run()