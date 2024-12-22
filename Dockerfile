from python:3.12

WORKDIR /server

RUN groupadd -r yaas && \
       useradd --no-log-init -m -r -g yaas yaas && \
       mkdir /youtube_files && \
       chown yaas:yaas /youtube_files

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /server/
RUN pip install -r requirements.txt

COPY app.py tasks.py /server/
COPY templates/ /server/templates

VOLUME /youtube_files

USER yaas
