# Youtube-dl as a service

A very simple front-end for [youtube-dl](https://youtube-dl.org/). Used to download videos from [Youtube](https://www.youtube.com/) and other popular video services in the background.

It is a tiny Python3 [Flask](https://flask.palletsprojects.com/en/2.0.x/) server which offload the downloads to [Celery](https://docs.celeryproject.org/en/stable/index.html) workers ([Redis](https://redis.io/) is used as the backend/broker). The UI is a simple HTML page made with [Bootstrap](https://getbootstrap.com/).

Is is a week-end hack that I did for myself, so there is no multi-tenancy and I took a few shortcuts. Put it behind your favorite
HTTPS reverse proxy ([Caddy](https://caddyserver.com/) handle file browsing, TLS encryption, certificate management and Basic authentication for me).
