FROM python:3.11-slim

WORKDIR /app

# Install build tools needed for pyahocorasick + cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project (minus .dockerignore exclusions)
COPY . .

# Declare shared volume mounts
VOLUME ["/shared", "/data"]

# Environment defaults (overridden by K8s env block)
ENV LOG_INPUT_PATH=/shared/app.log
ENV STATS_OUTPUT_PATH=/data/stats.json
ENV VAULT_DB_PATH=/data/vault.db
ENV VAULT_KEY_PATH=/data/vault.key
ENV LINEAGE_DB_PATH=/data/lineage.db
ENV LINEAGE_KEY_PATH=/data/lineage.key
ENV AUTHORIZED_ACTORS=admin,security-team
ENV PYTHONUNBUFFERED=1

# Run as non-root for security
RUN useradd -m -u 1000 logshield
USER logshield

# Copy the in-pod admin CLI for SecureReveal
COPY vault_admin.py /app/vault_admin.py

CMD ["python", "sidecar/main.py"]
