from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential


_RETRYABLE_STATUS = {429, 500, 502, 503, 504}
DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_USER_AGENT = "delvn/0.1.0"


def _should_retry(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in _RETRYABLE_STATUS
    return isinstance(exc, (httpx.TimeoutException, httpx.NetworkError))


def build_client(
    *,
    headers: Mapping[str, str] | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_SECONDS,
) -> httpx.Client:
    base_headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "application/json",
    }
    if headers:
        base_headers.update(headers)
    return httpx.Client(
        timeout=httpx.Timeout(timeout_s),
        headers=base_headers,
        follow_redirects=True,
    )


@retry(
    reraise=True,
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
    retry=retry_if_exception(_should_retry),
)
def get_json(
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    params: Mapping[str, Any] | None = None,
) -> Any:
    with build_client(headers=headers) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()
