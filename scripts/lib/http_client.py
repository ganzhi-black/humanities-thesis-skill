"""统一的 HTTP 请求封装，供各数据源脚本调用"""
from __future__ import annotations
import urllib.request
import urllib.parse
import urllib.error
import ssl
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 默认使用系统 SSL 证书验证
_SSL_CTX_SECURE = ssl.create_default_context()

# 仅在安全连接失败时作为 fallback，并发出警告
_SSL_CTX_INSECURE = ssl.create_default_context()
_SSL_CTX_INSECURE.check_hostname = False
_SSL_CTX_INSECURE.verify_mode = ssl.CERT_NONE

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def get_text(
    url: str,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: int = 15,
    encoding: str = "utf-8",
) -> str:
    """发送 GET 请求，返回响应文本。默认验证 SSL，失败时 fallback 并警告。"""
    if params:
        url = url + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", DEFAULT_UA)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)

    # 先尝试安全连接
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX_SECURE) as resp:
            return resp.read().decode(encoding, errors="replace")
    except ssl.SSLError as ssl_err:
        # SSL 验证失败，fallback 到不验证，但发出警告
        logger.warning(
            "SSL verification failed for %s (%s), retrying without verification. "
            "This may expose data to interception.",
            url.split("?")[0], ssl_err,
        )
        try:
            # 需要重新创建 Request 对象
            req2 = urllib.request.Request(url)
            req2.add_header("User-Agent", DEFAULT_UA)
            if headers:
                for k, v in headers.items():
                    req2.add_header(k, v)
            with urllib.request.urlopen(req2, timeout=timeout, context=_SSL_CTX_INSECURE) as resp:
                return resp.read().decode(encoding, errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            raise ConnectionError(f"HTTP request failed (SSL fallback): {e}") from e
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        raise ConnectionError(f"HTTP request failed: {e}") from e


def get_json(
    url: str,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: int = 15,
) -> dict:
    """发送 GET 请求，解析 JSON 响应"""
    text = get_text(url, params=params, headers=headers, timeout=timeout)
    return json.loads(text)
