FROM python:3.11

WORKDIR /code

# Install uv
ADD --chmod=755 https://astral.sh/uv/0.2.18/install.sh /install.sh
RUN bash /install.sh && rm /install.sh

# Install dbtx
RUN /root/.cargo/bin/uv pip install dbtx --system

COPY . .