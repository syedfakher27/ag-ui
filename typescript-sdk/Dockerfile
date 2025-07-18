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

# Install all workspace dependencies
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
FROM node:18-slim

RUN npm install -g pnpm

WORKDIR /app

COPY --from=builder /app .

ENV PORT=3000
EXPOSE 3000

CMD ["sh", "-c", "pnpm start"]
