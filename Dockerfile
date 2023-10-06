FROM python:3.9-slim

WORKDIR /code

RUN apt-get update && apt-get install -y \
  ffmpeg \
  libsm6 \
  libxext6 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["gunicorn", "--conf", "/code/app/gunicorn_conf.py", "--bind", "0.0.0.0:80", "app.app:app"]