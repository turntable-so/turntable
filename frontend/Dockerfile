# Dockerfile
FROM node:20-alpine AS base

# Define build arguments
ARG ENV=prod

# Set working directory
WORKDIR /app

COPY . .

# Install pnpm
RUN npm install -g pnpm

# Install dependencies
RUN pnpm install

# Build the frontend
RUN if [ "$ENV" = "prod" ]; then \
        pnpm build; \
    fi

EXPOSE 3000
