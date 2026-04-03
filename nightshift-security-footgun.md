# Security Foot-Gun Finder Report — delvn

**Generated:** 2026-04-03  
**Branch:** `nightshift/security-footgun`  
**Scope:** `src/` — all Python source modules  
**Tooling:** Manual static analysis

---

## Executive Summary

The delvn codebase is a well-structured Python threat-intelligence pipeline. It uses sound practices in several areas: `yaml.safe_load` for YAML parsing, Pydantic models for data validation, `httpx` with default TLS verification, no hardcoded secrets, and parameterized queries for user-supplied values in Cosmos DB. However, the analysis identified **12 security-relevant findings** across P1–P3 severity levels. The most significant risks are f-string SQL construction in Cosmos queries (a latent injection foot-gun), missing retry/resilience on the embedding HTTP call, blanket exception swallowing that hides security events, and potential path traversal in the report writer.

| # | Severity | File | Finding |
|---|----------|------|---------|
| F-01 | **P1** | `src/storage/cosmos.py:67-69,81` | F-string SQL construction in Cosmos DB queries (latent injection risk) |
| F-02 | **P1** | `src/embeddings/client.py:63-72` | Raw `httpx.post()` bypasses shared HTTP client — no retry, no resilience |
| F-03 | **P1** | `src/storage/search.py:187-188` | OData filter built with f-string — insufficient escaping |
| F-04 | **P2** | `src/storage/search.py:186-188` | Single-quote-only escaping for OData `filter` expression |
| F-05 | **P2** | `src/agents/reporter_agent.py:58-61` | File write without path-traversal guard |
| F-06 | **P2** | `src/agents/news_agent.py:17-25` | SSRF surface via `RSS_FEED_URLS` environment variable |
| F-07 | **P2** | `src/agents/*.py` (6 files) | Blanket `except Exception` blocks silently swallow security errors |
| F-08 | **P2** | `src/integrations/rss.py:17` | Unvalidated external URL passed to `feedparser.parse()` |
| F-09 | **P2** | `src/config/settings.py:43-45` | Secrets held as plain strings; `lru_cache` prevents key rotation |
| F-10 | **P3** | `src/common/http.py:35` | Unconditional `follow_redirects=True` on shared HTTP client |
| F-11 | **P3** | `src/storage/cosmos.py:66-70` | Dynamic column names in SQL via f-string (safe today, fragile pattern) |
| F-12 | **P3** | `src/normalization/normalize.py:35` | Slow `dateutil.parser.parse` fallback on attacker-controlled date strings |

---

## Detailed Findings

### F-01 · P1 (High) — F-string SQL construction in Cosmos DB queries

**File:** `src/storage/cosmos.py`, lines 67–69 and 81  
**Category:** NoSQL Injection (latent)

```python
# Line 67-69
query = (
    f"SELECT TOP {normalized_limit} * FROM c "
    f"WHERE IS_DEFINED(c.{time_field}) AND IS_STRING(c.{time_field}) "
    f"ORDER BY c.{time_field} DESC"
)

# Line 81
fallback_query = f"SELECT TOP {normalized_limit} * FROM c ORDER BY c._ts DESC"
```

**Description:**  
The `list_recent_threats` method builds Cosmos DB SQL queries using f-string interpolation. While `normalized_limit` is cast to `int()` (preventing injection through the limit value) and `time_field` is sourced from a hardcoded tuple `("observed_at", "published_at")`, the **pattern itself is a foot-gun**. Any future refactoring that passes user-controlled data into these variables will create a direct NoSQL injection vector. F-string SQL construction violates the principle of parameterized queries.

**Risk:** Currently not exploitable. Will become a critical injection vulnerability if the code is refactored to accept dynamic field names, sort columns, or where clauses from external input.

**Recommended Fix:**  
Use parameterized queries wherever possible. For column names that must be dynamic, maintain an explicit allowlist and validate against it before interpolation.

```python
_ALLOWED_TIME_FIELDS = frozenset({"observed_at", "published_at"})

if time_field not in _ALLOWED_TIME_FIELDS:
    raise ValueError(f"Invalid time field: {time_field!r}")
query = (
    f"SELECT TOP @limit * FROM c "
    f"WHERE IS_DEFINED(c.{time_field}) AND IS_STRING(c.{time_field}) "
    f"ORDER BY c.{time_field} DESC"
)
parameters=[{"name": "@limit", "value": normalized_limit}]
# Note: column names cannot be parameterized in Cosmos SQL;
# the allowlist check is the critical safety measure.
```

