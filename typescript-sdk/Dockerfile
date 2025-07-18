# ---------------------------------------------
# Stage 1: Build packages and frontend
# ---------------------------------------------
FROM node:18 as builder

# Install pnpm
RUN npm install -g pnpm && \
    apt-get update && \
    apt-get install -y protobuf-compiler


# Set working directory
WORKDIR /app

# Copy all project files (monorepo)
COPY . .

# Change to typescript-sdk directory where package.json exists
WORKDIR /app/typescript-sdk

# Install dependencies
RUN pnpm install


WORKDIR /app/typescript-sdk/packages/cli
RUN pnpm install && pnpm build

# Step into other dependent packages and build in order
WORKDIR /app/typescript-sdk/packages/core
RUN pnpm install && pnpm build

# Step into the proto package and run required steps first
WORKDIR /app/typescript-sdk/packages/proto
RUN pnpm install && pnpm build

WORKDIR /app/typescript-sdk/packages/encoder
RUN pnpm install && pnpm build

WORKDIR /app/typescript-sdk/packages/client
RUN pnpm install && pnpm build

# Finally build frontend (dojo)
WORKDIR /app/typescript-sdk/apps/dojo
RUN pnpm install && pnpm build

# ---------------------------------------------
# Stage 2: Serve frontend
# ---------------------------------------------
# ---------------------------------------------
# Stage 2: Serve frontend
# ---------------------------------------------
FROM node:18-slim

# Install pnpm globally
RUN npm install -g pnpm

# Set working directory to where dojo package.json lives
WORKDIR /app/apps/dojo

# Copy only the built frontend from builder
COPY --from=builder /app/typescript-sdk/apps/dojo /app/apps/dojo

ENV PORT=3000
EXPOSE 3000

CMD ["pnpm", "start"]
