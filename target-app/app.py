"""
Sample Application — Intentional Secret Leaker
==============================================
This FastAPI application deliberately simulates the "bad developer"
behaviour that LogShield protects against:

  - On startup: dumps the full environment (including secrets) to the
    debug log. This is extremely common when developers add
    `print(os.environ)` while debugging a deployment issue.

  - On certain endpoints: logs request details including auth headers.

This file is NOT production code. It exists to verify LogShield's interception capabilities.
"""

import logging
import os
from fastapi import FastAPI, Request

Path_to_log = os.environ.get("LOG_OUTPUT_PATH", "/shared/app.log")

os.makedirs(os.path.dirname(Path_to_log) or ".", exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-5s] %(message)s",
    handlers=[
        logging.FileHandler(Path_to_log),   # <- sidecar reads this
        logging.StreamHandler(),             # <- app's own stdout
    ],
)
logger = logging.getLogger("target-app")

app = FastAPI(title="LogShield Target App")


@app.on_event("startup")
async def startup_event():
    """
    Scenario: A developer added this block to debug why the app
    couldn't connect to the database in staging. They fixed the bug
    but forgot to remove the logging call before the production deploy.
    """
    logger.debug("=== Startup diagnostics — full environment dump ===")
    logger.debug(
        f"DATABASE_URL={os.getenv('DATABASE_URL', 'postgres://admin:MyP@ssw0rd123@db:5432/prod')}"
    )
    logger.debug(
        f"AWS_SECRET_ACCESS_KEY={os.getenv('AWS_SECRET_ACCESS_KEY', 'AKIAIOSFODNN7EXAMPLEwJalrXUtnFEMI')}"
    )
    logger.debug(
        f"JWT_SECRET={os.getenv('JWT_SECRET', 'super-secret-jwt-signing-key-do-not-share')}"
    )
    logger.debug(
        f"STRIPE_SECRET_KEY={os.getenv('STRIPE_SECRET_KEY', 'sk_test_abcdefghijklmnopqrstuvwxyz')}"
    )
    logger.debug("=== End environment dump ===")
    logger.info("Application started successfully on port 8000")


@app.get("/orders/{order_id}")
async def get_order(order_id: str, request: Request):
    logger.info(f"GET /orders/{order_id} from {request.client.host if request.client else 'unknown'}")
    return {"order_id": order_id, "status": "shipped"}


@app.get("/health")
async def health():
    logger.debug("Health check OK")
    # Also leak an AWS key here for the demo
    logger.debug(f"Connecting to AWS S3: {os.getenv('AWS_SECRET_ACCESS_KEY', 'AKIAIOSFODNN7EXAMPLEwJalrXUtnFEMI')}")
    return {"status": "ok"}


@app.get("/process-payment")
async def process_payment():
    # Simulate a stripe leak
    logger.info(f"Processing payment with Stripe Key: {os.getenv('STRIPE_SECRET_KEY', 'sk_test_abcdefghijklmnopqrstuvwxyz')}")
    return {"status": "payment processed"}


@app.get("/auth")
async def auth(token: str = ""):
    # Simulate a token and DB URL leak
    logger.error(f"Auth failed for token: {token}")
    logger.debug(f"Failing DB Connection: {os.getenv('DATABASE_URL', 'postgres://admin:MyP@ssw0rd123@db:5432/prod')}")
    return {"status": "auth failed"}


@app.get("/debug")
async def debug_endpoint():
    # Simulate a GitHub token leak
    logger.debug("Starting debug session. GITHUB_TOKEN=ghp_abcdefghijklmnopqrstuvwxyz123456")
    return {"status": "debug complete"}

@app.post("/admin/rotate-key")
async def rotate_key(request: Request):
    body = await request.json()
    new_key = body.get("new_key", "")
    logger.debug(f"Key rotation initiated. new_key={new_key}")
    logger.info("Key rotation completed successfully")
    return {"status": "rotated"}