---

### F-02 · P1 (High) — Raw `httpx.post()` bypasses shared HTTP client

**File:** `src/embeddings/client.py`, lines 63–72  
**Category:** Insecure HTTP client usage / Missing resilience

```python
response = httpx.post(
    url=(
        f"{self._endpoint}/openai/deployments/{self._deployment}/embeddings"
        f"?api-version={self._api_version}"
    ),
    headers={"api-key": self._api_key, "Content-Type": "application/json"},
    json={"input": texts},
    timeout=self._timeout_seconds,
)
response.raise_for_status()
```

**Description:**  
The `AzureOpenAIEmbeddingClient.embed()` method uses `httpx.post()` directly instead of the shared `build_client()` / `get_json()` utilities from `common/http.py`. This means:

1. **No retry logic** — The shared client uses `tenacity` with exponential backoff for 429/5xx errors. The embedding call has none, so transient failures cause immediate crashes.
2. **No `User-Agent` header** — The shared client sends `delvn/0.1.0`; the raw call does not, making API usage harder to trace and potentially triggering bot-detection heuristics.
3. **No redirect policy** — The shared client explicitly enables redirects; the raw call uses httpx defaults.
4. **No connection pooling** — Each call creates and destroys a new TCP connection.

The timeout (30s default) is set, which is good. TLS verification uses the httpx default (`verify=True`), which is also good.

**Risk:** Transient network errors or rate-limiting from Azure OpenAI will cause unhandled exceptions that propagate up to the correlator agent, potentially halting the correlation pipeline. This is a reliability issue with security implications (denial of service for the threat correlation workflow).

**Recommended Fix:**  
Use the shared HTTP client pattern, or at minimum add retry logic:

```python
from common.http import build_client

def embed(self, texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    with build_client(
        headers={"api-key": self._api_key},
        timeout_s=self._timeout_seconds,
    ) as client:
        response = client.post(
            url=(...),
            json={"input": texts},
        )
        response.raise_for_status()
    ...
```

---

### F-03 · P1 (High) — OData filter built with f-string from external data

**File:** `src/storage/search.py`, lines 186–188  
**Category:** Injection (OData filter)

```python
if exclude_id:
    escaped_id = exclude_id.replace("'", "''")
    filter_expression = f"id ne '{escaped_id}'"
```

**Description:**  
The `vector_query` method constructs an Azure AI Search OData `$filter` expression by interpolating `exclude_id` into an f-string. The `exclude_id` originates from `threat.id`, which is constructed from external data (NVD CVE IDs, OTX indicator values, RSS feed items). While single quotes are escaped by doubling them, this escaping is **insufficient** for OData filter expressions:

- OData supports a rich expression syntax including function calls (`search.ismatch()`, `geo.distance()`), logical operators, and type literals.
- Backslash characters, double quotes, or other OData metacharacters in `exclude_id` are **not** sanitized.
- A carefully crafted threat ID could potentially break out of the string literal context.

**Example attack vector:** If a threat ID contains characters like `)` or `'` in combination with OData operators, the filter expression could be manipulated.

**Recommended Fix:**  
Use the Azure SDK's built-in parameterized filter support or validate the ID against a strict allowlist pattern:

```python
import re
_SAFE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_:/-]+$')

if exclude_id:
    if not _SAFE_ID_PATTERN.match(exclude_id):
        raise ValueError(f"Invalid exclude_id format: {exclude_id!r}")
    escaped_id = exclude_id.replace("'", "''")
    filter_expression = f"id ne '{escaped_id}'"
```

---

### F-04 · P2 (Medium) — Single-quote-only escaping for OData filter

**File:** `src/storage/search.py`, lines 187–188  
**Category:** Insufficient input sanitization

**Description:**  
This is a companion finding to F-03. The escaping strategy (`replace("'", "''")`) only handles single-quote characters. Azure AI Search OData expressions may interpret other characters as syntactic. The current approach is fragile and depends on the assumption that threat IDs never contain metacharacters — an assumption that may not hold for all data sources.

