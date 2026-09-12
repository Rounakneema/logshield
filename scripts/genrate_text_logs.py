#!/usr/bin/env python3

"""
=============================================================
 LOGSHIELD MASSIVE LOG GENERATOR
=============================================================

Generates realistic Kubernetes / microservice-style logs.

OUTPUT:
    logs.txt
    ground_truth.txt

The generator creates:

    NORMAL
    SECRET
    PII
    HARD_NEGATIVE
    ADVERSARIAL

Secret categories:

    PASSWORD
    API_KEY
    AWS_CREDENTIAL
    GITHUB_TOKEN
    JWT
    DATABASE_CREDENTIAL
    REDIS_CREDENTIAL
    AUTHORIZATION_TOKEN
    PRIVATE_KEY
    GENERIC_TOKEN
    PII

Hard negatives:

    UUID
    TRACE_ID
    SHA256
    CHECKSUM
    BUILD_ID
    HIGH_ENTROPY_ID
    RANDOM_IDENTIFIER

Adversarial cases:

    BASE64
    URL_ENCODED
    ESCAPED
    WHITESPACE_SPLIT
    JSON_EMBEDDED
    MULTIFIELD_SPLIT

All secrets are synthetic and non-functional.

=============================================================
"""

import argparse
import base64
import hashlib
import json
import random
import secrets
import string
import time
import uuid

from datetime import datetime, timezone
from urllib.parse import quote


# ============================================================
# GLOBAL CONFIGURATION
# ============================================================

SERVICES = [
    "api-gateway",
    "auth-service",
    "user-service",
    "payment-service",
    "order-service",
    "inventory-service",
    "notification-service",
    "search-service",
    "analytics-service",
    "recommendation-service",
    "worker",
    "scheduler",
]

NAMESPACES = [
    "production",
    "staging",
    "payments",
    "backend",
    "frontend",
    "analytics",
]

REGIONS = [
    "ap-south-1",
    "ap-south-2",
    "us-east-1",
    "us-west-2",
    "eu-west-1",
]

METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
]

ENDPOINTS = [
    "/api/users",
    "/api/users/{id}",
    "/api/orders",
    "/api/orders/{id}",
    "/api/products",
    "/api/products/{id}",
    "/api/payment",
    "/api/checkout",
    "/api/login",
    "/api/logout",
    "/api/search",
    "/api/health",
    "/api/metrics",
]

DATABASES = [
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
]

USER_AGENTS = [
    "Mozilla/5.0",
    "curl/8.5.0",
    "python-requests/2.32",
    "okhttp/4.12",
    "mobile-app/7.2",
]

ERROR_MESSAGES = [
    "connection timeout",
    "connection refused",
    "database unavailable",
    "upstream timeout",
    "serialization failure",
    "invalid request",
    "authentication failed",
    "rate limit exceeded",
    "request validation failed",
    "service unavailable",
]


# ============================================================
# RANDOM UTILITIES
# ============================================================

