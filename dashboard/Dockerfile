FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0
ENV PORT=3000
ENV SIDECAR_API_URL=http://auth-service:8080/api

EXPOSE 3000

# Build and start in a single step
RUN npm run build

CMD ["npm", "start"]