**Recommended Fix:**  
Same as F-03 — use strict input validation (allowlist pattern) before any string interpolation into filter expressions.

---

### F-05 · P2 (Medium) — File write without path-traversal guard

**File:** `src/agents/reporter_agent.py`, lines 58–61  
**Category:** Insecure file operation / Path traversal

```python
if output_path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")
```

**Description:**  
The `run_reporting` function accepts an `output_path` parameter and writes the generated markdown report to that path without validating that the path stays within an intended output directory. If `output_path` is sourced from user input, configuration, or an API call, an attacker could craft a path like `../../etc/cron.d/malicious` or `/tmp/sensitive-file` to write arbitrary content to any location the process has access to.

The function also creates parent directories with `mkdir(parents=True)`, which amplifies the risk by ensuring the path always exists.

**Recommended Fix:**  
Resolve the path and validate it against an allowed output directory:

```python
import os

ALLOWED_OUTPUT_DIR = os.getenv("DELVN_OUTPUT_DIR", "./artifacts")

if output_path:
    output = Path(output_path).resolve()
    allowed_root = Path(ALLOWED_OUTPUT_DIR).resolve()
    if not str(output).startswith(str(allowed_root)):
        raise ValueError(f"output_path must be within {allowed_root}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")
```

---

### F-06 · P2 (Medium) — SSRF surface via RSS_FEED_URLS environment variable

**File:** `src/agents/news_agent.py`, lines 17–25  
**Category:** Server-Side Request Forgery (SSRF)

```python
def _resolve_feeds() -> list[str]:
    override = os.getenv("RSS_FEED_URLS", "")
    if not override:
        return DEFAULT_FEEDS.copy()
    feeds = [feed.strip() for feed in override.split(",") if feed.strip()]
    if feeds:
        return feeds
    return DEFAULT_FEEDS.copy()
```

**Description:**  
The `_resolve_feeds` function reads a comma-separated list of URLs from the `RSS_FEED_URLS` environment variable and passes them directly to `fetch_feed()` → `feedparser.parse()` → HTTP request. There is **no URL scheme validation**, **no hostname allowlist**, and **no private-IP blocking**. An attacker who can control the environment variable (e.g., through a container misconfiguration, CI/CD variable injection, or shared deployment config) can trigger requests to internal services:

