from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential


_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def _should_retry(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in _RETRYABLE_STATUS
    return isinstance(exc, (httpx.TimeoutException, httpx.NetworkError))


def build_client(
    *, headers: dict[str, str] | None = None, timeout_s: float = 10.0
) -> httpx.Client:
    base_headers = {
        "User-Agent": "threat-fusion/0.1.0",
        "Accept": "application/json",
    }
    if headers:
        base_headers.update(headers)
    return httpx.Client(timeout=httpx.Timeout(timeout_s), headers=base_headers)


@retry(
    reraise=True,
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
    retry=retry_if_exception(_should_retry),
)
def get_json(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> Any:
    with build_client(headers=headers) as client:
        resp = client.get(url, params=params)
        if resp.status_code >= 400:
            raise httpx.HTTPStatusError(
                "request failed", request=resp.request, response=resp
            )
        return resp.json()
