FROM python:3.11

WORKDIR /code

COPY . .

# Install uv
ADD --chmod=755 https://astral.sh/uv/0.2.18/install.sh /install.sh
RUN /install.sh && rm /install.sh

RUN chmod +x /code/populate_db.sh