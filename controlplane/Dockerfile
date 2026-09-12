FROM python:3.11-slim

WORKDIR /app

# Flask is the only dependency for the webhook server
RUN pip install --no-cache-dir flask

COPY controlplane/webhook.py /app/webhook.py

# TLS cert/key are mounted from a Kubernetes Secret at this path
ENV TLS_CERT=/etc/webhook/certs/tls.crt
ENV TLS_KEY=/etc/webhook/certs/tls.key
ENV PYTHONUNBUFFERED=1

EXPOSE 8443

CMD ["python", "webhook.py"]
