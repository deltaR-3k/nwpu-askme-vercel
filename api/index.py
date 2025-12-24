import json
import os

import serverless_wsgi

# 确保可以导入项目根目录的模块
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from rag_backend import app  # noqa: E402


def handler(event, context):
    """Vercel Python Serverless 入口"""
    return serverless_wsgi.handle_request(app, event, context)
