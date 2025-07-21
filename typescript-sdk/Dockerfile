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
RUN pnpm install && pnpm build

# Finally build frontend (dojo)
WORKDIR /app/apps/dojo
RUN pnpm install && pnpm build

WORKDIR /app/apps/dojo 

# # Expose port
EXPOSE 3000

CMD ["pnpm", "start"]