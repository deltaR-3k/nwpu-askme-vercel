// RAG系统前端JavaScript
// 使用相对路径，自动适配当前服务器的端口
const API_BASE_URL = '/api';

// DOM元素
const searchForm = document.getElementById('searchForm');
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const chatButton = document.getElementById('chatButton');
const clearChatButton = document.getElementById('clearChatButton');
const topKInput = document.getElementById('topK');
const loadingDiv = document.getElementById('loading');
const resultsContainer = document.getElementById('resultsContainer');
const chatHistorySection = document.getElementById('chatHistorySection');
const chatHistoryList = document.getElementById('chatHistoryList');
const answerSection = document.getElementById('answerSection');
const answerContent = document.getElementById('answerContent');
const sourcesSection = document.getElementById('sourcesSection');
const sourcesList = document.getElementById('sourcesList');
const errorMessage = document.getElementById('errorMessage');
const promptChips = document.querySelectorAll('.prompt-chip');
const themeToggle = document.getElementById('themeToggle');

// 对话历史
let conversationHistory = [];

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 绑定搜索表单提交事件
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        performSearch();
    });

    // 绑定搜索按钮点击事件
    searchButton.addEventListener('click', performSearch);
    
    // 绑定聊天按钮点击事件
    chatButton.addEventListener('click', performChat);
    
    // 绑定清除对话按钮
    clearChatButton.addEventListener('click', clearChatHistory);

    // 绑定回车键（聊天模式下发送消息，搜索模式下搜索）
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            // 如果已有对话历史，默认使用聊天模式
            if (conversationHistory.length > 0) {
                performChat();
            } else {
                performSearch();
            }
        }
    });

    // 快捷提示填充输入框
    promptChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const prompt = chip.dataset.prompt || chip.textContent.trim();
            searchInput.value = prompt;
            searchInput.focus();
        });
    });

    // 检查后端健康状态
    checkHealth();

    // 主题加载与切换
    initTheme();
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
});

function initTheme() {
    const saved = localStorage.getItem('npu-theme');
    const isDark = saved === 'dark';
    document.body.classList.toggle('theme-dark', isDark);
    updateThemeToggleIcon(isDark);
}

function toggleTheme() {
    const isDark = document.body.classList.toggle('theme-dark');
    localStorage.setItem('npu-theme', isDark ? 'dark' : 'light');
    updateThemeToggleIcon(isDark);
}

function updateThemeToggleIcon(isDark) {
    if (!themeToggle) return;
    themeToggle.textContent = isDark ? '🌙' : '☀️';
    themeToggle.setAttribute('aria-label', isDark ? '切换到亮色' : '切换到暗色');
}

// 检查后端健康状态
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('后端状态:', data);
    } catch (error) {
        console.error('无法连接到后端:', error);
        showError('无法连接到后端服务器，请确保后端服务已启动');
    }
}

// 显示错误信息
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('active');
    setTimeout(() => {
        errorMessage.classList.remove('active');
    }, 5000);
}

// 显示加载状态
function showLoading() {
    loadingDiv.classList.add('active');
    resultsContainer.classList.remove('active');
    searchButton.disabled = true;
    chatButton.disabled = true;
    errorMessage.classList.remove('active');
}

// 隐藏加载状态
function hideLoading() {
    loadingDiv.classList.remove('active');
    searchButton.disabled = false;
    chatButton.disabled = false;
}

// 执行搜索
async function performSearch() {
    const query = searchInput.value.trim();
    if (!query) {
        showError('请输入搜索内容');
        return;
    }

    showLoading();

    try {
        const topK = parseInt(topKInput.value) || 5;
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                top_k: topK
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displaySearchResults(data);
    } catch (error) {
        console.error('搜索错误:', error);
        showError('搜索失败: ' + error.message);
        hideLoading();
    }
}

// 执行RAG聊天
async function performChat() {
    const query = searchInput.value.trim();
    if (!query) {
        showError('请输入问题');
        return;
    }

    showLoading();

    // 先更新UI显示用户消息（但暂时不添加到conversationHistory）
    addMessageToHistory('user', query);

    // 清空输入框
    const currentQuery = query;
    searchInput.value = '';

    try {
        const topK = parseInt(topKInput.value) || 5;
        
        // 准备发送给后端的对话历史（不包括当前消息）
        const historyForAPI = conversationHistory.map(msg => ({
            role: msg.role,
            content: msg.content
        }));
        
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: currentQuery,
                top_k: topK,
                history: historyForAPI  // 发送之前的对话历史，不包括当前消息
            })
        });

        if (!response.ok) {
            // 尝试获取详细的错误信息
            let errorMsg = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData.error) {
                    errorMsg = errorData.error;
                }
            } catch (e) {
                // 如果无法解析错误响应，使用默认错误信息
            }
            throw new Error(errorMsg);
        }

        const data = await response.json();
        
        // 检查返回的数据中是否包含错误
        if (data.error) {
            throw new Error(data.error);
        }
        
        // 收到回复后，将用户消息和助手回复都添加到对话历史
        conversationHistory.push({
            role: 'user',
            content: currentQuery
        });
        conversationHistory.push({
            role: 'assistant',
            content: data.answer
        });
        
    // 更新UI显示助手回复（用户消息已经在上面显示了）
    addMessageToHistory('assistant', data.answer);
    displayChatResults(data);
    } catch (error) {
        console.error('聊天错误:', error);
        showError('生成回答失败: ' + error.message);
        // 如果出错，移除刚才显示的用户消息（从UI中移除）
        const lastMessage = chatHistoryList.lastElementChild;
        if (lastMessage && lastMessage.classList.contains('user')) {
            lastMessage.remove();
        }
        hideLoading();
    }
}

