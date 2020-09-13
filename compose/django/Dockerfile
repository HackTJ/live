FROM python:3.8

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements.txt /requirements.txt

RUN python -m pip install -r /requirements.txt \
    && groupadd -r django \
    && useradd -r -g django django

COPY ./compose/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh && chmod +x /entrypoint.sh

COPY . /app
RUN chown -R django /app

COPY ./compose/django/start.sh /start.sh
RUN sed -i 's/\r//' /start.sh \
    && chmod +x /start.sh \
    && chown django /start.sh

WORKDIR /app

RUN mkdir /data \
    && chown django.django /data

RUN mkdir /data/static \
    && chown django.django /data/static

RUN mkdir /data/media \
    && chown django.django /data/media

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