- `http://169.254.169.254/latest/meta-data/` (cloud metadata service)
- `http://localhost:6379/` (internal Redis)
- `http://internal-api.company.local/` (internal services)
- `file:///etc/passwd` (local file access via feedparser's URL handling)

**Recommended Fix:**  
Validate URLs against an allowlist of schemes and, optionally, hostnames:

```python
from urllib.parse import urlparse

def _validate_feed_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http"):
        raise ValueError(f"Unsupported feed URL scheme: {parsed.scheme}")
    # Optionally block private IPs
    hostname = parsed.hostname or ""
    if hostname in ("localhost", "127.0.0.1", "169.254.169.254"):
        raise ValueError(f"Feed URL points to blocked host: {hostname}")
    return url
```

---

### F-07 · P2 (Medium) — Blanket exception swallowing hides security events

**Files:**  
- `src/agents/cve_agent.py` — lines 35, 45, 52, 60  
- `src/agents/intel_agent.py` — lines 18, 27, 33, 46  
- `src/agents/news_agent.py` — lines 52, 68  
- `src/agents/correlator_agent.py` — lines 35, 41, 51, 57, 77, 94  
- `src/agents/prioritizer_agent.py` — lines 40, 48, 57  

**Category:** Missing security observability / Error handling

```python
# Example from cve_agent.py:35
except Exception:
    stats["errors"] += 1
    return stats
```

**Description:**  
All agent modules use bare `except Exception:` blocks that increment an error counter and continue. No exception information is logged, not even the exception type. This means:

1. **Security events are invisible** — Authentication failures to Cosmos DB, certificate validation errors, or injection-attempt responses from APIs are silently counted as generic errors.
2. **Debugging is impossible** — When a pipeline run reports `errors: 47`, there is no way to determine what went wrong without reproducing the issue.
3. **Data integrity issues are masked** — A `ValueError` from input validation and a `PermissionError` from Cosmos DB are treated identically.

**Recommended Fix:**  
Add structured logging at minimum for errors; consider distinguishing retryable from fatal errors:

```python
import logging
logger = logging.getLogger(__name__)

try:
    ...
except Exception as exc:
    logger.exception("CVE fetch failed")  # includes full traceback
    stats["errors"] += 1
    return stats
```

---

### F-08 · P2 (Medium) — Unvalidated external URL passed to feedparser

**File:** `src/integrations/rss.py`, line 17  
**Category:** SSRF / Unsafe deserialization

```python
def fetch_feed(url: str) -> list[dict[str, Any]]:
    parsed = feedparser.parse(url)
```

**Description:**  
The `feedparser.parse()` function fetches and parses content from the provided URL. While `feedparser` is generally robust, it:

1. Follows HTTP redirects by default
2. Can parse local files via `file://` scheme
3. Parses XML which, despite feedparser's built-in protections, could trigger vulnerabilities in underlying XML parsers for specially crafted content
4. Makes network requests without any timeout (the default `feedparser.parse()` does not use the shared HTTP client's timeout settings)

The `url` parameter comes from either hardcoded `DEFAULT_FEEDS` or the `RSS_FEED_URLS` environment variable (see F-06).

**Recommended Fix:**  
- Use the shared HTTP client to fetch content, then pass the response body to `feedparser.parse()` as a string, giving control over timeouts and TLS.
- Validate URL scheme before fetching.

```python
def fetch_feed(url: str) -> list[dict[str, Any]]:
    # Validate URL
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ("https",):
        raise ValueError(f"Feed URL must use HTTPS: {url}")

    # Fetch with shared client (timeout, retries, TLS)
    content = get_json(url)  # or use get_raw for non-JSON
    parsed = feedparser.parse(content)
    ...
```

---

### F-09 · P2 (Medium) — Secrets held as plain strings with no rotation support

**File:** `src/config/settings.py`, lines 14, 20, 25–26, 28–29, 31–32  
**Category:** Secrets management

```python
COSMOS_KEY: str | None = None
SEARCH_KEY: str | None = None
NVD_API_KEY: str | None = None
OTX_API_KEY: str | None = None
FOUNDRY_API_KEY: str | None = None
AZURE_OPENAI_API_KEY: str | None = None
```

**Description:**  
All API keys and credentials are stored as plain `str | None` fields on the `Settings` Pydantic model. Combined with the `@lru_cache(maxsize=1)` decorator on `get_settings()` (line 43), this means:

1. **No key rotation without restart** — The cached `Settings` instance is never invalidated. If an API key is rotated (e.g., after a leak), the application must be fully restarted.
2. **Risk of accidental logging** — If the `Settings` object is logged, serialized, or included in an error response (e.g., `model_dump()`), all credentials are exposed in plain text.
3. **No key masking** — Pydantic's `Field(secret=True)` is not used, so no built-in protection against serialization leakage.

**Recommended Fix:**

```python
from pydantic import SecretStr

class Settings(BaseSettings):
    COSMOS_KEY: SecretStr | None = None
    SEARCH_KEY: SecretStr | None = None
    NVD_API_KEY: SecretStr | None = None
    OTX_API_KEY: SecretStr | None = None
    FOUNDRY_API_KEY: SecretStr | None = None
    AZURE_OPENAI_API_KEY: SecretStr | None = None
```

And add a mechanism to invalidate the settings cache for key rotation.

---

### F-10 · P3 (Low) — Unconditional redirect following on shared HTTP client

**File:** `src/common/http.py`, line 35  
**Category:** SSRF amplification

```python
return httpx.Client(
    timeout=httpx.Timeout(timeout_s),
    headers=base_headers,
    follow_redirects=True,
)
```

**Description:**  
The shared HTTP client has `follow_redirects=True` unconditionally. While this is convenient for API integrations that redirect (e.g., CDN URLs), it expands the SSRF attack surface: a malicious or compromised API endpoint can redirect to internal services. Combined with the fact that the client sends API keys in headers (e.g., NVD `apiKey`, OTX `X-OTX-API-KEY`), a redirect to an attacker-controlled server could exfiltrate these keys.

**Recommended Fix:**  
- Limit the number of redirects: `max_redirects=3`
- Consider stripping sensitive headers on cross-origin redirects
- Or set `follow_redirects=False` and handle redirects explicitly for known safe endpoints

---

### F-11 · P3 (Low) — Dynamic column names in Cosmos SQL (safe today, fragile pattern)

**File:** `src/storage/cosmos.py`, lines 65–69  
**Category:** NoSQL injection (latent)

```python
for time_field in ("observed_at", "published_at"):
    query = (
        f"SELECT TOP {normalized_limit} * FROM c "
        f"WHERE IS_DEFINED(c.{time_field}) AND IS_STRING(c.{time_field}) "
        f"ORDER BY c.{time_field} DESC"
    )
```

**Description:**  
The `time_field` variable is interpolated directly into the SQL column position. Currently safe because the loop source is a hardcoded tuple of two strings. However, this pattern has no validation guard — if a future developer changes the loop source to include external input, it becomes a direct injection vector. Cosmos DB SQL column names cannot be parameterized, so an explicit allowlist check is the only defense.

**Recommended Fix:**  
Add an explicit allowlist assertion near the interpolation:

```python
_ALLOWED_SORT_FIELDS = frozenset({"observed_at", "published_at", "_ts"})
assert time_field in _ALLOWED_SORT_FIELDS
```

---

### F-12 · P3 (Low) — Slow dateutil fallback on untrusted input

**File:** `src/normalization/normalize.py`, line 35  
**Category:** Denial of Service (algorithmic)

```python
try:
    return parser.isoparse(text)
except ValueError:
    try:
        return parser.parse(text)
    except (OverflowError, TypeError, ValueError):
        return None
```

**Description:**  
The `dateutil.parser.parse()` fallback is known to have poor performance on certain adversarial inputs (e.g., very long numeric strings, ambiguous date formats). While the input originates from API responses (NVD, OTX, RSS) rather than direct user input, a compromised or malicious feed could craft date strings that cause excessive CPU consumption.

The `isoparse()` first attempt is fast and handles ISO 8601 — the fallback to `parser.parse()` is only needed for non-standard date formats.

**Recommended Fix:**  
- Add a length check before parsing (e.g., `if len(text) > 64: return None`)
- Consider removing the `parser.parse()` fallback if all data sources use ISO 8601 dates
- Or set a CPU timeout around the parsing call

---

## Positive Security Observations

The following good practices were observed during the analysis:

| Area | Practice | Location |
|------|----------|----------|
| YAML parsing | Uses `yaml.safe_load()` — not vulnerable to deserialization attacks | `src/config/user_stack.py:57` |
| TLS verification | All HTTP clients use default `verify=True`; no `verify=False` anywhere | `src/common/http.py`, `src/embeddings/client.py` |
| Timeouts | Shared HTTP client sets `timeout=httpx.Timeout(10.0)` | `src/common/http.py:33` |
| No hardcoded secrets | No API keys or credentials in source code | All files |
| `.gitignore` | `.env` and `.env.*` are excluded from version control | `.gitignore` |
| Data validation | Pydantic models with `Field(min_length=1)`, `ge`/`le` constraints, and `extra="ignore"` | `src/models/*.py` |
| NoSQL parameterization | `list_correlations_for_threat` uses parameterized `@threat_id` | `src/storage/cosmos.py:100-106` |
| Input bounds checking | `limit`, `results_per_page`, `top_k` validated before use | Multiple files |
| No `eval()`/`exec()` | No use of dangerous Python functions | All files |
| No `pickle` | No unsafe deserialization | All files |

---

## Recommendations Summary

1. **Immediately** (P1): Refactor Cosmos DB SQL queries to use allowlist-validated column names (F-01). Validate `exclude_id` before OData filter interpolation (F-03). Refactor embedding client to use the shared HTTP client (F-02).
2. **Short-term** (P2): Add path-traversal validation to the report writer (F-05). Validate and restrict feed URLs (F-06, F-08). Add structured logging to all agent error handlers (F-07). Use `SecretStr` for credential fields (F-09).
3. **Hardening** (P3): Add redirect limits to the shared HTTP client (F-10). Add allowlist assertions for dynamic SQL column names (F-11). Add input length limits for date parsing (F-12).
