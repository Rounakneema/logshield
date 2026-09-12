"""
Messaging & Communication Detectors
======================================
Covers: Slack (all token types), Telegram Bot,
        Discord (Webhook + Bot Token), Twilio,
        SendGrid, Mailgun, Mailchimp, Postmark,
        Resend, Mailjet, PubNub, Pusher,
        MessageBird/Bird, Vonage/Nexmo, Line,
        Beamer, Zoom, Webex, Zulip, Intercom,
        Teams Webhook, Bandwidth, Livekit,
        Daily, Plivo.
"""

import re

# fmt: off
MESSAGING_DETECTORS = [

    # ════════════════════════════════════════════════════════════════════
    # Slack
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"xoxb-[0-9]+-[0-9]+-[a-zA-Z0-9]+"),
     "Slack Bot Token", "Slack", "messaging", 1.0),

    (re.compile(r"xoxp-[0-9]+-[0-9]+-[0-9]+-[a-f0-9]+"),
     "Slack User OAuth Token", "Slack", "messaging", 1.0),

    (re.compile(r"xoxa-[0-9]+-[0-9]+-[0-9]+-[a-f0-9]+"),
     "Slack App-Level Token (deprecated)", "Slack", "messaging", 1.0),

    (re.compile(r"xoxs-[0-9]+-[0-9]+-[0-9]+-[a-f0-9]+"),
     "Slack Legacy Session Token", "Slack", "messaging", 1.0),

    (re.compile(r"xapp-\d-[A-Z0-9]+-[0-9]+-[a-f0-9]+"),
     "Slack App Token", "Slack", "messaging", 1.0),

    (re.compile(r"xwfp-[0-9]+-[0-9]+-[a-zA-Z0-9]+"),
     "Slack Workflow Step Token", "Slack", "messaging", 1.0),

    (re.compile(r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+"),
     "Slack Webhook URL", "Slack", "messaging", 1.0),

    (re.compile(r"https://hooks\.slack\.com/workflows/T[A-Z0-9]+/A[A-Z0-9]+/[0-9]+/[A-Za-z0-9]+"),
     "Slack Workflow Webhook URL", "Slack", "messaging", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Telegram
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"\d{9,10}:[A-Za-z0-9_\-]{35}"),
     "Telegram Bot Token", "Telegram", "messaging", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Discord
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"https://discord\.com/api/webhooks/\d{17,20}/[A-Za-z0-9_\-]{60,}"),
     "Discord Webhook URL", "Discord", "messaging", 1.0),

    (re.compile(r"https://discordapp\.com/api/webhooks/\d{17,20}/[A-Za-z0-9_\-]{60,}"),
     "Discord Webhook URL (legacy)", "Discord", "messaging", 1.0),

    (re.compile(r"(?:DISCORD_BOT_TOKEN|discord[_\-]?(?:bot[_\-]?)?token)\s*[=:]\s*[A-Za-z0-9_\-.]{59,100}"),
     "Discord Bot Token", "Discord", "messaging", 0.85),

    (re.compile(r"MTI[0-9A-Za-z_\-]{60,}"),
     "Discord Bot Token (raw)", "Discord", "messaging", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Twilio
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"AC[a-f0-9]{32}"),
     "Twilio Account SID", "Twilio", "messaging", 1.0),

    (re.compile(r"SK[a-f0-9]{32}"),
     "Twilio API Key SID", "Twilio", "messaging", 1.0),

    (re.compile(r"(?:TWILIO_AUTH_TOKEN|twilio[_\-]?auth[_\-]?token)\s*[=:]\s*[a-f0-9]{32}"),
     "Twilio Auth Token", "Twilio", "messaging", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # SendGrid
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}"),
     "SendGrid API Key", "SendGrid", "messaging", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Mailgun
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"key-[a-z0-9]{32}"),
     "Mailgun API Key", "Mailgun", "messaging", 1.0),

    (re.compile(r"mailgun[_\-]?(?:api[_\-]?key|private[_\-]?key)\s*[=:]\s*key-[a-z0-9]{32}"),
     "Mailgun Private Key", "Mailgun", "messaging", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Mailchimp
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"[a-f0-9]{32}-us\d+"),
     "Mailchimp API Key", "Mailchimp", "messaging", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Postmark
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"),
     "Postmark Server Token (UUID format)", "Postmark", "messaging", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Resend
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"re_[A-Za-z0-9_]{30,}"),
     "Resend API Key", "Resend", "messaging", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Mailjet
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:mailjet[_\-]?(?:api[_\-]?key|secret[_\-]?key))\s*[=:]\s*[a-f0-9]{32}"),
     "Mailjet API / Secret Key", "Mailjet", "messaging", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # PubNub
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"pub-c-[0-9a-f\-]{36}"),
     "PubNub Publish Key", "PubNub", "messaging", 1.0),

    (re.compile(r"sub-c-[0-9a-f\-]{36}"),
     "PubNub Subscribe Key", "PubNub", "messaging", 1.0),

    (re.compile(r"sec-c-[A-Za-z0-9+/=]{40}"),
     "PubNub Secret Key", "PubNub", "messaging", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Pusher
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:PUSHER_APP_SECRET|pusher[_\-]?(?:secret|app[_\-]?secret))\s*[=:]\s*[a-f0-9]{20}"),
     "Pusher App Secret", "Pusher", "messaging", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # MessageBird / Bird
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:MESSAGEBIRD_API_KEY|messagebird[_\-]?api[_\-]?key)\s*[=:]\s*[A-Za-z0-9]{25}"),
     "MessageBird API Key", "MessageBird", "messaging", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Vonage / Nexmo
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:VONAGE_API_SECRET|NEXMO_API_SECRET|nexmo[_\-]?api[_\-]?secret)\s*[=:]\s*[a-zA-Z0-9]{16}"),
     "Vonage API Secret", "Vonage", "messaging", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Zoom
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:ZOOM_SECRET_TOKEN|ZOOM_WEBHOOK_SECRET_TOKEN)\s*[=:]\s*[A-Za-z0-9+/=]{40}"),
     "Zoom Webhook Secret", "Zoom", "messaging", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Microsoft Teams Incoming Webhook
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"https://[a-zA-Z0-9.]+\.webhook\.office\.com/webhookb2/[A-Za-z0-9\-@]+/IncomingWebhook/[A-Za-z0-9]+/[A-Za-z0-9\-]+"),
     "Microsoft Teams Incoming Webhook URL", "Microsoft", "messaging", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Intercom
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:INTERCOM_ACCESS_TOKEN|intercom[_\-]?(?:access[_\-]?token|api[_\-]?key))\s*[=:]\s+dG9rO[A-Za-z0-9+/=]{60,}"),
     "Intercom Access Token", "Intercom", "messaging", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # LiveKit
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:LIVEKIT_API_SECRET|livekit[_\-]?api[_\-]?secret)\s*[=:]\s*[A-Za-z0-9+/=]{40,}"),
     "LiveKit API Secret", "LiveKit", "messaging", 0.85),
]
# fmt: on
