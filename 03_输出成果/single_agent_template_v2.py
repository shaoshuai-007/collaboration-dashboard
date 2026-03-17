SINGLE_AGENT_PAGE_V2 = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>单智能体工作区 - 指南针工程</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --primary: #C93832;
            --secondary: #006EBD;
            --bg-main: #f5f7fa;
            --bg-card: #ffffff;
            --text-primary: #1a1a1a;
            --text-secondary: #666;
            --border: #e0e0e0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: var(--bg-main);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        /* 顶部导航 */
        .header {
            background: linear-gradient(135deg, var(--primary), #A02820);
            color: white;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .logo { font-size: 18px; font-weight: bold; }
        
        .mode-badge {
            background: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 12px;
        }
        
        .header-nav { display: flex; gap: 12px; }
        
        .header-nav a {
            color: white;
            text-decoration: none;
            padding: 6px 14px;
            border-radius: 6px;
            background: rgba(255,255,255,0.15);
            font-size: 13px;
        }
        
        .header-nav a:hover { background: rgba(255,255,255,0.25); }
        
        /* 主内容区 */
        .main-container {
            flex: 1;
            display: flex;
            overflow: hidden;
        }
        
        /* 左侧专家选择 */
        .sidebar {
            width: 260px;
            background: var(--bg-card);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }
        
        .sidebar-header {
            padding: 16px;
            border-bottom: 1px solid var(--border);
            font-weight: bold;
            font-size: 14px;
            color: var(--text-secondary);
        }
        
        .agent-list {
            flex: 1;
            overflow-y: auto;
            padding: 8px;
        }
        
        .agent-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 4px;
            border: 2px solid transparent;
        }
        
        .agent-item:hover { background: #f0f2f5; }
        
        .agent-item.active {
            background: #e8f4ff;
            border-color: var(--secondary);
        }
        
        .agent-avatar {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: white;
            flex-shrink: 0;
        }
        
        .agent-info { flex: 1; min-width: 0; }
        
        .agent-name {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .agent-role {
            font-size: 11px;
            color: var(--text-secondary);
            margin-top: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        /* 右侧对话区 */
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: var(--bg-card);
            min-width: 0;
        }
        
        /* 专家信息区 */
        .agent-info-panel {
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
            display: none;
        }
        
        .agent-info-panel.show { display: block; }
        
        .agent-intro {
            display: flex;
            gap: 16px;
            align-items: flex-start;
        }
        
        .agent-intro-avatar {
            width: 56px;
            height: 56px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            color: white;
            flex-shrink: 0;
        }
        
        .agent-intro-content { flex: 1; }
        
        .agent-intro-name {
            font-size: 18px;
            font-weight: bold;
            color: var(--text-primary);
        }
        
        .agent-intro-role {
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }
        
        .agent-intro-desc {
            font-size: 13px;
            color: var(--text-primary);
            line-height: 1.6;
            margin-bottom: 12px;
        }
        
        .agent-expertise {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 12px;
        }
        
        .expertise-tag {
            background: #f0f2f5;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            color: var(--text-secondary);
        }
        
        .agent-guidance {
            background: #fff8e6;
            border-left: 3px solid #ffc107;
            padding: 10px 14px;
            font-size: 12px;
            color: #856404;
            line-height: 1.6;
            white-space: pre-line;
        }
        
        /* 消息区 */
        .messages-area {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .message {
            display: flex;
            gap: 10px;
            max-width: 85%;
        }
        
        .message.user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }
        
        .message-avatar {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: white;
            flex-shrink: 0;
        }
        
        .message-content {
            padding: 12px 16px;
            border-radius: 12px;
            line-height: 1.6;
            font-size: 14px;
        }
        
        .message.user .message-content {
            background: var(--secondary);
            color: white;
        }
        
        .message.agent .message-content {
            background: #f0f2f5;
            color: var(--text-primary);
        }
        
        .message.system .message-content {
            background: #fff3e0;
            color: #e65100;
            text-align: center;
            font-size: 12px;
            max-width: 100%;
        }
        
        /* 输入区 - 固定底部 */
        .input-area {
            padding: 12px 16px;
            border-top: 1px solid var(--border);
            display: flex;
            gap: 10px;
            background: var(--bg-card);
            flex-shrink: 0;
        }
        
        .input-area textarea {
            flex: 1;
            padding: 10px 14px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 14px;
            resize: none;
            font-family: inherit;
            min-height: 42px;
            max-height: 120px;
        }
        
        .input-area textarea:focus {
            outline: none;
            border-color: var(--secondary);
        }
        
        .send-btn {
            padding: 10px 24px;
            background: linear-gradient(135deg, var(--secondary), #005a9e);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }
        
        .send-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0, 110, 189, 0.3);
        }
        
        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        /* 欢迎提示 */
        .welcome-tip {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
            text-align: center;
            padding: 40px;
        }
        
        .welcome-tip .icon { font-size: 48px; margin-bottom: 16px; }
        .welcome-tip h3 { font-size: 18px; color: var(--text-primary); margin-bottom: 8px; }
        .welcome-tip p { font-size: 14px; }
        
        /* 打字动画 */
        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 6px 10px;
        }
        
        .typing-indicator span {
            width: 6px;
            height: 6px;
            background: #999;
            border-radius: 50%;
            animation: typing 1s infinite;
        }
        
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-left">
            <div class="logo">🧭 指南针工程</div>
            <div class="mode-badge">👤 单智能体模式</div>
        </div>
        <div class="header-nav">
            <a href="/">返回首页</a>
            <a href="/multi">切换多智能体</a>
        </div>
    </header>
    
    <div class="main-container">
        <div class="sidebar">
            <div class="sidebar-header">⭐ 选择专家顾问</div>
            <div class="agent-list" id="agentList"></div>
        </div>
        
        <div class="chat-container">
            <div class="agent-info-panel" id="agentInfoPanel"></div>
            
            <div class="messages-area" id="messagesArea">
                <div class="welcome-tip" id="welcomeTip">
                    <div class="icon">👈</div>
                    <h3>请选择一位专家开始对话</h3>
                    <p>点击左侧专家卡片即可开始一对一咨询</p>
                </div>
            </div>
            
            <div class="input-area">
                <textarea id="messageInput" placeholder="输入您的问题..." rows="1" disabled></textarea>
                <button class="send-btn" id="sendBtn" onclick="sendMessage()" disabled>发送</button>
            </div>
        </div>
    </div>
    
    <script>
        // Agent详细信息（从后端获取）
        const AGENTS = {
            'caiwei': { name: '采薇', role: '需求分析专家', emoji: '🌸', color: '#409EFF' },
            'zhijin': { name: '织锦', role: '架构设计师', emoji: '🧵', color: '#67C23A' },
            'zhutai': { name: '筑台', role: '售前工程师', emoji: '🏗️', color: '#E6A23C' },
            'chengcai': { name: '呈彩', role: '方案设计师', emoji: '🎨', color: '#FF9800' },
            'yuheng': { name: '玉衡', role: '项目经理', emoji: '⚖️', color: '#F56C6C' },
            'gongchi': { name: '工尺', role: '系统设计师', emoji: '📐', color: '#607D8B' },
            'zhegui': { name: '折桂', role: '资源管家', emoji: '📚', color: '#00BCD4' },
            'fuyao': { name: '扶摇', role: '总指挥', emoji: '🌀', color: '#165DFF' },
            'nanqiao': { name: '南乔', role: '智能助手', emoji: '🌿', color: '#9C27B0' }
        };
        
        let currentAgent = null;
        let conversations = {};
        let isProcessing = false;
        
        // 渲染Agent列表
        function renderAgentList() {
            const container = document.getElementById('agentList');
            container.innerHTML = '';
            
            const order = ['caiwei', 'zhijin', 'zhutai', 'chengcai', 'yuheng', 'gongchi', 'zhegui', 'fuyao', 'nanqiao'];
            
            order.forEach(id => {
                const agent = AGENTS[id];
                const item = document.createElement('div');
                item.className = 'agent-item' + (currentAgent === id ? ' active' : '');
                item.onclick = () => selectAgent(id);
                item.innerHTML = `
                    <div class="agent-avatar" style="background: ${agent.color}">${agent.emoji}</div>
                    <div class="agent-info">
                        <div class="agent-name">${agent.name}</div>
                        <div class="agent-role">${agent.role}</div>
                    </div>
                `;
                container.appendChild(item);
            });
        }
        
        // 选择Agent（支持切换）
        async function selectAgent(agentId) {
            if (isProcessing) return;
            
            const prevAgent = currentAgent;
            currentAgent = agentId;
            
            // 保存上一个Agent的对话
            if (prevAgent && conversations[prevAgent]) {
                // 已保存
            }
            
            // 初始化当前Agent的对话
            if (!conversations[agentId]) {
                conversations[agentId] = [];
            }
            
            const agent = AGENTS[agentId];
            
            // 更新UI
            renderAgentList();
            document.getElementById('welcomeTip').style.display = 'none';
            document.getElementById('messageInput').disabled = false;
            document.getElementById('sendBtn').disabled = false;
            
            // 加载专家详细信息
            loadAgentInfo(agentId);
            
            // 渲染历史消息
            renderMessages();
        }
        
        // 加载专家详细信息
        async function loadAgentInfo(agentId) {
            try {
                const response = await fetch(`/api/agent/info/${agentId}`);
                const result = await response.json();
                
                if (result.status === 'ok') {
                    const agent = result.agent;
                    const panel = document.getElementById('agentInfoPanel');
                    panel.className = 'agent-info-panel show';
                    panel.innerHTML = `
                        <div class="agent-intro">
                            <div class="agent-intro-avatar" style="background: ${agent.color}">${agent.emoji}</div>
                            <div class="agent-intro-content">
                                <div class="agent-intro-name">${agent.name}</div>
                                <div class="agent-intro-role">${agent.role}</div>
                                <div class="agent-intro-desc">${agent.introduction}</div>
                                <div class="agent-expertise">
                                    ${agent.expertise.map(e => `<span class="expertise-tag">${e}</span>`).join('')}
                                </div>
                                <div class="agent-guidance">${agent.guidance}</div>
                            </div>
                        </div>
                    `;
                }
            } catch (e) {
                console.error('加载专家信息失败', e);
            }
        }
        
        // 渲染消息
        function renderMessages() {
            const area = document.getElementById('messagesArea');
            const msgs = conversations[currentAgent] || [];
            
            // 保留欢迎提示如果还没有消息
            if (msgs.length === 0) {
                area.innerHTML = '';
                return;
            }
            
            area.innerHTML = '';
            
            msgs.forEach(msg => {
                const msgDiv = document.createElement('div');
                msgDiv.className = 'message ' + msg.type;
                
                if (msg.type === 'user') {
                    msgDiv.innerHTML = `
                        <div class="message-avatar" style="background: #595959;">👤</div>
                        <div class="message-content">${escapeHtml(msg.content)}</div>
                    `;
                } else if (msg.type === 'agent') {
                    const agent = AGENTS[currentAgent];
                    msgDiv.innerHTML = `
                        <div class="message-avatar" style="background: ${agent.color}">${agent.emoji}</div>
                        <div class="message-content">${escapeHtml(msg.content)}</div>
                    `;
                } else {
                    msgDiv.innerHTML = `<div class="message-content">${msg.content}</div>`;
                    msgDiv.style.maxWidth = '100%';
                }
                
                area.appendChild(msgDiv);
            });
            
            area.scrollTop = area.scrollHeight;
        }
        
        // 发送消息
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message || !currentAgent || isProcessing) return;
            
            // 添加用户消息
            conversations[currentAgent].push({ type: 'user', content: message });
            renderMessages();
            input.value = '';
            
            // 显示加载状态
            isProcessing = true;
            document.getElementById('sendBtn').disabled = true;
            showTyping();
            
            try {
                // 使用流式API
                const response = await fetch('/api/agent/stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        agent_id: currentAgent,
                        message: message,
                        history: conversations[currentAgent].slice(-10).map(m => ({
                            speaker: m.type === 'user' ? 'user' : 'agent',
                            content: m.content
                        }))
                    })
                });
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let fullResponse = '';
                
                hideTyping();
                
                // 创建Agent消息容器
                const area = document.getElementById('messagesArea');
                const agent = AGENTS[currentAgent];
                const msgDiv = document.createElement('div');
                msgDiv.className = 'message agent';
                msgDiv.id = 'current-response';
                msgDiv.innerHTML = `
                    <div class="message-avatar" style="background: ${agent.color}">${agent.emoji}</div>
                    <div class="message-content"></div>
                `;
                area.appendChild(msgDiv);
                
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6);
                            if (data === '[DONE]') {
                                break;
                            }
                            try {
                                const json = JSON.parse(data);
                                if (json.text) {
                                    fullResponse += json.text;
                                    msgDiv.querySelector('.message-content').innerText = fullResponse;
                                    area.scrollTop = area.scrollHeight;
                                }
                            } catch (e) {}
                        }
                    }
                }
                
                // 保存完整响应
                conversations[currentAgent].push({ type: 'agent', content: fullResponse });
                
            } catch (e) {
                hideTyping();
                addMessage('system', '网络错误，请重试');
            }
            
            isProcessing = false;
            document.getElementById('sendBtn').disabled = false;
        }
        
        // 显示/隐藏打字指示器
        function showTyping() {
            const area = document.getElementById('messagesArea');
            const agent = AGENTS[currentAgent];
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message agent';
            typingDiv.id = 'typingIndicator';
            typingDiv.innerHTML = `
                <div class="message-avatar" style="background: ${agent.color}">${agent.emoji}</div>
                <div class="message-content">
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            `;
            area.appendChild(typingDiv);
            area.scrollTop = area.scrollHeight;
        }
        
        function hideTyping() {
            const typing = document.getElementById('typingIndicator');
            if (typing) typing.remove();
        }
        
        function addMessage(type, content) {
            if (!conversations[currentAgent]) {
                conversations[currentAgent] = [];
            }
            conversations[currentAgent].push({ type, content });
            renderMessages();
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML.replace(/\\n/g, '<br>');
        }
        
        // 回车发送
        document.getElementById('messageInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // 自动调整输入框高度
        document.getElementById('messageInput').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
        
        // 初始化
        renderAgentList();
    </script>
</body>
</html>
'''
