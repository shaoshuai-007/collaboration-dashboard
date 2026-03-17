SINGLE_AGENT_PAGE_V3 = '''
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
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: #f5f7fa;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        /* 顶部导航 */
        .header {
            background: linear-gradient(135deg, #C93832, #A02820);
            color: white;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header a {
            color: white;
            text-decoration: none;
            padding: 6px 14px;
            border-radius: 6px;
            background: rgba(255,255,255,0.15);
            font-size: 13px;
            margin-left: 8px;
        }
        
        .header a:hover { background: rgba(255,255,255,0.25); }
        
        /* 主内容区 */
        .main-container {
            flex: 1;
            display: flex;
            overflow: hidden;
        }
        
        /* 左侧专家选择 */
        .sidebar {
            width: 260px;
            background: white;
            border-right: 1px solid #e0e0e0;
            display: flex;
            flex-direction: column;
        }
        
        .sidebar-header {
            padding: 16px;
            border-bottom: 1px solid #e0e0e0;
            font-weight: bold;
            font-size: 14px;
            color: #666;
        }
        
        .agent-list {
            flex: 1;
            overflow-y: auto;
            padding: 8px;
        }
        
        /* 专家卡片 - 关键修复 */
        .agent-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 4px;
            border: 2px solid transparent;
            background: white;
            transition: all 0.2s;
        }
        
        .agent-item:hover {
            background: #f0f2f5;
        }
        
        .agent-item.active {
            background: #e8f4ff;
            border-color: #006EBD;
        }
        
        /* 子元素不阻挡点击 */
        .agent-item * {
            pointer-events: none;
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
        
        .agent-info {
            flex: 1;
            min-width: 0;
        }
        
        .agent-name {
            font-size: 14px;
            font-weight: 600;
            color: #1a1a1a;
        }
        
        .agent-role {
            font-size: 11px;
            color: #666;
            margin-top: 2px;
        }
        
        /* 右侧对话区 */
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: white;
            min-width: 0;
        }
        
        /* 专家信息区 */
        .agent-info-panel {
            padding: 16px 20px;
            border-bottom: 1px solid #e0e0e0;
            display: none;
        }
        
        .agent-info-panel.show {
            display: block;
        }
        
        .agent-intro {
            display: flex;
            gap: 16px;
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
        
        .agent-intro-content {
            flex: 1;
        }
        
        .agent-intro-name {
            font-size: 18px;
            font-weight: bold;
            color: #1a1a1a;
        }
        
        .agent-intro-role {
            font-size: 13px;
            color: #666;
            margin-bottom: 8px;
        }
        
        .agent-intro-desc {
            font-size: 13px;
            color: #1a1a1a;
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
            color: #666;
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
            background: #006EBD;
            color: white;
        }
        
        .message.agent .message-content {
            background: #f0f2f5;
            color: #1a1a1a;
        }
        
        /* 输入区 - 固定底部 */
        .input-area {
            padding: 12px 16px;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
            background: white;
        }
        
        .input-area textarea {
            flex: 1;
            padding: 10px 14px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            resize: none;
            font-family: inherit;
            min-height: 42px;
            max-height: 120px;
        }
        
        .input-area textarea:focus {
            outline: none;
            border-color: #006EBD;
        }
        
        .send-btn {
            padding: 10px 24px;
            background: linear-gradient(135deg, #006EBD, #005a9e);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
        }
        
        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        /* 欢迎提示 */
        .welcome-tip {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #666;
            text-align: center;
            padding: 40px;
        }
        
        .welcome-tip .icon {
            font-size: 48px;
            margin-bottom: 16px;
        }
        
        .welcome-tip h3 {
            font-size: 18px;
            color: #1a1a1a;
            margin-bottom: 8px;
        }
        
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
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="font-size: 18px; font-weight: bold;">🧭 指南针工程</div>
            <div style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 16px; font-size: 12px;">👤 单智能体模式</div>
        </div>
        <div>
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
                <button class="send-btn" id="sendBtn" disabled>发送</button>
            </div>
        </div>
    </div>
    
    <script>
        // Agent数据
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
        
        // 状态变量
        var currentAgent = null;
        var conversations = {};
        var isProcessing = false;
        
        // 页面加载后渲染专家列表
        document.addEventListener('DOMContentLoaded', function() {
            console.log('页面加载完成，渲染专家列表');
            renderAgentList();
            
            // 绑定发送按钮事件
            document.getElementById('sendBtn').addEventListener('click', sendMessage);
            
            // 绑定回车发送
            document.getElementById('messageInput').addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
        });
        
        // 渲染专家列表
        function renderAgentList() {
            var container = document.getElementById('agentList');
            container.innerHTML = '';
            
            var order = ['caiwei', 'zhijin', 'zhutai', 'chengcai', 'yuheng', 'gongchi', 'zhegui', 'fuyao', 'nanqiao'];
            
            for (var i = 0; i < order.length; i++) {
                var id = order[i];
                var agent = AGENTS[id];
                
                // 使用document.createElement而不是innerHTML
                var item = document.createElement('div');
                item.className = 'agent-item' + (currentAgent === id ? ' active' : '');
                item.setAttribute('data-agent-id', id);
                
                // 使用addEventListener绑定点击事件
                (function(agentId) {
                    item.addEventListener('click', function() {
                        console.log('点击了专家: ' + agentId);
                        selectAgent(agentId);
                    });
                })(id);
                
                // 创建内部元素
                var avatar = document.createElement('div');
                avatar.className = 'agent-avatar';
                avatar.style.background = agent.color;
                avatar.textContent = agent.emoji;
                
                var info = document.createElement('div');
                info.className = 'agent-info';
                
                var name = document.createElement('div');
                name.className = 'agent-name';
                name.textContent = agent.name;
                
                var role = document.createElement('div');
                role.className = 'agent-role';
                role.textContent = agent.role;
                
                info.appendChild(name);
                info.appendChild(role);
                item.appendChild(avatar);
                item.appendChild(info);
                container.appendChild(item);
            }
            
            console.log('专家列表渲染完成，共 ' + order.length + ' 位专家');
        }
        
        // 选择专家
        function selectAgent(agentId) {
            console.log('selectAgent 被调用，agentId=' + agentId);
            
            if (isProcessing) {
                console.log('正在处理中，忽略切换请求');
                return;
            }
            
            var prevAgent = currentAgent;
            currentAgent = agentId;
            console.log('切换专家: ' + prevAgent + ' -> ' + currentAgent);
            
            // 初始化对话
            if (!conversations[agentId]) {
                conversations[agentId] = [];
            }
            
            // 更新UI
            renderAgentList();
            document.getElementById('welcomeTip').style.display = 'none';
            document.getElementById('messageInput').disabled = false;
            document.getElementById('sendBtn').disabled = false;
            
            // 加载专家信息
            loadAgentInfo(agentId);
            
            // 渲染消息
            renderMessages();
        }
        
        // 加载专家详细信息
        function loadAgentInfo(agentId) {
            fetch('/api/agent/info/' + agentId)
                .then(function(response) { return response.json(); })
                .then(function(result) {
                    if (result.status === 'ok') {
                        var agent = result.agent;
                        var panel = document.getElementById('agentInfoPanel');
                        panel.className = 'agent-info-panel show';
                        panel.innerHTML = 
                            '<div class="agent-intro">' +
                            '<div class="agent-intro-avatar" style="background: ' + agent.color + '">' + agent.emoji + '</div>' +
                            '<div class="agent-intro-content">' +
                            '<div class="agent-intro-name">' + agent.name + '</div>' +
                            '<div class="agent-intro-role">' + agent.role + '</div>' +
                            '<div class="agent-intro-desc">' + agent.introduction + '</div>' +
                            '<div class="agent-expertise">' + agent.expertise.map(function(e) { return '<span class="expertise-tag">' + e + '</span>'; }).join('') + '</div>' +
                            '<div class="agent-guidance">' + agent.guidance + '</div>' +
                            '</div></div>';
                    }
                })
                .catch(function(e) {
                    console.error('加载专家信息失败', e);
                });
        }
        
        // 渲染消息
        function renderMessages() {
            var area = document.getElementById('messagesArea');
            var msgs = conversations[currentAgent] || [];
            
            area.innerHTML = '';
            
            for (var i = 0; i < msgs.length; i++) {
                var msg = msgs[i];
                var msgDiv = document.createElement('div');
                msgDiv.className = 'message ' + msg.type;
                
                if (msg.type === 'user') {
                    msgDiv.innerHTML = '<div class="message-avatar" style="background: #595959;">👤</div><div class="message-content">' + escapeHtml(msg.content) + '</div>';
                } else if (msg.type === 'agent') {
                    var agent = AGENTS[currentAgent];
                    msgDiv.innerHTML = '<div class="message-avatar" style="background: ' + agent.color + '">' + agent.emoji + '</div><div class="message-content">' + escapeHtml(msg.content) + '</div>';
                }
                
                area.appendChild(msgDiv);
            }
            
            area.scrollTop = area.scrollHeight;
        }
        
        // 发送消息
        function sendMessage() {
            var input = document.getElementById('messageInput');
            var message = input.value.trim();
            
            if (!message || !currentAgent || isProcessing) return;
            
            // 添加用户消息
            conversations[currentAgent].push({ type: 'user', content: message });
            renderMessages();
            input.value = '';
            
            // 显示加载状态
            isProcessing = true;
            document.getElementById('sendBtn').disabled = true;
            showTyping();
            
            // 发送请求
            fetch('/api/agent/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    agent_id: currentAgent,
                    message: message,
                    history: conversations[currentAgent].slice(-10).map(function(m) {
                        return { speaker: m.type === 'user' ? 'user' : 'agent', content: m.content };
                    })
                })
            })
            .then(function(response) {
                var reader = response.body.getReader();
                var decoder = new TextDecoder();
                var fullResponse = '';
                
                hideTyping();
                
                var area = document.getElementById('messagesArea');
                var agent = AGENTS[currentAgent];
                var msgDiv = document.createElement('div');
                msgDiv.className = 'message agent';
                msgDiv.id = 'current-response';
                msgDiv.innerHTML = '<div class="message-avatar" style="background: ' + agent.color + '">' + agent.emoji + '</div><div class="message-content"></div>';
                area.appendChild(msgDiv);
                
                function readChunk() {
                    reader.read().then(function(result) {
                        if (result.done) {
                            conversations[currentAgent].push({ type: 'agent', content: fullResponse });
                            isProcessing = false;
                            document.getElementById('sendBtn').disabled = false;
                            return;
                        }
                        
                        var chunk = decoder.decode(result.value);
                        var lines = chunk.split('\\n');
                        
                        for (var i = 0; i < lines.length; i++) {
                            var line = lines[i];
                            if (line.indexOf('data: ') === 0) {
                                var data = line.substring(6);
                                if (data === '[DONE]') break;
                                try {
                                    var json = JSON.parse(data);
                                    if (json.text) {
                                        fullResponse += json.text;
                                        document.querySelector('#current-response .message-content').textContent = fullResponse;
                                        area.scrollTop = area.scrollHeight;
                                    }
                                } catch (e) {}
                            }
                        }
                        
                        readChunk();
                    });
                }
                
                readChunk();
            })
            .catch(function(e) {
                hideTyping();
                alert('网络错误，请重试');
                isProcessing = false;
                document.getElementById('sendBtn').disabled = false;
            });
        }
        
        // 显示/隐藏打字指示器
        function showTyping() {
            var area = document.getElementById('messagesArea');
            var agent = AGENTS[currentAgent];
            var typingDiv = document.createElement('div');
            typingDiv.className = 'message agent';
            typingDiv.id = 'typingIndicator';
            typingDiv.innerHTML = '<div class="message-avatar" style="background: ' + agent.color + '">' + agent.emoji + '</div><div class="message-content"><div class="typing-indicator"><span></span><span></span><span></span></div></div>';
            area.appendChild(typingDiv);
            area.scrollTop = area.scrollHeight;
        }
        
        function hideTyping() {
            var typing = document.getElementById('typingIndicator');
            if (typing) typing.remove();
        }
        
        // HTML转义
        function escapeHtml(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML.replace(/\\n/g, '<br>');
        }
    </script>
</body>
</html>
'''
