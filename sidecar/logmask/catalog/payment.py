"""
Payment & E-commerce Detectors
================================
Covers: Stripe, PayPal, Razorpay, Braintree,
        Square, Plaid, Flutterwave, Paystack,
        Shopify, Mercado Pago, Midtrans,
        WooCommerce, Xendit, GoCardless,
        Checkout.com, Adyen, PIN Payments,
        Payu, PayNow, Paddle.
"""

import re

# fmt: off
PAYMENT_DETECTORS = [

    # ════════════════════════════════════════════════════════════════════
    # Stripe
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"sk_live_[A-Za-z0-9]{24,99}"),
     "Stripe Live Secret Key", "Stripe", "payment", 1.0),

    (re.compile(r"sk_test_[A-Za-z0-9]{24,99}"),
     "Stripe Test Secret Key", "Stripe", "payment", 1.0),

    (re.compile(r"rk_live_[A-Za-z0-9]{24,99}"),
     "Stripe Live Restricted Key", "Stripe", "payment", 1.0),

    (re.compile(r"whsec_[A-Za-z0-9]{32,}"),
     "Stripe Webhook Secret", "Stripe", "payment", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # PayPal
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:PAYPAL_SECRET|paypal[_\-]?(?:secret|client[_\-]?secret))\s*[=:]\s*[A-Za-z0-9_\-]{40,80}"),
     "PayPal Client Secret", "PayPal", "payment", 0.85),

    (re.compile(r"access_token\$(?:production|sandbox)\$[A-Za-z0-9]{32,}"),
     "PayPal Access Token", "PayPal", "payment", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Razorpay
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"rzp_(?:live|test)_[A-Za-z0-9]{14}"),
     "Razorpay API Key", "Razorpay", "payment", 1.0),

    (re.compile(r"(?:RAZORPAY_KEY_SECRET|razorpay[_\-]?(?:key[_\-]?secret|secret))\s*[=:]\s*[A-Za-z0-9]{20,}"),
     "Razorpay Key Secret", "Razorpay", "payment", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Braintree
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"access_token\$(?:production|sandbox)\$[a-f0-9]+\$[a-f0-9]+"),
     "Braintree Access Token", "Braintree (PayPal)", "payment", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Square
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"sq0atp-[A-Za-z0-9_\-]{22}"),
     "Square Access Token", "Square", "payment", 1.0),

    (re.compile(r"sq0csp-[A-Za-z0-9_\-]{43}"),
     "Square Client Secret", "Square", "payment", 1.0),

    (re.compile(r"EAAAEOo[A-Za-z0-9]{80,}"),
     "Square Sandbox Access Token", "Square", "payment", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Plaid
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:PLAID_SECRET|plaid[_\-]?(?:secret|client[_\-]?secret))\s*[=:]\s*[a-f0-9]{30}"),
     "Plaid Secret", "Plaid", "payment", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Flutterwave
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"FLWSECK-[A-Za-z0-9]{32}-X"),
     "Flutterwave Secret Key", "Flutterwave", "payment", 1.0),

    (re.compile(r"FLWSECK_TEST-[A-Za-z0-9]{32}-X"),
     "Flutterwave Test Secret Key", "Flutterwave", "payment", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Paystack
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"sk_(?:live|test)_[A-Za-z0-9]{40}"),
     "Paystack Secret Key", "Paystack", "payment", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Shopify
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"shpat_[A-Za-z0-9]{32}"),
     "Shopify Staff Access Token", "Shopify", "payment", 1.0),

    (re.compile(r"shpca_[A-Za-z0-9]{32}"),
     "Shopify Custom App Access Token", "Shopify", "payment", 1.0),

    (re.compile(r"shpss_[A-Za-z0-9]{32}"),
     "Shopify Shared Secret", "Shopify", "payment", 1.0),

    (re.compile(r"shppa_[A-Za-z0-9]{32}"),
     "Shopify Partner Access Token", "Shopify", "payment", 1.0),

    (re.compile(r"shpkey_[A-Za-z0-9]{32}"),
     "Shopify API Key", "Shopify", "payment", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # WooCommerce
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"ck_[a-f0-9]{40}"),
     "WooCommerce Consumer Key", "WooCommerce", "payment", 1.0),

    (re.compile(r"cs_[a-f0-9]{40}"),
     "WooCommerce Consumer Secret", "WooCommerce", "payment", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Adyen
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"AQEyhmfxK[A-Za-z0-9]{90,}"),
     "Adyen Live API Key", "Adyen", "payment", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Xendit
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"xnd_(?:development|production)_[A-Za-z0-9]{40}"),
     "Xendit API Key", "Xendit", "payment", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # GoCardless
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"live_[A-Za-z0-9_\-]{40}"),
     "GoCardless Live Access Token", "GoCardless", "payment", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Paddle
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"pdl_snd_[A-Za-z0-9]{40}"),
     "Paddle Sandbox API Key", "Paddle", "payment", 1.0),

    (re.compile(r"pdl_(?:live|snd)_[A-Za-z0-9]{40}"),
     "Paddle API Key", "Paddle", "payment", 1.0),
]
# fmt: on
