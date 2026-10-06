# -*- coding: utf-8 -*-
"""HTTP 请求统一封装（业务层）。基于 requests 库的 Session 复用。"""
import requests
from .config_util import ConfigUtil


class RequestUtil:
    """统一请求封装：复用 Session、统一超时、统一日志。"""

    def __init__(self):
        self.session = requests.Session()

    def send(self, method: str, url: str, *, headers=None, params=None,
             json_body=None, data=None, files=None) -> requests.Response:
        full_url = url if url.startswith("http") else ConfigUtil.base_url() + url
        method = method.upper()
        timeout = ConfigUtil.timeout()

        resp = self.session.request(
            method=method,
            url=full_url,
            headers=headers,
            params=params,
            json=json_body,
            data=data,
            files=files,
            timeout=timeout,
        )
        print(f"[HTTP] {method} {full_url} -> {resp.status_code}")
        return resp

    def get(self, url, **kwargs):
        return self.send("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.send("POST", url, **kwargs)
