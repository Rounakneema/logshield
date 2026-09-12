FROM python:3.11-slim

WORKDIR /app

# Install FastAPI + uvicorn (for demo-app server)
RUN pip install --no-cache-dir fastapi uvicorn[standard]

# Copy only the target-app source
COPY target-app/app.py /app/app.py

VOLUME ["/shared"]

# CRITICAL: app.py reads LOG_OUTPUT_PATH for the log file destination
ENV LOG_OUTPUT_PATH=/shared/app.log
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Run with uvicorn (FastAPI requires an ASGI server)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
