# -*- coding: utf-8 -*-
"""
契约测试组件（业务层）。
对应简历项目② APITestka：扩展 JSON Schema / JSONPath / 响应时间 SLA 断言验证接口契约与性能。
"""
import json

from jsonschema import validate, ValidationError, draft7_format_checker


class ContractAssert:
    """契约断言工具。"""

    @staticmethod
    def schema(instance: dict, schema: dict, msg="JSON Schema契约"):
        """用 JSON Schema 校验响应结构是否符合契约。"""
        try:
            validate(instance=instance, schema=schema, format_checker=draft7_format_checker)
            print(f"[ASSERT] {msg} 校验通过")
            return True
        except ValidationError as e:
            raise AssertionError(f"{msg}校验失败: {e.message} | 路径: {list(e.absolute_path) or '/'}")

    @staticmethod
    def schema_from_file(instance: dict, schema_file: str, msg="JSON Schema契约"):
        """从 data/schemas/ 下的 JSON Schema 文件校验响应结构。"""
        with open(schema_file, encoding="utf-8") as f:
            schema = json.load(f)
        return ContractAssert.schema(instance, schema, msg)

    @staticmethod
    def required_fields(instance: dict, fields: list, msg="字段存在性"):
        """校验响应必须包含指定字段（契约基础校验）。"""
        missing = [f for f in fields if f not in instance]
        assert not missing, f"{msg}失败: 缺少字段 {missing}"
        print(f"[ASSERT] {msg}通过: 字段 {fields} 均存在")

    @staticmethod
    def field_type(instance: dict, field: str, expect_type: str, msg="字段类型"):
        """校验指定字段的类型是否符合契约。"""
        expect_type_map = {
            "integer": int, "string": str, "bool": bool, "float": float,
        }
        val = instance.get(field)
        assert isinstance(val, expect_type_map.get(expect_type, str)), \
            f"{msg}失败: 字段 {field} 期望类型 {expect_type}, 实际 {type(val).__name__}"
        print(f"[ASSERT] {msg}通过: 字段 {field} 类型为 {expect_type}")
#（注：内容由AI生成）