// 添加消息到对话历史显示
function addMessageToHistory(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    
    const headerDiv = document.createElement('div');
    headerDiv.className = 'chat-message-header';
    headerDiv.textContent = role === 'user' ? '👤 您' : '🤖 助手';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'chat-message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(headerDiv);
    messageDiv.appendChild(contentDiv);
    // 最新消息插入顶部
    chatHistoryList.prepend(messageDiv);
    
    // 显示对话历史区域
    chatHistorySection.style.display = 'block';
    clearChatButton.style.display = 'inline-block';
}

// 更新对话历史显示
function updateChatHistoryDisplay() {
    chatHistoryList.innerHTML = '';
    // 倒序展示，最新在上
    [...conversationHistory].reverse().forEach(msg => {
        addMessageToHistory(msg.role, msg.content);
    });
}

// 清除对话历史
function clearChatHistory() {
    conversationHistory = [];
    chatHistoryList.innerHTML = '';
    chatHistorySection.style.display = 'none';
    clearChatButton.style.display = 'none';
    answerSection.style.display = 'none';
    sourcesSection.style.display = 'none';
    resultsContainer.classList.remove('active');
    searchInput.focus();
}

// 显示搜索结果
function displaySearchResults(data) {
    hideLoading();
    resultsContainer.classList.add('active');
    resultsContainer.classList.add('fade-in');
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // 隐藏对话历史和答案区域（搜索模式）
    chatHistorySection.style.display = 'none';
    answerSection.style.display = 'none';
    clearChatButton.style.display = 'none';

    // 显示源文档列表
    sourcesSection.style.display = 'block';
    sourcesList.innerHTML = '';

    if (data.documents && data.documents.length > 0) {
        data.documents.forEach((doc, index) => {
            const sourceItem = createSourceItem(doc, index + 1);
            sourcesList.appendChild(sourceItem);
        });
    } else {
        sourcesList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <h3>未找到相关文档</h3>
                <p>请尝试使用其他关键词搜索</p>
            </div>
        `;
    }
}

// 显示聊天结果（显示最新回答和源文档）
function displayChatResults(data) {
    hideLoading();
    resultsContainer.classList.add('active');
    resultsContainer.classList.add('fade-in');
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // 仅保留对话气泡显示，隐藏摘要卡片
    answerSection.style.display = 'none';

    // 显示源文档
    sourcesSection.style.display = 'block';
    sourcesList.innerHTML = '';

    if (data.sources && data.sources.length > 0) {
        data.sources.forEach((source, index) => {
            const sourceItem = createSourceItem(source, index + 1, true);
            sourcesList.appendChild(sourceItem);
        });
    }
}

// 创建源文档项
function createSourceItem(doc, index, isChatMode = false) {
    const item = document.createElement('div');
    item.className = 'source-item fade-in';
    item.style.animationDelay = `${index * 0.1}s`;

    const title = doc.title || '无标题';
    const category = doc.category || '未分类';
    const source = doc.source || '未知来源';
    const similarity = doc.similarity ? (doc.similarity * 100).toFixed(1) : null;
    const rawContent = doc.content || doc.text || doc.chunk || '';
    const content = typeof rawContent === 'string' ? rawContent : JSON.stringify(rawContent);
    const isLong = content && content.length > 0;

    item.innerHTML = `
        <div class="source-header">
            <div class="source-title">${index}. ${escapeHtml(title)}</div>
        </div>
        <div class="source-meta">
            <span class="source-tag source-category">${escapeHtml(category)}</span>
            <span class="source-tag">来源: ${escapeHtml(source)}</span>
            ${similarity ? `<span class="source-tag source-similarity">相似度: ${similarity}%</span>` : ''}
        </div>
        ${content ? `<div class="source-content">${escapeHtml(content.substring(0, 300))}${content.length > 300 ? '...' : ''}</div>` : ''}
    `;

    // 点击展开/折叠内容（聊天/搜索都可用）
    if (isLong) {
        item.addEventListener('click', () => {
            const contentDiv = item.querySelector('.source-content');
            if (!contentDiv) return;
            const expanded = contentDiv.classList.toggle('expanded');
            if (expanded) {
                contentDiv.textContent = escapeHtml(content);
            } else {
                contentDiv.textContent = escapeHtml(content.substring(0, 300)) + (content.length > 300 ? '...' : '');
            }
        });
    }

    return item;
}

// HTML转义函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

