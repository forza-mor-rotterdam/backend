FROM mguikema/ubi8-python-39-postgis

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

COPY requirements.txt /requirements.txt

RUN yum update -y \
    && yum install -y \
                nc \
                pkg-config \
                graphviz \
    && pip install -r /requirements.txt \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/

RUN chgrp root /app && chown root:2000 /app && chmod g+w /app
ENV LD_LIBRARY_PATH=/usr/local/lib64:$LD_LIBRARY_PATH

ENV DJANGO_SETTINGS_MODULE=signals.settings
ARG DJANGO_SECRET_KEY=insecure_docker_build_key

COPY app /app/
COPY deploy /deploy/

RUN mkdir -p /media && mkdir -p /static && chown 2000 /media && chown 2000 /static

USER 2000

RUN SECRET_KEY=$DJANGO_SECRET_KEY python manage.py collectstatic --no-input