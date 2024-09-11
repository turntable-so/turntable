FROM python:3.11

WORKDIR /code

# Install uv
ADD --chmod=755 https://astral.sh/uv/0.2.18/install.sh /install.sh
RUN bash /install.sh && rm /install.sh

COPY . .