from python:3.9

WORKDIR /server

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /server/
RUN pip install -r requirements.txt

COPY app.py tasks.py /server/
COPY templates/ /server/templates

USER 10000

