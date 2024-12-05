FROM python:3.12-slim

WORKDIR /code

# Install uv
RUN apt-get update && apt-get install -y curl
COPY --from=ghcr.io/astral-sh/uv:0.5.6 /uv /uvx /bin/


# Install dbtx
RUN uv pip install dbtx --system

COPY . .