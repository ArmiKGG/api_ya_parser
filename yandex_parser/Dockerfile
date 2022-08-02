FROM python:3.8

WORKDIR /app


ENV STARTING_PAGE=market.yandex.ru
ENV ROUTER=localhost
ENV ROUTER_PORT=4444
ENV APIKEY_2CAPTCHA=480b03b270dfb2725f9e6023f0554efc


COPY requirements.txt .
COPY utils.py .
COPY wsgi.py .
COPY app.py .
COPY cookies ./cookies

RUN pip install -r requirements.txt


CMD gunicorn --worker-class gevent \
  --workers 20 \
  --bind 0.0.0.0:5000 \
  --timeout 0 \
  --limit-request-line 0 \
  --preload \
  wsgi:app
