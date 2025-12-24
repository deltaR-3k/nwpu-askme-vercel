"""
数据合并脚本：将不同格式的JSON数据统一合并为RAG系统可用的格式
"""
import json
import os
from pathlib import Path

def load_json_file(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        # 如果JSON解析失败，尝试修复常见的转义问题
        print(f"  警告: JSON解析错误，尝试修复...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 修复无效的反斜杠转义（如 \学分 -> \\学分）
            # 但保留有效的转义序列（\n, \t等）
            import re
            # 替换无效的反斜杠转义（后面跟着非转义字符）
            content = re.sub(r'\\(?![nrtbf"\\/])', r'\\\\', content)
            return json.loads(content)

def process_qa_data(data, source_file):
    """处理问答格式的数据（数组格式）"""
    results = []
    for item in data:
        # 合并question、answer和keywords为文档内容
        content = f"问题：{item.get('question', '')}\n\n答案：{item.get('answer', '')}"
        if item.get('keywords'):
            content += f"\n\n关键词：{', '.join(item.get('keywords', []))}"
        
        results.append({
            'id': f"{source_file}_{len(results)}",
            'title': item.get('question', ''),
            'category': item.get('category', ''),
            'content': content,
            'keywords': item.get('keywords', []),
            'source': source_file
        })
    return results

def process_doc_data(data, source_file):
    """处理文档格式的数据（对象格式）"""
    content = f"标题：{data.get('title', '')}\n\n"
    if data.get('docNumber'):
        content += f"文件号：{data.get('docNumber', '')}\n"
    if data.get('authority'):
        content += f"发布单位：{data.get('authority', '')}\n"
    if data.get('date'):
        content += f"发布日期：{data.get('date', '')}\n"
    if data.get('pageRange'):
        content += f"页码范围：{data.get('pageRange', '')}\n"
    content += f"\n内容：\n{data.get('content', '')}"
    
    return [{
        'id': f"{source_file}_0",
        'title': data.get('title', ''),
        'category': data.get('category', ''),
        'content': content,
        'keywords': data.get('tags', []),
        'source': source_file
    }]

def merge_all_data(data_dir='data'):
    """合并所有JSON数据文件"""
    data_dir_path = Path(data_dir)
    all_documents = []
    
    # 排除zip文件
    json_files = [f for f in data_dir_path.glob('*.json')]
    
    for json_file in json_files:
        print(f"正在处理: {json_file.name}")
        try:
            data = load_json_file(json_file)
            source_name = json_file.stem
            
            # 判断数据格式：数组还是对象
            if isinstance(data, list):
                # 数组格式（问答数据）
                documents = process_qa_data(data, source_name)
            elif isinstance(data, dict):
                # 对象格式（文档数据）
                documents = process_doc_data(data, source_name)
            else:
                print(f"警告: {json_file.name} 格式不支持，跳过")
                continue
            
            all_documents.extend(documents)
            print(f"  - 成功处理 {len(documents)} 条记录")
            
        except Exception as e:
            print(f"错误: 处理 {json_file.name} 时出错: {str(e)}")
            continue
    
    return all_documents

def main():
    """主函数"""
    print("开始合并数据...")
    documents = merge_all_data('data')
    
    # 保存合并后的数据
    output_file = 'merged_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据合并完成！")
    print(f"总共合并了 {len(documents)} 条文档")
    print(f"输出文件: {output_file}")
    
    # 统计信息
    categories = {}
    sources = {}
    for doc in documents:
        cat = doc.get('category', '未知')
        categories[cat] = categories.get(cat, 0) + 1
        src = doc.get('source', '未知')
        sources[src] = sources.get(src, 0) + 1
    
    print(f"\n分类统计:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count} 条")
    
    print(f"\n来源统计:")
    for src, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"  {src}: {count} 条")

if __name__ == '__main__':
    main()

