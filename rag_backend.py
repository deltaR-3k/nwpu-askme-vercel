"""
RAG系统后端：基于OpenAI API的检索增强生成系统
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# 初始化OpenAI客户端
openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
openai_base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
if not openai_api_key:
    raise ValueError("请设置OPENAI_API_KEY环境变量")

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_base_url
)

# OpenAI嵌入模型名称
# text-embedding-3-small: 1536维，性能更好
# text-embedding-ada-002: 1536维，稳定可靠
EMBEDDING_MODEL = "text-embedding-3-small"

# 嵌入向量缓存文件
EMBEDDINGS_CACHE_FILE = 'document_embeddings.npy'
EMBEDDINGS_METADATA_FILE = 'embeddings_metadata.json'

# 加载合并后的数据
def load_documents():
    """加载合并后的文档数据"""
    with open('merged_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

documents = load_documents()
print(f"已加载 {len(documents)} 条文档")

# 生成文档嵌入
def generate_embeddings(texts: List[str], batch_size: int = 100) -> np.ndarray:
    """使用OpenAI API生成文本嵌入向量"""
    all_embeddings = []
    embedding_dim = None  # 动态获取维度
    
    print(f"正在使用OpenAI API生成 {len(texts)} 条文档的嵌入向量...")
    print(f"使用模型: {EMBEDDING_MODEL}")
    
    # 批量处理，避免一次请求过多（OpenAI API限制最大2048条）
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=batch
            )
            # 提取嵌入向量
            batch_embeddings = [item.embedding for item in response.data]
            if embedding_dim is None and batch_embeddings:
                embedding_dim = len(batch_embeddings[0])
            all_embeddings.extend(batch_embeddings)
            print(f"  已处理 {min(i + batch_size, len(texts))}/{len(texts)} 条文档")
        except Exception as e:
            print(f"  警告: 处理批次 {i//batch_size + 1} 时出错: {str(e)}")
            # 如果批次失败，尝试逐条处理
            for text in batch:
                try:
                    response = client.embeddings.create(
                        model=EMBEDDING_MODEL,
                        input=[text]
                    )
                    embedding = response.data[0].embedding
                    if embedding_dim is None:
                        embedding_dim = len(embedding)
                    all_embeddings.append(embedding)
                except Exception as e2:
                    print(f"    错误: 处理单条文档时出错: {str(e2)}")
                    # 如果仍然失败，使用零向量作为占位符
                    if embedding_dim is None:
                        embedding_dim = 1536  # 默认维度
                    all_embeddings.append([0.0] * embedding_dim)
    
    if not all_embeddings:
        raise ValueError("未能生成任何嵌入向量，请检查API配置和网络连接")
    
    print(f"嵌入向量维度: {embedding_dim}")
    return np.array(all_embeddings, dtype=np.float32)

def get_query_embedding(query: str) -> np.ndarray:
    """获取查询文本的嵌入向量"""
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[query]
        )
        if not response or not response.data or len(response.data) == 0:
            raise ValueError("API返回的嵌入向量为空")
        return np.array(response.data[0].embedding, dtype=np.float32)
    except Exception as e:
        print(f"获取查询嵌入向量时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def load_embeddings() -> Tuple[bool, Optional[np.ndarray]]:
    """
    尝试加载缓存的嵌入向量
    返回: (是否成功, 嵌入向量数组)
    """
    if not os.path.exists(EMBEDDINGS_CACHE_FILE) or not os.path.exists(EMBEDDINGS_METADATA_FILE):
        return False, None
    
    try:
        # 加载元数据
        with open(EMBEDDINGS_METADATA_FILE, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # 检查元数据是否匹配
        if metadata.get('document_count') != len(documents):
            print(f"文档数量不匹配（缓存: {metadata.get('document_count')}, 当前: {len(documents)}），需要重新生成")
            return False, None
        
        if metadata.get('model') != EMBEDDING_MODEL:
            print(f"嵌入模型不匹配（缓存: {metadata.get('model')}, 当前: {EMBEDDING_MODEL}），需要重新生成")
            return False, None
        
        # 检查数据哈希（可选，用于检测数据是否变更）
        import hashlib
        document_hash = hashlib.md5(json.dumps([doc['content'] for doc in documents], ensure_ascii=False).encode('utf-8')).hexdigest()
        if metadata.get('content_hash') != document_hash:
            print("文档内容已变更，需要重新生成嵌入向量")
            return False, None
        
        # 加载嵌入向量
        embeddings = np.load(EMBEDDINGS_CACHE_FILE)
        print(f"✓ 成功加载缓存的嵌入向量，维度: {embeddings.shape}")
        print(f"  模型: {metadata.get('model')}, 文档数: {metadata.get('document_count')}")
        return True, embeddings
        
    except Exception as e:
        print(f"加载缓存嵌入向量时出错: {str(e)}，将重新生成")
        return False, None

def save_embeddings(embeddings: np.ndarray):
    """保存嵌入向量到文件"""
    try:
        # 保存嵌入向量
        np.save(EMBEDDINGS_CACHE_FILE, embeddings)
        
        # 保存元数据
        import hashlib
        document_hash = hashlib.md5(json.dumps([doc['content'] for doc in documents], ensure_ascii=False).encode('utf-8')).hexdigest()
        metadata = {
            'model': EMBEDDING_MODEL,
            'document_count': len(documents),
            'embedding_dim': embeddings.shape[1] if len(embeddings.shape) > 1 else embeddings.shape[0],
            'content_hash': document_hash,
            'created_at': str(Path(EMBEDDINGS_CACHE_FILE).stat().st_mtime)
        }
        
        with open(EMBEDDINGS_METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 嵌入向量已保存到 {EMBEDDINGS_CACHE_FILE}")
        
    except Exception as e:
        print(f"保存嵌入向量时出错: {str(e)}")

# 加载或生成文档嵌入（Serverless 环境仅允许读取缓存）
print("\n正在加载文档嵌入向量...")
loaded, document_embeddings = load_embeddings()

if not loaded or document_embeddings is None:
    raise RuntimeError(
        "未找到可用的文档嵌入缓存，请先在本地生成 document_embeddings.npy 和 embeddings_metadata.json 后再部署。"
    )

print(f"✓ 使用缓存的嵌入向量，维度: {document_embeddings.shape}")

def cosine_similarity(vec1, vec2):
    """计算余弦相似度"""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def search_relevant_documents(query: str, top_k: int = 5) -> List[Dict]:
    """根据查询检索相关文档"""
    # 验证 document_embeddings 是否有效
    if document_embeddings is None or not isinstance(document_embeddings, np.ndarray):
        raise ValueError("文档嵌入向量未正确初始化，无法进行搜索")
    
    # 使用OpenAI API生成查询的嵌入向量
    query_embedding = get_query_embedding(query)
    
    # 计算与所有文档的相似度
    similarities = []
    for i, doc_embedding in enumerate(document_embeddings):
        similarity = cosine_similarity(query_embedding, doc_embedding)
        similarities.append((similarity, i))
    
    # 按相似度排序，取前top_k个
    similarities.sort(reverse=True, key=lambda x: x[0])
    top_indices = [idx for _, idx in similarities[:top_k]]
    
    # 返回相关文档
    results = []
    for similarity_score, idx in similarities[:top_k]:
        doc = documents[idx].copy()
        doc['similarity'] = float(similarity_score)
        results.append(doc)
    
    return results

def generate_answer(query: str, context_docs: List[Dict], conversation_history: List[Dict] = None) -> str:
    """使用OpenAI API生成答案，支持多轮对话"""
    try:
        # 构建上下文
        context = "\n\n".join([f"文档{i+1}:\n{doc['content']}" for i, doc in enumerate(context_docs)])
        
        # 构建系统提示词
        system_message = """你是一个专业的大学信息助手，擅长回答关于西北工业大学的各种问题。
