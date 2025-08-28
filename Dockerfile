# Base image with Python and uv, installs deps system-wide (no venv)
FROM python:3.13-slim AS base

# Install uv and minimal build tools
COPY --from=ghcr.io/astral-sh/uv:0.7.19 /uv /bin/
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Workdir for app
WORKDIR /app

# Copy only dependency manifests for layer caching
COPY pyproject.toml uv.lock ./

ENV UV_PROJECT_ENVIRONMENT=/opt/venv
RUN uv sync --frozen --no-cache

# Make the venv the default Python
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
ENTRYPOINT ["/opt/venv/bin/python"]

# Development image: mounts source via volume; no COPY of source here
FROM base AS dev
WORKDIR /app
EXPOSE 8000
# Keep entrypoint simple for local aliasing; code is bind-mounted by compose
CMD ["manage.py", "runserver", "0.0.0.0:8000"]


# Production image: copy full source, collect static, run gunicorn
FROM base AS prod
WORKDIR /app

# Copy the entire project (respects .dockerignore)
COPY . .

EXPOSE 8000
ENTRYPOINT ["/bin/sh", "-c"]
CMD /opt/venv/bin/python manage.py migrate --noinput && \
    /opt/venv/bin/python manage.py collectstatic --noinput && \
    exec /opt/venv/bin/python -m gunicorn config.wsgi:application --bind 0.0.0.0:8000
