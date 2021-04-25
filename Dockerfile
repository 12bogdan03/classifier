FROM python:3.7

RUN apt-get -y update && apt-get install -y libpq-dev gcc python3-dev curl unzip supervisor

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip && pip install -r requirements.txt && rm -rf ~/.cache/pip/*

COPY . /app/

ADD deployment/conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENTRYPOINT ["/app/docker-entrypoint.sh"]

EXPOSE 8000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
