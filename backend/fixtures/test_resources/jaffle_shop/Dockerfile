FROM python:3.12-slim

WORKDIR /code

# Install uv
RUN apt-get update && apt-get install -y curl
ADD --chmod=755 https://astral.sh/uv/0.2.18/install.sh /install.sh
RUN bash /install.sh && rm /install.sh

# Install dbtx
RUN /root/.cargo/bin/uv pip install dbtx --system

COPY . .