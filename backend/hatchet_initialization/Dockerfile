FROM python:3.11

# Set working directory
WORKDIR /code
ENV PYTHONPATH="/code:${PYTHONPATH}"
ENV PYTHONUNBUFFERED=1

# Copy the relevant backend code
COPY hatchet_initialization hatchet_initialization

# Install uv
ADD --chmod=755 https://astral.sh/uv/0.2.18/install.sh /install.sh
RUN bash /install.sh && rm /install.sh

# Install psycopg3
RUN /root/.cargo/bin/uv pip install "psycopg[binary]" --system