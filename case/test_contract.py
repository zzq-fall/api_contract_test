"""
契约测试
1. 从JSON数据驱动文件读取用例，0代码新增契约用例
2. JSON Schema校验响应结构是否符合契约（json-schema校验）
3. JSONPath字段断言
4. 响应时间SLA断言
5. VCR录放：录制真实交互，回放时离线复用 cassette，提升稳定性
6. OpenAPI契约：演示从 OpenAPI 规范导入接口定义

数据驱动文件：data/contract_cases.json
契约文件：data/schemas/*.json
"""
import json
import os

import allure
import pytest

from common.request_util import RequestUtil
from common.contract_util import ContractAssert
from common.sla_util import SlaAssert
from common.vcr_util import use_cassette

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "contract_cases.json")
OPENAPI_FILE = os.path.join(BASE_DIR, "data", "openapi.yaml")


def _load_contract_cases():
    """读取 JSON 数据驱动的契约用例"""
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


CONTRACT_CASES = _load_contract_cases()


@pytest.mark.parametrize("case", CONTRACT_CASES, ids=[c["name"] for c in CONTRACT_CASES])
@use_cassette("contract_api", record_mode="new_episodes")
@allure.title("契约测试: {case[name]}")
def test_contract(case):
    request_util = RequestUtil()
    resp = request_util.send(
        case["method"], case["url"],
        params=case.get("params"),
        headers=case.get("headers"),
    )

    # 1. 契约校验：JSON Schema 校验响应结构
    if case.get("schema"):
        schema_path = os.path.join(BASE_DIR, "data", case["schema"])
        with allure.step("JSON Schema 契约校验"):
            ContractAssert.schema_from_file(resp.json(), schema_path)

    # 2. JSONPath 字段断言
    for expr, expect in (case.get("jsonpath", {}) or {}).items():
        with allure.step(f"JSONPath 断言 {expr}"):
            ContractAssert.schema(resp.json(), {
                "type": "object",
                "properties": {"code": {"type": "integer"}},
                "required": ["code"],
            })  # 保持基础契约校验
            # JSONPath 字段校验
            actual = __find_by_path(resp.json(), expr)
            assert actual == expect, f"JSONPath {expr} 断言失败: 预期{expect}, 实际{actual}"

    # 3. SLA 性能断言
    if case.get("sla"):
        with allure.step("响应时间 SLA 断言"):
            SlaAssert.response_time(resp)


def __find_by_path(obj, path: str):
    """极简 JSONPath 取数：支持 $.a.b / $.data[0].id 形式。"""
    import re
    parts = re.split(r"\.", path.strip("$").lstrip("."))
    cur = obj
    for p in parts:
        if not p:
            continue
        if "[" in p:
            key, _, rest = p.partition("[")
            idx = int(rest.rstrip("]")) if rest else 0
            cur = cur[key][idx] if key else cur[idx]
        else:
            cur = cur[p]
    return cur


@use_cassette("openapi_contract", record_mode="new_episodes")
@allure.title("OpenAPI 契约: 从规范导入并校验用户接口结构")
def test_openapi_contract():
    """演示 OpenAPI 驱动：读取 openapi.yaml，对用户接口响应做契约校验。"""
    import yaml

    with open(OPENAPI_FILE, encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    # 从 OpenAPI 中提取用户契约 schema 的关键字段约束，落到 JSON Schema 校验
    user_schema = spec["components"]["schemas"]["User"]
    assert "id" in user_schema["required"] and "email" in user_schema["required"], "OpenAPI契约缺少必需字段"

    request_util = RequestUtil()
    resp = request_util.get("/api/users/1")

    # 用 OpenAPI 派生的约束校验响应
    contract = {
        "type": "object",
        "required": ["code", "data"],
        "properties": {
            "code": {"type": "integer"},
            "data": {
                "type": "object",
                "required": user_schema["required"],
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "age": {"type": "integer", "minimum": 0},
                },
            },
        },
    }
    with allure.step("OpenAPI 派生契约校验"):
        ContractAssert.schema(resp.json(), contract)
