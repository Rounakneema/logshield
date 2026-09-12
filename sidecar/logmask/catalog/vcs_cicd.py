"""
Version Control & CI/CD Detectors
====================================
Covers: GitHub, GitLab, Bitbucket, Gitea,
        npm, PyPI, NuGet, RubyGems, Docker Hub,
        JFrog Artifactory, CircleCI, Travis CI,
        Buildkite, Bitrise, Jenkins, Nx Cloud,
        LaunchDarkly, SonarQube, Snyk.
"""

import re

# fmt: off
VCS_CICD_DETECTORS = [

    # ════════════════════════════════════════════════════════════════════
    # GitHub
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"ghp_[A-Za-z0-9]{36}"),
     "GitHub Personal Access Token (classic)", "GitHub", "version_control_platform", 1.0),

    (re.compile(r"github_pat_[A-Za-z0-9_]{82}"),
     "GitHub Fine-Grained PAT", "GitHub", "version_control_platform", 1.0),

    (re.compile(r"gho_[A-Za-z0-9]{36}"),
     "GitHub OAuth Token", "GitHub", "version_control_platform", 1.0),

    (re.compile(r"ghu_[A-Za-z0-9]{36}"),
     "GitHub User-to-Server Token", "GitHub", "version_control_platform", 1.0),

    (re.compile(r"ghs_[A-Za-z0-9]{36}"),
     "GitHub Server-to-Server Token", "GitHub", "version_control_platform", 1.0),

    (re.compile(r"ghr_[A-Za-z0-9]{36}"),
     "GitHub Refresh Token", "GitHub", "version_control_platform", 1.0),

    (re.compile(r"ghx_[A-Za-z0-9]{36}"),
     "GitHub Enterprise Token", "GitHub", "version_control_platform", 1.0),

    (re.compile(r"v1\.[\da-f]{40}"),
     "GitHub App Installation Token", "GitHub", "version_control_platform", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # GitLab
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"glpat-[A-Za-z0-9_\-]{20}"),
     "GitLab Personal Access Token", "GitLab", "version_control_platform", 1.0),

    (re.compile(r"gldt-[A-Za-z0-9_\-]{20}"),
     "GitLab Deploy Token", "GitLab", "version_control_platform", 1.0),

    (re.compile(r"glrt-[A-Za-z0-9_\-]{20}"),
     "GitLab Runner Authentication Token", "GitLab", "ci_cd", 1.0),

    (re.compile(r"glag-[A-Za-z0-9_\-]{20}"),
     "GitLab Agent Kubernetes Token", "GitLab", "version_control_platform", 1.0),

    (re.compile(r"glsoat-[A-Za-z0-9_\-]{20}"),
     "GitLab SCIM Token", "GitLab", "version_control_platform", 1.0),

    (re.compile(r"glft-[A-Za-z0-9_\-]{20}"),
     "GitLab Feed Token", "GitLab", "version_control_platform", 1.0),

    (re.compile(r"GR1348941[A-Za-z0-9_\-]{20}"),
     "GitLab CI/CD Job Token", "GitLab", "version_control_platform", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Bitbucket
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"ATBB[A-Za-z0-9]{32}"),
     "Bitbucket Repository Access Token", "Atlassian", "version_control_platform", 1.0),

    (re.compile(r"(?:bitbucket[_\-]?app[_\-]?password|BITBUCKET_APP_PASSWORD)\s*[=:]\s*[A-Za-z0-9+/=]{20,}"),
     "Bitbucket App Password", "Bitbucket", "version_control_platform", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Gitea
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"gta_[A-Za-z0-9_]{40}"),
     "Gitea Access Token", "Gitea", "version_control_platform", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # npm
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"npm_[A-Za-z0-9]{36}"),
     "npm Access Token", "npm", "package_registry", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # PyPI
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"pypi-AgEIcHlwaS5vcmcC[A-Za-z0-9_\-]{60,}"),
     "PyPI API Token", "Python Package Index", "package_registry", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # NuGet
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"oy2[A-Za-z0-9_\-]{43}"),
     "NuGet API Key", "NuGet", "package_registry", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # RubyGems
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"rubygems_[A-Za-z0-9]{48}"),
     "RubyGems API Key", "RubyGems", "package_registry", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Docker Hub
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:DOCKER_PASSWORD|docker[_\-]?(?:token|password|pat))\s*[=:]\s*\S{20,}"),
     "Docker Hub Credentials", "Docker", "package_registry", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # JFrog Artifactory
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:AKCp|AKCb)[A-Za-z0-9]{70}"),
     "JFrog Artifactory Access Token", "JFrog", "package_registry", 1.0),

    (re.compile(r"cmVmdGtuOjA[A-Za-z0-9+/=]{60,}"),
     "JFrog Artifactory Reference Token", "JFrog", "package_registry", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # CircleCI
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"CCIPAT_[A-Za-z0-9]{40}"),
     "CircleCI Personal Access Token", "CircleCI", "ci_cd", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Travis CI
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:TRAVIS_TOKEN|travis[_\-]?(?:token|api[_\-]?key))\s*[=:]\s*[A-Za-z0-9_\-]{20,}"),
     "Travis CI Personal Token", "Travis", "ci_cd", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Buildkite
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"bkua_[A-Za-z0-9]{40}"),
     "Buildkite Agent Token", "Buildkite", "ci_cd", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Bitrise
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:BITRISE_API_TOKEN|bitrise[_\-]?(?:token|api[_\-]?key))\s*[=:]\s*[A-Za-z0-9_\-]{86}"),
     "Bitrise Personal Access Token", "Bitrise", "ci_cd", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Nx Cloud
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"nxcloud-[A-Za-z0-9]{40}"),
     "Nx Cloud Token", "Nx Cloud", "ci_cd", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # SonarQube
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"sqa_[A-Za-z0-9]{40}"),
     "SonarQube User Token", "SonarQube", "code_analysis", 1.0),

    (re.compile(r"sqp_[A-Za-z0-9]{40}"),
     "SonarQube Project Analysis Token", "SonarQube", "code_analysis", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Snyk
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"),
     "Snyk API Key (UUID format)", "Snyk", "code_analysis", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Doppler
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"dp\.pt\.[A-Za-z0-9]{40}"),
     "Doppler Personal Access Token", "Doppler", "secret_management", 1.0),

    (re.compile(r"dp\.sa\.[A-Za-z0-9]{40}"),
     "Doppler Service Account Token", "Doppler", "secret_management", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # HashiCorp Vault
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"hvs\.[A-Za-z0-9]{24,}"),
     "HashiCorp Vault Service Token", "HashiCorp", "secret_management", 1.0),

    (re.compile(r"hvb\.[A-Za-z0-9]{24,}"),
     "HashiCorp Vault Batch Token", "HashiCorp", "secret_management", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Octopus Deploy
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"API-[A-Za-z0-9]{26}"),
     "Octopus Deploy API Key", "Octopus Deploy", "ci_cd", 1.0),
]
# fmt: on
