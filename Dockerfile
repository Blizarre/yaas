from python:3.9

WORKDIR /server
COPY requirements.txt /server/
RUN pip install -r requirements.txt

COPY app.py tasks.py /server/

USER 10000

