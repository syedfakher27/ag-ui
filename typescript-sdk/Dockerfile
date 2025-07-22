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

WORKDIR /app/apps/dojo 

# # Expose port
EXPOSE 3000

CMD ["pnpm", "start"]

# gcloud builds submit -t gcr.io/slamsportsai/slams-agui-app

# gcloud run deploy slams-agui-app --image gcr.io/slamsportsai/slams-agui-app --platform managed --region us-central1 --allow-unauthenticated