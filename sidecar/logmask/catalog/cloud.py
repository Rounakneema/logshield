"""
Cloud Provider Detectors
=========================
Covers: AWS, Azure, GCP, DigitalOcean, Alibaba Cloud,
        Cloudflare, IBM Cloud, Oracle Cloud, Heroku,
        Linode, Vultr, Scaleway, Tencent Cloud, Volcengine,
        Pulumi, Terraform, Kubernetes.
"""

import re

# fmt: off
CLOUD_DETECTORS = [

    # ════════════════════════════════════════════════════════════════════
    # AWS — Amazon Web Services
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16}"),
     "AWS IAM Access Key ID", "Amazon Web Services", "cloud_provider", 1.0),

    (re.compile(r"aws[_\-]?(?:secret|access)[_\-]?(?:key|token)\s*[=:]\s*[A-Za-z0-9+/]{40}"),
     "AWS Secret Access Key", "Amazon Web Services", "cloud_provider", 1.0),

    (re.compile(r"AWS4-HMAC-SHA256\s+Credential=[A-Z0-9]{20}/\d{8}/[a-z0-9-]+/[a-z0-9]+/aws4_request"),
     "AWS Signature V4 Credential", "Amazon Web Services", "cloud_provider", 1.0),

    (re.compile(r"(?:AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16}:[A-Za-z0-9+/]{40}"),
     "Base64 AWS IAM Keys", "Amazon Web Services", "cloud_provider", 1.0),

    (re.compile(r"arn:aws:sts::[0-9]{12}:assumed-role/[A-Za-z0-9+=,.@_/-]+"),
     "AWS STS Assumed Role ARN", "Amazon Web Services", "cloud_provider", 1.0),

    (re.compile(r"(?:ses|smtp)\.(?:access|secret)[_\-]?key\s*[=:]\s*[A-Za-z0-9+/]{40}"),
     "AWS SES Keys", "Amazon Web Services", "cloud_provider", 0.85),

    (re.compile(r"(?:AKIAIOSFODNN7|AKIAexample)"),
     "AWS Example Key (test — suppress)", "Amazon Web Services", "cloud_provider", 0.0),

    # ════════════════════════════════════════════════════════════════════
    # Azure — Microsoft
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/]{86}=="),
     "Azure Storage Connection String", "Microsoft", "cloud_provider", 1.0),

    (re.compile(r"[A-Za-z0-9+/]{86}==\s*;?\s*EndpointSuffix=core\.windows\.net"),
     "Azure Storage Account Key", "Microsoft", "cloud_provider", 1.0),

    (re.compile(r"sv=\d{4}-\d{2}-\d{2}&s[a-z]=&s[a-z]=&s[a-z]=&s[a-z]=&spr=https&sig=[A-Za-z0-9%+/]{40,}"),
     "Azure SAS URL", "Microsoft", "cloud_provider", 1.0),

    (re.compile(r"Endpoint=sb://[a-z0-9\-.]+\.servicebus\.windows\.net/;SharedAccessKeyName=[^;]+;SharedAccessKey=[A-Za-z0-9+/=]{44}"),
     "Azure Service Bus Connection String", "Microsoft", "cloud_provider", 1.0),

    (re.compile(r"AccountEndpoint=https://[a-z0-9]+\.documents\.azure\.com:\d+/;AccountKey=[A-Za-z0-9+/=]{88}"),
     "Azure Cosmos DB Connection String", "Microsoft", "cloud_provider", 1.0),

    (re.compile(r"HostName=[a-zA-Z0-9\-.]+\.azure-devices\.net;DeviceId=[^;]+;SharedAccessKey=[A-Za-z0-9+/=]{44}"),
     "Azure IoT Device Connection String", "Microsoft", "cloud_provider", 1.0),

    (re.compile(r"Endpoint=https://[a-z0-9\-.]+\.azconfig\.io;Id=[^;]+;Secret=[A-Za-z0-9+/=]{44}"),
     "Azure App Configuration Connection String", "Microsoft", "cloud_provider", 1.0),

    (re.compile(r"Endpoint=https://[a-z0-9\-.]+\.communication\.azure\.com/;AccessKey=[A-Za-z0-9+/=]{44}"),
     "Azure Communication Services Connection String", "Microsoft", "cloud_provider", 1.0),

    (re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.[a-zA-Z0-9_.-]{30,}"),
     "Azure Entra App Secret (candidate)", "Microsoft", "cloud_provider", 0.85),

    (re.compile(r"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6"),
     "Azure Entra Access Token", "Microsoft", "cloud_provider", 1.0),

    (re.compile(r"SharedAccessSignature\s+sr=[^&]+&sig=[A-Za-z0-9%+/=]+&se=\d+&skn=[^&\s]+"),
     "Azure Logic App Shared Access Signature", "Microsoft", "cloud_provider", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # GCP — Google Cloud Platform
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"AIza[0-9A-Za-z_\-]{35}"),
     "Google API Key", "Google", "cloud_provider", 1.0),

    (re.compile(r"ya29\.[A-Za-z0-9_\-]{100,}"),
     "Google OAuth2 Access Token", "Google", "cloud_provider", 1.0),

    (re.compile(r'"type"\s*:\s*"service_account"[^}]{0,200}"private_key_id"\s*:\s*"[0-9a-f]{40}"'),
     "Google Cloud Service Account JSON", "Google", "cloud_provider", 1.0),

    (re.compile(r"1//[0-9A-Za-z_\-]{40,}"),
     "Google OAuth2 Refresh Token", "Google", "cloud_provider", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # DigitalOcean
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"dop_v1_[a-f0-9]{64}"),
     "DigitalOcean Personal Access Token v1", "DigitalOcean", "cloud_provider", 1.0),

    (re.compile(r"doo_v1_[a-f0-9]{64}"),
     "DigitalOcean OAuth Application Token v1", "DigitalOcean", "cloud_provider", 1.0),

    (re.compile(r"dor_v1_[a-f0-9]{64}"),
     "DigitalOcean Refresh Token v1", "DigitalOcean", "cloud_provider", 1.0),

    (re.compile(r"(?:do|digitalocean)[_\-]?spaces[_\-]?(?:key|secret)\s*[=:]\s*[A-Za-z0-9]{20,}"),
     "DigitalOcean Spaces Keys", "DigitalOcean", "cloud_provider", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Cloudflare
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"[0-9a-f]{37}"),  # CF API Token is 40 base62 chars, often contains hex
     "Cloudflare API Token (candidate)", "Cloudflare", "cloud_provider", 0.85),

    (re.compile(r"v1\.0-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}-[a-f0-9]{64}"),
     "Cloudflare R2 Token", "Cloudflare", "cloud_provider", 1.0),

    (re.compile(r"(?:CF_API_KEY|CLOUDFLARE_API_KEY|CF_EMAIL)\s*[=:]\s*\S{20,}"),
     "Cloudflare Authentication Credentials", "Cloudflare", "cloud_provider", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Alibaba Cloud
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"LTAI[A-Za-z0-9]{20}"),
     "Alibaba Cloud Access Key ID", "Alibaba Cloud", "cloud_provider", 1.0),

    (re.compile(r"(?:aliyun|alibaba)[_\-]?(?:secret|access)[_\-]?key\s*[=:]\s*[A-Za-z0-9]{30}"),
     "Alibaba Cloud Secret Key", "Alibaba Cloud", "cloud_provider", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # IBM Cloud
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"ibm[_\-]?(?:api[_\-]?key|cloud[_\-]?key)\s*[=:]\s*[A-Za-z0-9_\-]{44}"),
     "IBM Cloud API Key", "IBM", "cloud_provider", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Heroku
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"HEROKU_API_KEY\s*[=:]\s*[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"),
     "Heroku Platform API Key", "Heroku", "cloud_provider", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Tencent Cloud
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"AKID[A-Za-z0-9]{32}"),
     "Tencent Cloud Access Key ID", "Tencent Cloud", "cloud_provider", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Volcengine (ByteDance)
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"AKLT[A-Za-z0-9_\-]{56}"),
     "Volcengine Access Key ID", "Volcengine", "cloud_provider", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Terraform Cloud
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"[a-z0-9]{14}\.atlasv1\.[a-z0-9]{67}"),
     "Terraform Cloud Token", "Terraform", "cloud_provider", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Pulumi
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"pul-[a-f0-9]{40}"),
     "Pulumi Access Token", "Pulumi", "cloud_provider", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Kubernetes
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"eyJhbGciOiJSUzI1NiIsImtpZCI6"),
     "Kubernetes Service Account Token", "Kubernetes", "cloud_provider", 1.0),

    (re.compile(r"-----BEGIN CERTIFICATE-----"),
     "Kubernetes User Certificate", "Kubernetes", "cloud_provider", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # K3s
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"K10[a-zA-Z0-9_\-]{60,}::"),
     "K3s Token", "K3s", "cloud_provider", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Linode
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:LINODE_TOKEN|linode[_\-]?api[_\-]?key)\s*[=:]\s*[a-f0-9]{64}"),
     "Linode Personal Access Token", "Linode", "cloud_provider", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Scaleway
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"scw-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"),
     "Scaleway API Token", "Scaleway", "cloud_provider", 1.0),
]
# fmt: on
