import logging
import re

import requests

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


def parse_repository_url(url: str):
    """
    Extract owner and repository name from a GitHub URL.
    """
    pattern = r"^https?://github\.com/([^/]+)/([^/#?]+?)/?$"

    match = re.match(pattern, url.strip())

    if not match:
        return None

    owner = match.group(1)
    repo = match.group(2)

    if repo.endswith(".git"):
        repo = repo[:-4]

    return owner, repo


def get_repository(owner: str, repo: str):
    url = f"{GITHUB_API}/repos/{owner}/{repo}"

    try:
        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()

        return response.json()

    except requests.RequestException:
        logger.exception(
            "Failed to fetch GitHub repository %s/%s",
            owner,
            repo
        )

        return None


def get_latest_release(owner: str, repo: str):
    url = (
        f"{GITHUB_API}/repos/"
        f"{owner}/{repo}/releases/latest"
    )

    try:
        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()

        return response.json()

    except requests.RequestException:
        logger.exception(
            "Failed to fetch latest release for %s/%s",
            owner,
            repo
        )

        return None