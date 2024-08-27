FROM python:3.11

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
    postgresql \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
ADD --chmod=755 https://astral.sh/uv/0.2.18/install.sh /install.sh
RUN /install.sh && rm /install.sh

# Install the notebook backend
COPY requirements.lock .
COPY requirements-dev.lock .
RUN if [ "$ENV" = "dev" ]; then \
        /root/.cargo/bin/uv pip install --system --no-cache -r requirements-dev.lock; \
    else \
        /root/.cargo/bin/uv pip install --system --no-cache -r requirements.lock; \
    fi


# Copy the backend code
COPY . .

# Make entrypoint scripts executable
RUN chmod +x /code/entrypoint.sh
RUN chmod +x /code/entrypoint-dev.sh