# -*- coding: utf-8 -*-
"""
VCR 录放封装（业务层）。
对应简历项目② APITestka：配置 VCR 录放代理，录制接口真实交互，
回放时用本地录制的 cassette 数据，避免重复真实请求，提升稳定性和效率。
"""
import os

import vcr

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASSETTES_DIR = os.path.join(BASE_DIR, "data", "cassettes")


def make_vcr(cassette_name: str, record_mode: str = "none"):
    """
    创建 VCR 实例。

    :param cassette_name: 录放文件名（不含扩展名）
    :param record_mode:
        "all"   全新录制（首次运行）
        "none"  仅回放，不录制（cassette 已存在时使用，离线可跑）
        "once"  已存在则回放，不存在则录制
    """
    cassette_path = os.path.join(CASSETTES_DIR, f"{cassette_name}.yaml")
    return vcr.VCR(
        cassette_library_dir=CASSETTES_DIR,
        record_mode=record_mode,
        match_on=["method", "scheme", "host", "port", "path", "query"],
    )


def use_cassette(cassette_name: str, record_mode: str = "once"):
    """装饰器形式：给测试函数套上 VCR 录放。"""
    vcr_instance = make_vcr(cassette_name, record_mode)
    return vcr_instance.use_cassette(f"{cassette_name}.yaml")
#（注：内容由AI生成）
