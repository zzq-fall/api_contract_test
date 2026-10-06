# -*- coding: utf-8 -*-
"""
本地 Mock 服务器（业务层，纯 Python 标准库）。
用于契约测试 / SLA 测试 / VCR 录放的本地被测系统。
【注意】DB 用户数据必须包含 age 字段，与 data/schemas/*.json 契约保持一致，
否则 JSON Schema 契约校验会报 "age is a required property"。

启动: python scripts/mock_server.py    默认监听 127.0.0.1:9000
"""
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HOST, PORT = "127.0.0.1", 9000

# 模拟的"数据库" —— age 字段必须存在，契约要求必填
DB = {
    "users": [
        {"id": 1, "name": "张伟", "email": "zhangwei@example.com", "age": 25},
        {"id": 2, "name": "李娜", "email": "lina@example.com", "age": 28},
    ]
}


class MockHandler(BaseHTTPRequestHandler):
    def _send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length) or b"{}")

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/login":
            body = self._read_body()
            if body.get("username") and body.get("password"):
                self._send_json({"code": 0, "token": "mock-token-abc123", "expires_in": 7200})
            else:
                self._send_json({"code": 40001, "message": "用户名或密码错误"})
        elif path == "/api/users":
            body = self._read_body()
            new_id = max(u["id"] for u in DB["users"]) + 1
            user = {
                "id": new_id,
                "name": body.get("name", ""),
                "email": body.get("email", ""),
                "age": body.get("age", 20),  # 新用户默认给一个 age，保证契约通过
            }
            DB["users"].append(user)
            self._send_json({"code": 0, "data": user})
        else:
            self._send_json({"code": 40400, "message": "接口不存在"}, 404)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        time.sleep(0.05)  # 模拟网络耗时，用于演示 SLA 断言
        if path == "/api/users":
            page = int(dict(p.split("=") for p in parsed.query.split("&") if "=" in p).get("page", 1))
            self._send_json({"code": 0, "data": {"page": page, "total": len(DB["users"]), "items": DB["users"]}})
        elif path.startswith("/api/users/"):
            uid = int(path.rsplit("/", 1)[-1])
            user = next((u for u in DB["users"] if u["id"] == uid), None)
            if user:
                self._send_json({"code": 0, "data": user})
            else:
                self._send_json({"code": 40400, "message": "用户不存在"})
        else:
            self._send_json({"code": 40400, "message": "接口不存在"}, 404)

    def log_message(self, *args):
        print(f"[MOCK] {self.command} {self.path}")


if __name__ == "__main__":
    print(f"Mock server 启动: http://{HOST}:{PORT}")
    HTTPServer((HOST, PORT), MockHandler).serve_forever()
