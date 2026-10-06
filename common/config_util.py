# -*- coding: utf-8 -*-
"""配置文件读取封装：读取 conf/conf.ini 中的配置"""
import configparser
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF_PATH = os.path.join(BASE_DIR, "conf", "conf.ini")


class ConfigUtil:
    """conf.ini 配置读取工具"""

    _conf = None

    @classmethod
    def _load(cls):
        if cls._conf is None:
            cls._conf = configparser.ConfigParser()
            cls._conf.read(CONF_PATH, encoding="utf-8")
        return cls._conf

    @classmethod
    def get(cls, section: str, option: str, fallback: str = None) -> str:
        try:
            return cls._load().get(section, option)
        except Exception:
            return fallback

    @classmethod
    def base_url(cls) -> str:
        return cls.get("environment", "base_url", "http://127.0.0.1:9000")

    @classmethod
    def timeout(cls) -> float:
        return float(cls.get("request", "timeout", "10"))

    @classmethod
    def sla_ms(cls) -> int:
        return int(cls.get("assert", "sla_ms", "3000"))
