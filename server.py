import logging
import os
import re
import typing as t

import requests
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("gnews-mcp")

BASE_URL = "https://gnews.io/api/v4"
DEFAULT_TIMEOUT = 20

# HTTP session with retries
_session = Session()
_retry = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset(["GET"]),
    raise_on_status=False,
)
_adapter = HTTPAdapter(max_retries=_retry)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)

mcp = FastMCP("gnews")

def _resolve_key(api_key: t.Optional[str]) -> str:
    headers = get_http_headers(include_all=False) or {}
    h_key = headers.get("X-Api-Key") or headers.get("X-Api-Key")
    if h_key:
        return str(h_key).strip()

    raise RuntimeError(
        "GNews API key required (missing header 'X-Api-Key')."
    )

def _iso(value: t.Optional[str]) -> t.Optional[str]:
    if not value:
        return None
    v = value.strip()
    return v + "T00:00:00Z" if len(v) == 10 and re.match(r"^\d{4}-\d{2}-\d{2}$", v) else v

def _clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))

def _validate_common(
    lang: t.Optional[str],
    country: t.Optional[str],
    max_results: int,
    page: int,
    date_from: t.Optional[str],
    date_to: t.Optional[str],
) -> None:
    if lang is not None and not re.match(r"^[a-zA-Z]{2}$", lang):
        raise ValueError("Parameter 'lang' invalid (2 letters, e.g. 'fr').")
    if country is not None and not re.match(r"^[a-zA-Z]{2}$", country):
        raise ValueError("Parameter 'country' invalid (2 letters, e.g. 'fr').")
    if page < 1:
        raise ValueError("'page' must be greater than 1.")
    if not (1 <= max_results <= 100):
        raise ValueError("'max' must be between 1 and 100.")
    for d, name in ((date_from, "date_from"), (date_to, "date_to")):
        if d is None:
            continue
        if len(d) == 10 and not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            raise ValueError(f"'{name}' is invalid. IS 8601 format required.")

def _http_get(url: str, params: dict, api_key: str) -> dict:
    params = {k: v for k, v in params.items() if v is not None}
    params["apikey"] = api_key
    try:
        r = _session.get(
            url,
            params=params,
            timeout=DEFAULT_TIMEOUT,
            headers={"User-Agent": "gnews-mcp/1.0"},
        )
        if r.status_code >= 400:
            msg = f"HTTP error {r.status_code} from GNews API."
            try:
                data = r.json()
                extra = data.get("errors") or data.get("message") or data
                msg += f" Details: {extra}"
            except Exception:
                pass
            raise RuntimeError(msg)
        try:
            return r.json()
        except requests.exceptions.JSONDecodeError:
            raise RuntimeError("Invalid GNews API response (JSON expected).")
    except requests.Timeout:
        raise RuntimeError("Timeout when calling GNews API.")
    except requests.RequestException as e:
        code = getattr(getattr(e, "response", None), "status_code", "n/a")
        raise RuntimeError(f"Network error (status: {code}).") from e

@mcp.tool
def search(
    q: str,
    lang: t.Optional[str] = None,
    country: t.Optional[str] = None,
    max: int = 10,
    in_fields: t.Optional[str] = None,
    sortby: t.Literal["publishedAt", "relevance"] = "publishedAt",
    date_from: t.Optional[str] = None,
    date_to: t.Optional[str] = None,
    page: int = 1,
) -> dict:
    key = _resolve_key()
    _validate_common(lang, country, max, page, date_from, date_to)
    params = {
        "q": q,
        "lang": lang.lower() if lang else None,
        "country": country.lower() if country else None,
        "max": _clamp(max, 1, 100),
        "in": in_fields,
        "sortby": sortby,
        "from": _iso(date_from),
        "to": _iso(date_to),
        "page": page,
    }
    log.debug("Calling /search (q=%r, max=%s, page=%s, lang=%s, country=%s)", q, params["max"], page, params["lang"], params["country"])
    return _http_get(f"{BASE_URL}/search", params, key)

@mcp.tool
def top_headlines(
    category: t.Literal[
        "general","world","nation","business","technology",
        "entertainment","sports","science","health"
    ] = "general",
    lang: t.Optional[str] = None,
    country: t.Optional[str] = None,
    max: int = 10,
    q: t.Optional[str] = None,
    date_from: t.Optional[str] = None,
    date_to: t.Optional[str] = None,
    page: int = 1,
) -> dict:
    key = _resolve_key()
    _validate_common(lang, country, max, page, date_from, date_to)
    params = {
        "category": category,
        "lang": lang.lower() if lang else None,
        "country": country.lower() if country else None,
        "max": _clamp(max, 1, 100),
        "q": q,
        "from": _iso(date_from),
        "to": _iso(date_to),
        "page": page,
    }
    log.debug("Calling /top-headlines (cat=%s, max=%s, page=%s, lang=%s, country=%s)", category, params["max"], page, params["lang"], params["country"])
    return _http_get(f"{BASE_URL}/top-headlines", params, key)

# --- (OPTIONAL) docs resources: only if available in package version ---
try:
    from fastmcp.resources import HttpResource, TextResource  # type: ignore
    CHEATSHEET = """\
GNews API Cheat Sheet:
- /search: q, lang, country, max, in, sortby, from, to, page
- /top-headlines: category, lang, country, max, q, from, to, page
- Dates: 'YYYY-MM-DD' ou ISO (ex: '2024-11-01T08:30:00Z')
- sortby: publishedAt | relevance
"""
    mcp.add_resource(TextResource(
        uri="docs://gnews/cheatsheet",
        name="GNews API Cheat Sheet",
        text=CHEATSHEET,
        tags={"documentation", "gnews"},
    ))
    mcp.add_resource(HttpResource(
        uri="docs://gnews/search",
        url="https://docs.gnews.io/endpoints/search-endpoint",
        name="GNews API - Search endpoint",
        tags={"documentation", "gnews"},
    ))
    mcp.add_resource(HttpResource(
        uri="docs://gnews/top-headlines",
        url="https://docs.gnews.io/endpoints/top-headlines-endpoint",
        name="GNews API - Top Headlines endpoint",
        tags={"documentation", "gnews"},
    ))
except Exception:
    log.debug("fastmcp.resources not available: no resource registration (ok).")

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    mcp.run(transport="http", host=host, port=port, path="/")
