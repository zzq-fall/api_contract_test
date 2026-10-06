# -*- coding: utf-8 -*-
"""
项目执行入口（契约测试）：
    1. 启动本地 mock 服务器（可选，--mock）
    2. 运行 pytest 契约测试，生成 allure 结果
用法：
    python run.py            # 仅执行测试
    python run.py --mock     # 先启动 mock 再执行
"""
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    mock = None
    if "--mock" in sys.argv:
        print(">> 启动 mock 服务器...")
        mock = subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "scripts", "mock_server.py")])
        import time
        time.sleep(1)

    print(">> 执行契约测试并生成 allure 结果...")
    code = subprocess.call([
        sys.executable, "-m", "pytest",
        os.path.join(BASE_DIR, "case"),
        "-s",
        "--alluredir", os.path.join(BASE_DIR, "report", "allure-result"),
    ])

    if mock is not None:
        mock.terminate()

    sys.exit(code)
#（注：内容由AI生成）
