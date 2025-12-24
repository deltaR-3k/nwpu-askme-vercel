# Vercel Python Serverless 入口：直接暴露 Flask app 即可（WSGI 适配由平台处理）
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from rag_backend import app  # noqa: E402
