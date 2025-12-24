@echo off
chcp 65001 >nul
echo ========================================
echo 西北工业大学 RAG 智能问答系统
echo ========================================
echo.
echo 正在启动后端服务...
echo 请确保已安装所有依赖: pip install -r requirements.txt
echo 请确保已设置 OPENAI_API_KEY 环境变量或在 .env 文件中配置
echo.
python rag_backend.py
pause

