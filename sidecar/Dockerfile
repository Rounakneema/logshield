FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy and install Python dependencies (all packages have pre-built manylinux wheels)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project (minus .dockerignore exclusions)
COPY . .

# Declare shared volume mounts
VOLUME ["/shared", "/data"]

# Environment defaults (overridden by compose/k8s env block)
ENV LOG_INPUT_PATH=/shared/app.log
ENV STATS_OUTPUT_PATH=/data/stats.json
ENV VAULT_DB_PATH=/data/vault.db
ENV VAULT_KEY_PATH=/data/vault.key
ENV LINEAGE_DB_PATH=/data/lineage.db
ENV LINEAGE_KEY_PATH=/data/lineage.key
ENV AUTHORIZED_ACTORS=admin,security-team
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

CMD ["python", "sidecar/main.py"]
