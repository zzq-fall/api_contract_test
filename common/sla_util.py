# -*- coding: utf-8 -*-
"""响应时间 SLA 断言组件，对应 APITestka 的性能断言思路"""
from .config_util import ConfigUtil


class SlaAssert:
    """响应时间 SLA 断言"""

    @staticmethod
    def response_time(resp, sla_ms: int = None, msg="响应时间SLA"):
        """断言响应耗时不超过 SLA 阈值（毫秒）"""
        sla_ms = sla_ms or ConfigUtil.sla_ms()
        elapsed_ms = resp.elapsed.total_seconds() * 1000
        assert elapsed_ms <= sla_ms, f"{msg}失败: 耗时{elapsed_ms:.0f}ms, 超出阈值{sla_ms}ms"
        print(f"[ASSERT] {msg}通过: 耗时{elapsed_ms:.0f}ms <= {sla_ms}ms")
        return elapsed_ms

    @staticmethod
    def report_timings(resp_timings: dict, msg="性能统计"):
        """输出整体请求性能统计（供报告展示）"""
        summary = {k: f"{v:.0f}ms" for k, v in resp_timings.items()}
        print(f"[PERF] {msg}: {summary}")
        return summary
