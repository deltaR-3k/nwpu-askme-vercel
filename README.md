# 西北工业大学 RAG 智能问答系统

基于RAG（检索增强生成）技术的智能问答系统，整合了西北工业大学相关的各类指南和文档数据，为用户提供准确的校园信息查询服务。

## 功能特性

- 🔍 **文档检索**：基于语义相似度的文档检索功能
- 💬 **智能问答**：结合OpenAI GPT模型的智能问答功能
- 📚 **多源数据**：整合了选课、GPA、转专业、校园生活等多个主题的数据
- 🎨 **现代化UI**：美观、响应式的用户界面
- 🌗 **亮/暗主题**：支持一键切换亮/暗模式，海军蓝系苹果风配色
- ☁️ **线上信息**：前后端托管于 Vercel Serverless，域名 `mymoon.cfd`；环境变量需在 Vercel 中配置 `OPENAI_API_KEY`（可选 `OPENAI_BASE_URL`）；API 路径 `/api/...` 保持不变

## 项目结构

```
.
├── data/                    # 原始数据目录
├── merge_data.py           # 数据合并脚本
├── rag_backend.py          # RAG后端API
├── requirements.txt        # Python依赖
├── index.html              # 前端页面
├── static/
│   ├── css/
│   │   └── style.css      # 样式文件
│   └── js/
│       └── app.js         # 前端JavaScript
└── merged_data.json        # 合并后的数据文件（运行merge_data.py后生成）
```

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 合并数据

运行数据合并脚本，将原始JSON数据统一处理：

```bash
python merge_data.py
```

这将生成 `merged_data.json` 文件。

### 3. 配置OpenAI API Key

创建 `.env` 文件（或在环境变量中设置）：

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. 启动后端服务

```bash
python rag_backend.py
```

后端服务将在 `http://localhost:5000` 启动。

**注意**：首次运行时会使用OpenAI API为所有文档生成嵌入向量，需要有效的API Key和网络连接。

### 5. 打开前端页面

在浏览器中打开 `index.html` 文件，或使用简单的HTTP服务器：

```bash
# Python 3
python -m http.server 8000

# 然后访问 http://localhost:8000
```

## 使用说明

1. **搜索文档**：输入关键词，点击"搜索文档"按钮，系统会返回相关的文档列表
2. **智能问答**：输入问题，点击"智能问答"按钮，系统会基于相关文档生成答案
3. **调整返回数量**：可以通过"返回文档数"选项调整检索的文档数量（1-20）

## API接口

### GET /api/health
健康检查接口

**响应**：
```json
{
  "status": "healthy",
  "document_count": 74
}
```

### POST /api/search
文档搜索接口

**请求体**：
```json
{
  "query": "如何选课？",
  "top_k": 5
}
```

**响应**：
```json
{
  "query": "如何选课？",
  "documents": [...],
  "count": 5
}
```

### POST /api/chat
智能问答接口

**请求体**：
```json
{
  "query": "如何选课？",
  "top_k": 5
}
```

**响应**：
```json
{
  "query": "如何选课？",
  "answer": "根据选课办法...",
  "sources": [...]
}
```

## 技术栈

- **后端**：
  - Flask：Web框架
  - OpenAI API：
    - GPT-3.5-turbo：用于生成答案
    - text-embedding-3-small：用于文本向量化（嵌入）
  - NumPy：向量计算和相似度计算

- **前端**：
  - HTML/CSS/JavaScript：原生前端技术
  - 响应式设计：支持移动端

## 数据说明

系统整合了以下数据源：

- 学术指南 (academic_guide.json)
- 入学指南 (admission_guide.json)
- 选课办法 (course_selection.json)
- GPA计算办法 (GPA.json)
- 转专业办法 (transfer_major.json)
- 校园生活指南 (living_guide.json)
- 以及其他相关文档

## 注意事项

1. 需要有效的OpenAI API Key才能使用系统功能（包括文档嵌入和智能问答）
2. 首次运行时会调用OpenAI API为所有文档生成嵌入向量，会产生API费用
3. 文档嵌入会在启动时生成并缓存在内存中，后续启动无需重新生成（除非数据更新）
4. 每次搜索/问答都会为查询文本生成嵌入向量，也会产生API费用

## 许可证

本项目仅供学习和研究使用。
