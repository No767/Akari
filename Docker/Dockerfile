####################################################################################################
## Builder image
####################################################################################################
FROM python:3.11-slim-bullseye AS builder

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt update \
  && apt install -y --no-install-recommends \
  build-essential \
  ca-certificates \
  curl \
  git

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN python -m pip install --upgrade pip setuptools
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="${PATH}:/root/.local/bin"

WORKDIR /Akari

COPY /pyproject.toml /Akari/
COPY /poetry.lock /Akari/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --only main \
  && pip wheel --wheel-dir=/Akari/wheels -r requirements.txt

####################################################################################################
## Final image
####################################################################################################
FROM python:3.11-slim-bullseye
RUN apt update \
  && apt install -y --no-install-recommends \
  tini \
  ca-certificates \
  bash \
  netcat \
  git

WORKDIR /Akari
COPY /Bot/akaribot.py /Akari/Bot/akaribot.py
COPY /Bot/akaricore.py /Akari/Bot/akaricore.py
COPY /Bot/Cogs /Akari/Bot/Cogs
COPY /Bot/Libs/ /Akari/Bot/Libs/
COPY /Migrations /Akari/Migrations
COPY /migration-runner.py /Akari/migration-runner.py
COPY /Docker/start.sh /Akari/start.sh
COPY /Docker/wait-for /Akari/wait-for

COPY --from=builder /Akari/wheels /Akari/wheels
COPY --from=builder /Akari/requirements.txt /Akari/requirements.txt

RUN pip install --upgrade pip setuptools

RUN adduser --disabled-password --gecos "" akari \
  && chown -R akari:akari /Akari \
  && chmod +x /Akari/start.sh \
  && chmod +x /Akari/wait-for

USER akari

ENV PATH="${PATH}:/home/akari/.local/bin"

RUN pip install --user --no-index --find-links=/Akari/wheels -r requirements.txt

# IPC ports
EXPOSE 1025
EXPOSE 20000

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["/Akari/start.sh"]

STOPSIGNAL SIGTERM

LABEL org.opencontainers.image.title="Akari"
LABEL org.opencontainers.image.description="A utility toolkit bot for Discord support servers"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.source="https://github.com/No767/Akari"
