# api-contract-testing

全栈 API 契约测试练习项目（业务层封装）——对应简历"全栈 API 自动化测试框架（基于开源 APITestka）"项目。

基于开源 APITestka 框架的思路，围绕**接口契约与性能**做业务层扩展：使用
`jsonschema` 做 **JSON Schema 契约校验**、`vcrpy` 做 **VCR 录放**、自研 **响应时间 SLA 断言**、
**JSON 数据驱动**，并演示 **OpenAPI 规范驱动** 的契约测试。

> 说明：本项目为个人学习与求职展示项目，借鉴开源 APITestka 框架的契约/性能测试设计思路，
> 底层依赖 jsonschema / vcrpy / requests 等开源库；本人独立完成契约断言组件、VCR 录放封装、
> SLA 断言、数据驱动与用例编写等业务代码。

---

## 功能特性

| 模块 | 说明 |
| --- | --- |
| JSON Schema 契约校验 | 用 jsonschema 校验响应结构是否符合契约文件（`data/schemas/`） |
| 字段级契约 | 校验响应必须包含的字段及字段类型 |
| 响应时间 SLA 断言 | 校验响应耗时不超过阈值（conf.ini `sla_ms`），验证接口性能 |
| VCR 录放 | 录制真实接口交互，离线回放复用 cassette，提升稳定性与效率 |
| JSON 数据驱动 | 从 `data/contract_cases.json` 读用例，0 代码新增契约用例 |
| OpenAPI 契约 | 从 `data/openapi.yaml` 导入接口定义，派生契约校验响应 |

## 技术栈

- pytest（用例执行 / 参数化 / fixture）
- jsonschema（JSON Schema 契约校验）
- vcrpy（VCR 录制 / 回放）
- requests（HTTP 请求）
- PyYAML（OpenAPI 契约解析）
- allure-pytest（可视化测试报告）

## 目录结构

```
api-contract-testing/
├── case/                     # 测试驱动层
│   └── test_contract.py      # 契约测试（JSON Schema / SLA / JSONPath / OpenAPI）
├── common/                   # 业务层公共封装（本项目核心代码）
│   ├── contract_util.py      # 契约断言组件（JSON Schema / 字段 / 类型）
│   ├── sla_util.py           # 响应时间 SLA 断言
│   ├── vcr_util.py           # VCR 录放封装
│   ├── request_util.py       # 请求封装
│   └── config_util.py        # 配置读取
├── data/
│   ├── contract_cases.json   # 契约用例（JSON 数据驱动）
│   ├── openapi.yaml          # OpenAPI 规范
│   ├── schemas/              # JSON Schema 契约文件
│   │   ├── user_list_schema.json
│   │   └── user_detail_schema.json
│   └── cassettes/            # VCR 录放数据（录制后自动生成）
├── conf/
│   └── conf.ini              # 环境 / SLA / 报告配置
├── scripts/
│   └── mock_server.py        # 本地 mock 服务器
├── report/                   # allure 结果输出
├── run.py                    # 执行入口
└── requirements.txt
```

## 快速开始

```bash
# 1. 安装依赖（建议 Python 3.8+）
pip install -r requirements.txt

# 2. 首次运行：启动 mock 服务器录制接口交互
python scripts/mock_server.py    # 终端A
python run.py                     # 终端B（会录制 VCR cassette）

# 3. 之后可以停掉 mock，纯离线回放（VCR 能力）
python run.py                     # 无需 mock，从 cassette 回放
```

执行成功会看到 4 个测试全部通过：
`查询用户列表(契约+SLA) → 查询用户1(契约+JSONPath) → 查询用户2(契约+JSONPath) → OpenAPI契约`

## 用例编写示例

在 `data/contract_cases.json` 中新增一条即可（0 代码新增契约用例）：

```json
{
  "name": "契约4: 查询单个用户",
  "method": "GET",
  "url": "/api/users/1",
  "schema": "schemas/user_detail_schema.json",
  "sla": true,
  "jsonpath": {"$.data.id": 1}
}
```

## JSON Schema 契约示例

`data/schemas/user_detail_schema.json`（校验响应结构）：

```json
{
  "type": "object",
  "required": ["code", "data"],
  "properties": {
    "code": { "type": "integer" },
    "data": {
      "type": "object",
      "required": ["id", "name", "email", "age"],
      "properties": {
        "id": { "type": "integer" },
        "email": { "type": "string", "format": "email" },
        "age": { "type": "integer", "minimum": 0 }
      }
    }
  }
}
```

## VCR 录放说明

- 首次运行（mock 开启时）会把真实 HTTP 交互录制到 `data/cassettes/*.yaml`；
- 之后即使被测服务不可用，也能从 cassette 离线回放，保证测试稳定可复现；
- 对应简历"配置 VCR 录放代理"的描述。

## 接入真实项目

把 `conf/conf.ini` 的 `base_url` 改成真实被测环境地址，契约文件按真实接口调整即可。

## License

仅供学习与求职展示使用。
