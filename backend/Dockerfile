FROM python:3.12-slim

# Define build arguments
ARG ENV=prod

# Set working directory
WORKDIR /code
ENV PYTHONPATH="/code:${PYTHONPATH}"
ENV PYTHONUNBUFFERED=1

# Expose necessary ports
EXPOSE 8000

# Install curl and other dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    libyaml-dev \
    postgresql \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.6 /uv /uvx /bin/

# Install the notebook backend
COPY requirements.lock .
COPY requirements-dev.lock .
RUN if [ "$ENV" != "prod" ]; then \
        uv pip install --system --no-cache -r requirements-dev.lock; \
    else \
        uv pip install --system --no-cache -r requirements.lock; \
    fi


# Copy the backend code
COPY . .