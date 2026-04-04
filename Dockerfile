FROM python:3.13-slim

# Bring in uv binary from the official image.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

# Install dependencies first to maximize Docker layer caching.
COPY pyproject.toml ./
RUN uv sync --no-dev

# Copy app source.
COPY . .

CMD ["uv", "run", "gunicorn", "-w", "2", "app:create_app()", "-b", "0.0.0.0:5000"]
