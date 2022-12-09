####################################################################################################
## Builder image
####################################################################################################
FROM python:3.11-slim-bullseye AS builder

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt update \
  && apt install -y --no-install-recommends \
  build-essential \
  ca-certificates \
  curl

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN python -m pip install --upgrade pip setuptools
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="${PATH}:/root/.local/bin"

RUN curl https://sh.rustup.rs -sSf | sh -s -- --profile minimal --default-toolchain nightly -y
ENV PATH="${PATH}:/root/.cargo/bin"

WORKDIR /Akari

COPY /pyproject.toml /Akari/
COPY /poetry.lock /Akari/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes \
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
  netcat

WORKDIR /Akari
COPY /Bot/akari.py /Akari/Bot/akari.py
COPY /Bot/akaricore.py /Akari/Bot/akaricore.py
COPY /Bot/Cogs /Akari/Bot/Cogs
COPY /Scripts/seeder.py /Akari/seeder.py
COPY /Bot/Libs/ /Akari/Bot/Libs/
COPY /Docker/Debian-Docker/start.sh /Akari/start.sh
COPY /Docker/Debian-Docker/wait-for /Akari/wait-for

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

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["/Akari/start.sh"]

STOPSIGNAL SIGTERM

LABEL org.opencontainers.image.title="Akari"
LABEL org.opencontainers.image.description="A multipurpose toolkit bot for servers"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.source="https://github.com/No767/Akari"
