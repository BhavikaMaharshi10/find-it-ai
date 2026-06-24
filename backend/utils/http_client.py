"""Minimal HTTP helper using stdlib only (no extra dependencies)."""
import json
import urllib.error
import urllib.request
from typing import Any

DEFAULT_HEADERS = {
    "User-Agent": "FindItAI/1.0 (job-sync; +https://github.com/finditai)",
    "Accept": "application/json",
}


def fetch_json(url: str, timeout: int = 30) -> Any:
    request = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))