def random_hex(length=32):
    """
    Generate hexadecimal identifier.
    """
    return secrets.token_hex((length + 1) // 2)[:length]


def random_alphanumeric(length=32):
    """
    Generate random alphanumeric value.
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )


def random_digits(length=10):
    return "".join(
        random.choice(string.digits)
        for _ in range(length)
    )


def now_timestamp():
    return datetime.now(
        timezone.utc
    ).isoformat(
        timespec="milliseconds"
    )


def random_ip():
    return ".".join(
        str(random.randint(1, 254))
        for _ in range(4)
    )


def random_email():
    names = [
        "alice",
        "bob",
        "charlie",
        "david",
        "emma",
        "frank",
        "user",
        "customer",
    ]

    return (
        random.choice(names)
        + str(random.randint(1, 99999))
        + "@example.test"
    )


def random_uuid():
    return str(uuid.uuid4())


def random_trace_id():
    return random_hex(32)


def random_span_id():
    return random_hex(16)


def random_request_id():
    return "req_" + random_hex(24)


def random_order_id():
    return "ord_" + random_hex(12)


def random_customer_id():
    return "cust_" + random_digits(10)


# ============================================================
# SYNTHETIC SECRET GENERATORS
# ============================================================

def generate_password():
    return "LS_TEST_PASSWORD_" + random_alphanumeric(24)


def generate_api_key():
    return "sk-test-" + random_alphanumeric(32)


def generate_aws_access_key():
    return "AKIA" + random_alphanumeric(16).upper()


def generate_aws_secret():
    return random_alphanumeric(40)


def generate_github_token():
    return "ghp_test_" + random_alphanumeric(36)


def generate_generic_token():
    return "token_" + random_alphanumeric(48)


def generate_jwt():
    """
    Creates a JWT-shaped synthetic token.
    It is intentionally non-functional.
    """

    header = {
        "alg": "HS256",
        "typ": "JWT",
    }

    payload = {
        "sub": str(random.randint(1000, 999999)),
        "role": random.choice([
            "user",
            "admin",
            "service",
        ]),
        "iat": int(time.time()),
    }

    def encode(obj):

        raw = json.dumps(
            obj,
            separators=(",", ":")
        ).encode()

        return base64.urlsafe_b64encode(
            raw
        ).decode().rstrip("=")

    return (
        encode(header)
        + "."
        + encode(payload)
        + "."
        + random_alphanumeric(32)
    )


def generate_database_url():

    password = generate_password()

    return (
        "postgresql://"
        "app_user:"
        + password
        + "@postgres.production.svc.cluster.local:"
        "5432/application"
    )


def generate_redis_url():

    password = generate_password()

    return (
        "redis://:"
        + password
        + "@redis.production.svc.cluster.local:"
        "6379/0"
    )


def generate_private_key():

    # Synthetic marker, NOT a usable private key.
    body = base64.b64encode(
        random_alphanumeric(512).encode()
    ).decode()

    return (
        "-----BEGIN TEST PRIVATE KEY-----"
        + body
        + "-----END TEST PRIVATE KEY-----"
    )


# ============================================================
# HARD NEGATIVES
# ============================================================

def generate_sha256():

    return hashlib.sha256(
        random_alphanumeric(64).encode()
    ).hexdigest()


def generate_md5():

    return hashlib.md5(
        random_alphanumeric(64).encode()
    ).hexdigest()


def generate_high_entropy_identifier():

    """
    High entropy but intentionally NOT a secret.

    This is critical for testing whether
    entropy alone creates false positives.
    """

    return secrets.token_urlsafe(64)


def generate_build_id():

    return (
        "build-"
        + random_hex(20)
    )


def generate_commit_hash():

    return random_hex(40)


def generate_checksum():

    return hashlib.sha1(
        random_alphanumeric(40).encode()
    ).hexdigest()


# ============================================================
# KUBERNETES METADATA
# ============================================================

def kubernetes_metadata():

    service = random.choice(SERVICES)
    namespace = random.choice(NAMESPACES)

    pod = (
        service
        + "-"
        + random_hex(5)
        + "-"
        + random_hex(5)
    )

    return {
        "service": service,
        "namespace": namespace,
        "pod": pod,
        "container": service,
        "node": "node-" + str(
            random.randint(1, 30)
        ),
        "region": random.choice(REGIONS),
    }


# ============================================================
# NORMAL LOG GENERATION
# ============================================================

def normal_log():

    meta = kubernetes_metadata()

    event = random.choice([
        "http",
        "database",
        "cache",
        "queue",
        "startup",
        "health",
        "worker",
        "deployment",
        "authentication",
        "error",
    ])

    if event == "http":

        return (
            "HTTP request completed "
            "method="
            + random.choice(METHODS)
            + " path="
            + random.choice(ENDPOINTS)
            + " status="
            + str(random.choice([
                200,
                200,
                200,
                201,
                204,
                400,
                404,
                429,
            ]))
            + " duration_ms="
            + str(random.randint(1, 950))
            + " request_id="
            + random_request_id()
            + " trace_id="
            + random_trace_id()
        )

    if event == "database":

        return (
            "Database query completed "
            "database="
            + random.choice(DATABASES)
            + " query_time_ms="
            + str(random.randint(1, 400))
            + " rows="
            + str(random.randint(0, 1000))
            + " connection_pool="
            + str(random.randint(1, 50))
        )

    if event == "cache":

        return (
            "Cache operation completed "
            "operation="
            + random.choice([
                "GET",
                "SET",
                "DELETE",
            ])
            + " key=user:"
            + random_digits(8)
            + " hit="
            + str(random.choice([
                True,
                False,
            ]))
            + " latency_ms="
            + str(random.randint(1, 30))
        )

    if event == "queue":

        return (
            "Queue message processed "
            "queue="
            + random.choice([
                "orders",
                "payments",
                "notifications",
                "analytics",
            ])
            + " message_id="
            + random_hex(20)
            + " processing_ms="
            + str(random.randint(1, 2000))
        )

    if event == "startup":

        return (
            "Application started "
            "version="
            + str(random.randint(1, 9))
            + "."
            + str(random.randint(0, 20))
            + "."
            + str(random.randint(0, 30))
            + " environment="
            + random.choice([
                "production",
                "staging",
                "test",
            ])
        )

    if event == "health":

        return (
            "Health check passed "
            "cpu_percent="
            + str(round(
                random.uniform(1, 95),
                2
            ))
            + " memory_percent="
            + str(round(
                random.uniform(5, 90),
                2
            ))
            + " uptime_seconds="
            + str(random.randint(
                10,
                500000
            ))
        )

    if event == "worker":

        return (
            "Background job completed "
            "job_id="
            + random_request_id()
            + " duration_ms="
            + str(random.randint(
                10,
                10000
            ))
            + " attempt="
            + str(random.randint(1, 3))
        )

    if event == "deployment":

        return (
            "Deployment rollout progressing "
            "deployment="
            + random.choice(SERVICES)
            + " replicas="
            + str(random.randint(1, 20))
            + " ready="
            + str(random.randint(0, 20))
        )

    if event == "authentication":

        return (
            "User authentication completed "
            "user_id="
            + random_digits(7)
            + " method="
            + random.choice([
                "password",
                "oauth",
                "sso",
                "mfa",
            ])
        )

    return (
        "Request failed "
        "error="
        + random.choice(ERROR_MESSAGES)
        + " request_id="
        + random_request_id()
    )


# ============================================================
# SECRET LOG GENERATION
# ============================================================

def secret_log():

    secret_type = random.choice([
        "PASSWORD",
        "API_KEY",
        "AWS",
        "GITHUB",
        "JWT",
        "DATABASE",
        "REDIS",
        "AUTHORIZATION",
        "PRIVATE_KEY",
        "GENERIC_TOKEN",
        "PII",
    ])

    if secret_type == "PASSWORD":

        secret = generate_password()

        return (
            "authentication configuration loaded "
            "username=service_account "
            "password="
            + secret,
            secret_type,
        )

    if secret_type == "API_KEY":

        secret = generate_api_key()

        return (
            "external service configuration loaded "
            "provider="
            + random.choice([
                "payments",
                "maps",
                "email",
                "analytics",
            ])
            + " api_key="
            + secret,
            secret_type,
        )

    if secret_type == "AWS":

        access = generate_aws_access_key()
        secret = generate_aws_secret()

        return (
            "cloud client initialized "
            "AWS_ACCESS_KEY_ID="
            + access
            + " AWS_SECRET_ACCESS_KEY="
            + secret
            + " region="
            + random.choice(REGIONS),
            secret_type,
        )

    if secret_type == "GITHUB":

        secret = generate_github_token()

        return (
            "repository client initialized "
            "github_token="
            + secret,
            secret_type,
        )

    if secret_type == "JWT":

        secret = generate_jwt()

        return (
            "authorization header received "
            "Authorization=Bearer "
            + secret
            + " request_id="
            + random_request_id(),
            secret_type,
        )

    if secret_type == "DATABASE":

        secret = generate_database_url()

        return (
            "database connection failed "
            "connection_string="
            + secret
            + " retry="
            + str(random.randint(1, 5)),
            secret_type,
        )

    if secret_type == "REDIS":

        secret = generate_redis_url()

        return (
            "redis connection failed "
            "redis_url="
            + secret,
            secret_type,
        )

    if secret_type == "AUTHORIZATION":

        secret = generate_jwt()

        return (
            "request headers "
            "Authorization: Bearer "
            + secret
            + " User-Agent="
            + random.choice(USER_AGENTS),
            secret_type,
        )

    if secret_type == "PRIVATE_KEY":

        secret = generate_private_key()

        return (
            "certificate initialization failed "
            + secret,
            secret_type,
        )

    if secret_type == "PII":

        return (
            "customer validation "
            "email="
            + random_email()
            + " phone=+1-555-"
            + random_digits(7)
            + " customer_id="
            + random_customer_id(),
            secret_type,
        )

    secret = generate_generic_token()

    return (
        "temporary service credential "
        "token="
        + secret,
        "GENERIC_TOKEN",
    )


# ============================================================
# HARD NEGATIVE LOG GENERATION
# ============================================================

def hard_negative_log():

    kind = random.choice([
        "UUID",
        "TRACE_ID",
        "SHA256",
        "CHECKSUM",
        "BUILD_ID",
        "ENTROPY",
        "COMMIT",
        "RANDOM_IDENTIFIER",
    ])

    if kind == "UUID":

        return (
            "resource created "
            "resource_id="
            + random_uuid(),
            kind,
        )

    if kind == "TRACE_ID":

        return (
            "distributed tracing metadata "
            "trace_id="
            + random_trace_id()
            + " span_id="
            + random_span_id(),
            kind,
        )

    if kind == "SHA256":

        return (
            "artifact verification completed "
            "sha256="
            + generate_sha256(),
            kind,
        )

    if kind == "CHECKSUM":

        return (
            "payload checksum calculated "
            "checksum="
            + generate_checksum(),
            kind,
        )

    if kind == "BUILD_ID":

        return (
            "build artifact deployed "
            "build_id="
            + generate_build_id(),
            kind,
        )

    if kind == "COMMIT":

        return (
            "source revision deployed "
            "commit="
            + generate_commit_hash(),
            kind,
        )

    if kind == "ENTROPY":

        return (
            "cache identifier generated "
            "cache_id="
            + generate_high_entropy_identifier(),
            kind,
        )

    return (
        "correlation metadata "
        "identifier="
        + random_alphanumeric(64),
        kind,
    )


# ============================================================
# ADVERSARIAL LOG GENERATION
# ============================================================

def adversarial_log():

    secret = generate_password()

    attack = random.choice([
        "BASE64",
        "URL_ENCODED",
        "ESCAPED",
        "WHITESPACE_SPLIT",
        "JSON",
        "MULTIFIELD",
    ])

    if attack == "BASE64":

        encoded = base64.b64encode(
            secret.encode()
        ).decode()

        return (
            "diagnostic payload received "
            "encoding=base64 "
            "payload="
            + encoded,
            attack,
        )

    if attack == "URL_ENCODED":

        encoded = quote(
            secret,
            safe=""
        )

        return (
            "redirect diagnostic "
            "url=https://example.test/debug?"
            "credential="
            + encoded,
            attack,
        )

    if attack == "ESCAPED":

        modified = secret.replace(
            "_",
            "\\u005f"
        )

        return (
            "escaped authentication value "
            "credential="
            + modified,
            attack,
        )

    if attack == "WHITESPACE_SPLIT":

        midpoint = len(secret) // 2

        modified = (
            secret[:midpoint]
            + " "
            + secret[midpoint:]
        )

        return (
            "diagnostic credential "
            "password="
            + modified,
            attack,
        )

    if attack == "JSON":

        body = json.dumps({
            "username": "service",
            "credentials": {
                "password": secret
            }
        })

        return (
            "request processing failed "
            "body="
            + body,
            attack,
        )

    midpoint = len(secret) // 2

    return (
        "multipart credential "
        "credential_part_a="
        + secret[:midpoint]
        + " credential_part_b="
        + secret[midpoint:],
        attack,
    )


# ============================================================
# MULTILINE EXCEPTIONS
# ============================================================

def multiline_exception():

    password = generate_password()

    lines = [
        "ERROR request processing failed",
        "Traceback (most recent call last):",
        '  File "/app/payment.py", line 182, in process',
        "    connection.authenticate()",
        "AuthenticationError: invalid credentials",
        "debug_context=password=" + password,
    ]

    return "\n".join(lines), "PASSWORD"


# ============================================================
# REALISTIC LOG FORMAT
# ============================================================

def render_log(message):

    meta = kubernetes_metadata()

    timestamp = now_timestamp()

    level = random.choice([
        "INFO",
        "INFO",
        "INFO",
        "DEBUG",
        "WARN",
        "ERROR",
    ])

    service = meta["service"]

    pid = random.randint(
        100,
        50000
    )

    thread = random.randint(
        1,
        32
    )

    return (
        timestamp
        + " "
        + level
        + " "
        + service
        + " "
        + "pid="
        + str(pid)
        + " thread="
        + str(thread)
        + " namespace="
        + meta["namespace"]
        + " pod="
        + meta["pod"]
        + " node="
        + meta["node"]
        + " "
        + message
    )


# ============================================================
# GENERATE ONE SAMPLE
# ============================================================

def generate_sample():

    """
    Distribution:

        68% NORMAL
        15% SECRET
        7% PII
        7% HARD_NEGATIVE
        3% ADVERSARIAL

    The exact distribution is deliberately configurable
    below.
    """

    r = random.random()

    if r < 0.68:

        message = normal_log()

        return (
            render_log(message),
            "NORMAL",
            "NONE",
        )

    if r < 0.83:

        message, secret_type = secret_log()

        return (
            render_log(message),
            "SECRET",
            secret_type,
        )

    if r < 0.90:

        message = (
            "customer validation "
            "email="
            + random_email()
            + " phone=+1-555-"
            + random_digits(7)
            + " customer_id="
            + random_customer_id()
        )

        return (
            render_log(message),
            "PII",
            "PII",
        )

    if r < 0.97:

        message, negative_type = (
            hard_negative_log()
        )

        return (
            render_log(message),
            "HARD_NEGATIVE",
            negative_type,
        )

    message, attack_type = (
        adversarial_log()
    )

    return (
        render_log(message),
        "ADVERSARIAL",
        attack_type,
    )


# ============================================================
# GENERATOR
# ============================================================

def generate_dataset(
    log_file,
    ground_truth_file,
    target_gb=None,
    target_lines=None,
    seed=None,
):

    if seed is not None:
        random.seed(seed)

    target_bytes = None

    if target_gb is not None:

        target_bytes = (
            target_gb
            * 1024
            * 1024
            * 1024
        )

    total_bytes = 0
    total_lines = 0

    counters = {
        "NORMAL": 0,
        "SECRET": 0,
        "PII": 0,
        "HARD_NEGATIVE": 0,
        "ADVERSARIAL": 0,
    }

    start_time = time.time()

    with open(
        log_file,
        "w",
        encoding="utf-8",
        buffering=4 * 1024 * 1024,
    ) as logs, open(
        ground_truth_file,
        "w",
        encoding="utf-8",
        buffering=4 * 1024 * 1024,
    ) as truth:

        # Header for ground truth
        truth.write(
            "LINE_ID|LABEL|TYPE\n"
        )

        while True:

            if (
                target_lines is not None
                and total_lines >= target_lines
            ):
                break

            if (
                target_bytes is not None
                and total_bytes >= target_bytes
            ):
                break

            log, label, sample_type = (
                generate_sample()
            )

            # ------------------------------------------------
            # Multiline samples are intentionally avoided here
            # so that one physical line corresponds to one
            # ground-truth record.
            # ------------------------------------------------

            log = log.replace(
                "\n",
                "\\n"
            )

            logs.write(
                log + "\n"
            )

            line_size = (
                len(
                    log.encode("utf-8")
                )
                + 1
            )

            total_bytes += line_size
            total_lines += 1

            counters[label] += 1

            truth.write(
                str(total_lines)
                + "|"
                + label
                + "|"
                + sample_type
                + "\n"
            )

            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            if total_lines % 100_000 == 0:

                elapsed = (
                    time.time()
                    - start_time
                )

                rate = (
                    total_lines
                    / elapsed
                    if elapsed > 0
                    else 0
                )

                gb = (
                    total_bytes
                    / (1024 ** 3)
                )

                print(
                    "\r"
                    f"Lines: {total_lines:,} | "
                    f"Size: {gb:.3f} GB | "
                    f"Rate: {rate:,.0f} lines/s",
                    end="",
                    flush=True,
                )

    elapsed = (
        time.time()
        - start_time
    )

    print()
    print()
    print("=" * 70)
    print("LOGSHIELD DATASET GENERATION COMPLETE")
    print("=" * 70)

    print(
        f"Total lines : {total_lines:,}"
    )

    print(
        f"Total size  : "
        f"{total_bytes / (1024 ** 3):.3f} GB"
    )

    print(
        f"Time        : "
        f"{elapsed:.2f} seconds"
    )

    print(
        f"Throughput  : "
        f"{total_lines / elapsed:,.0f} lines/sec"
    )

    print()
    print("Distribution:")
    print()

    for label, count in counters.items():

        percentage = (
            count / total_lines * 100
            if total_lines
            else 0
        )

        print(
            f"{label:16} "
            f"{count:12,} "
            f"({percentage:6.2f}%)"
        )

    print()
    print("Output:")
    print(
        f"  Logs       : {log_file}"
    )
    print(
        f"  Groundtruth: {ground_truth_file}"
    )


# ============================================================
# CLI
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Generate massive synthetic "
            "LogShield security logs."
        )
    )

    parser.add_argument(
        "--gb",
        type=float,
        help=(
            "Target approximate output "
            "size in GB."
        ),
    )

    parser.add_argument(
        "--lines",
        type=int,
        help=(
            "Generate an exact number "
            "of log lines."
        ),
    )

    parser.add_argument(
        "--logs",
        default="logs.txt",
        help="Output log file.",
    )

    parser.add_argument(
        "--truth",
        default="ground_truth.txt",
        help="Ground truth file.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility.",
    )

    args = parser.parse_args()

    if args.gb is None and args.lines is None:

        parser.error(
            "Specify either --gb or --lines"
        )

    if args.gb is not None and args.gb <= 0:

        parser.error(
            "--gb must be greater than zero"
        )

    if args.lines is not None and args.lines <= 0:

        parser.error(
            "--lines must be greater than zero"
        )

    generate_dataset(
        log_file=args.logs,
        ground_truth_file=args.truth,
        target_gb=args.gb,
        target_lines=args.lines,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()