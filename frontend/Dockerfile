# Dockerfile
FROM node:20-alpine AS base

# Set working directory
WORKDIR /app

COPY . .

# Install pnpm
RUN npm install -g pnpm

# Install dependencies
RUN pnpm install

# Expose the application port for Next from the container
EXPOSE 3000