请根据提供的相关文档内容回答用户的问题（不要明确说根据哪个文档回答，要更加自然）。
回答要求：
1. 回答要准确、详细
2. 如果涉及多个文档的信息，请综合回答
3. 使用中文回答
4. 回答要友好、易懂
5. 如果用户的问题是基于之前的对话，请结合对话历史来理解问题"""
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_message}]
        
        # 添加对话历史（如果有）
        if conversation_history:
            # 限制历史记录长度，避免token过多（保留最近10轮对话，即20条消息）
            max_history_messages = 20
            recent_history = conversation_history[-max_history_messages:]
            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role in ["user", "assistant"] and content and content.strip():
                    messages.append({
                        "role": role,
                        "content": content
                    })
        
        # 添加当前问题的上下文和查询
        user_content = f"""相关文档内容：
{context}

用户问题：{query}

请根据上述文档内容回答用户的问题。"""
        
        messages.append({"role": "user", "content": user_content})
        
        # 调用API生成答案
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1500  # 增加token限制以支持更长的回答
        )
        
        if not response or not response.choices or len(response.choices) == 0:
            raise ValueError("API返回的答案为空")
        
        answer = response.choices[0].message.content
        if not answer:
            raise ValueError("API返回的答案内容为空")
        
        return answer
        
    except Exception as e:
        error_msg = f"生成答案时出错: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        raise Exception(error_msg)

@app.route('/api/search', methods=['POST'])
def search():
    """搜索接口"""
    try:
        data = request.json
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({'error': '查询内容不能为空'}), 400
        
        # 检索相关文档
        relevant_docs = search_relevant_documents(query, top_k)
        
        return jsonify({
            'query': query,
            'documents': relevant_docs,
            'count': len(relevant_docs)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """RAG聊天接口，支持多轮对话"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
            
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        conversation_history = data.get('history', [])  # 接收对话历史
        
        if not query:
            return jsonify({'error': '查询内容不能为空'}), 400
        
        # 验证对话历史格式
        if conversation_history and not isinstance(conversation_history, list):
            conversation_history = []
        
        # 检索相关文档
        try:
            relevant_docs = search_relevant_documents(query, top_k)
        except Exception as e:
            print(f"检索文档时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'检索文档失败: {str(e)}'}), 500
        
        # 生成答案（传入对话历史）
        try:
            answer = generate_answer(query, relevant_docs, conversation_history)
        except Exception as e:
            print(f"生成答案时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'生成答案失败: {str(e)}'}), 500
        
        return jsonify({
            'query': query,
            'answer': answer,
            'sources': [
                {
                    'title': doc['title'],
                    'category': doc.get('category', ''),
                    'source': doc.get('source', ''),
                    'similarity': doc.get('similarity', 0)
                }
                for doc in relevant_docs
            ]
        })
    except Exception as e:
        print(f"聊天接口出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@app.route('/')
def index():
    """首页"""
    return send_from_directory('.', 'index.html')

@app.route('/api/health', methods=['GET'])
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'document_count': len(documents)
    })

if __name__ == '__main__':
    # 尝试使用不同端口，避免端口冲突
    import socket
    
    def find_free_port(start_port=8080):
        """查找可用端口"""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        raise RuntimeError("无法找到可用端口（请检查8080-8179范围内的端口）")
    
    try:
        port = find_free_port(8080)
        print("\n" + "="*50)
        print("RAG系统后端启动中...")
        print("="*50)
        print(f"已加载 {len(documents)} 条文档")
        print(f"\n服务器运行在: http://127.0.0.1:{port}")
        print(f"前端访问地址: http://127.0.0.1:{port}")
        print(f"API地址: http://127.0.0.1:{port}/api")
        print("="*50 + "\n")
        app.run(host='127.0.0.1', port=port, debug=True)
    except Exception as e:
        print(f"\n启动失败: {str(e)}")
        print("请检查端口占用情况或使用管理员权限运行")

