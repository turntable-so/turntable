from python:3.11

# Install uv
ADD --chmod=755 https://astral.sh/uv/0.2.18/install.sh /install.sh
RUN /install.sh && rm /install.sh

# Install psycopg2
RUN uv pip install psycopg2-binary