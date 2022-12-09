####################################################################################################
## Builder image
####################################################################################################
FROM python:3.11-alpine3.16 AS builder

# Note that some libaries require Linux Kernel C Headers
RUN apk add --no-cache \
  ca-certificates \
  build-base \
  curl \
  linux-headers 

# Add Poetry locally
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN python -m pip install --upgrade pip setuptools
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="${PATH}:/root/.local/bin"

# Install Rust. This is needed by orjson
RUN curl https://sh.rustup.rs -sSf | sh -s -- --profile minimal --default-toolchain nightly -y
ENV PATH="${PATH}:/root/.cargo/bin"

WORKDIR /Akari

COPY /pyproject.toml /Akari/
COPY /poetry.lock /Akari/

# Create dependency wheels
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes \
  && pip wheel --wheel-dir=/Akari/wheels -r requirements.txt

####################################################################################################
## Final image
####################################################################################################
FROM python:3.11-alpine3.16

RUN apk add --no-cache \
  ca-certificates \
  tini \
  bash \
  wget

WORKDIR /Akari
COPY /Bot/akari.py /Akari/Bot/akari.py
COPY /Bot/akaricore.py /Akari/Bot/akaricore.py
COPY /Bot/Cogs /Akari/Bot/Cogs
COPY /Scripts/seeder.py /Akari/seeder.py
COPY /Bot/Libs/ /Akari/Bot/Libs/
COPY /Docker/Alpine-Docker/start.sh /Akari/start.sh
COPY /Docker/Alpine-Docker/wait-for /Akari/wait-for

# Copy dependency wheels from builder stage
COPY --from=builder /Akari/wheels /Akari/wheels
COPY --from=builder /Akari/requirements.txt /Akari/requirements.txt

RUN pip install --upgrade pip setuptools

# Add an unprivileged user and set directory permissions
RUN adduser --disabled-password --gecos "" akari \
  && chown -R akari:akari /Akari \
  && chmod +x /Akari/start.sh \
  && chmod +x /Akari/wait-for

USER akari

# Set up path so pip won't complain again
ENV PATH="${PATH}:/home/akari/.local/bin"

# Install dependencies
RUN pip install --user --no-index --find-links=/Akari/wheels -r requirements.txt

ENTRYPOINT ["/sbin/tini", "--"]

CMD ["/Akari/start.sh"]

STOPSIGNAL SIGTERM

# Image metadata
LABEL org.opencontainers.image.title="Akari"
LABEL org.opencontainers.image.description="A multipurpose toolkit bot for servers"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.source="https://github.com/No767/Akari"
