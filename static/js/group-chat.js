/**
 * 九星智囊团群聊交互逻辑 - V16.0
 * 作者：南乔 🌿
 * 日期：2026-03-19
 */

// ===== 全局变量 =====
let agents = [];
let messages = [];
let tasks = [];
let currentTask = null;

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', () => {
    loadAgents();
    loadMessages();
    loadTasks();
    connectSSE();
    
    // 每10秒刷新一次
    setInterval(() => {
        loadAgents();
        loadTasks();
    }, 10000);
});

// ===== 加载Agent列表 =====
async function loadAgents() {
    try {
        const response = await fetch('/api/v16/agents');
        const data = await response.json();
        agents = data.agents || [];
        renderAgentList();
        updateMemberCount();
    } catch (error) {
        console.error('加载Agent失败:', error);
    }
}

// ===== 渲染Agent列表 =====
function renderAgentList() {
    const container = document.getElementById('agentList');
    
    const statusOrder = { 'online': 0, 'busy': 1, 'offline': 2 };
    const sortedAgents = [...agents].sort((a, b) => {
        return (statusOrder[a.status] || 2) - (statusOrder[b.status] || 2);
    });
    
    container.innerHTML = sortedAgents.map(agent => `
        <div class="agent-item" onclick="mentionAgent('${agent.agent_id}', '${agent.name}')">
            <div class="agent-avatar-small ${agent.agent_id}">
                ${agent.emoji}
            </div>
            <div class="agent-info">
                <div class="agent-name">${agent.name}</div>
                <div class="agent-role">
                    <span class="status-dot ${agent.status}"></span>
                    ${agent.role}
                </div>
            </div>
        </div>
    `).join('');
}

// ===== 更新成员数量 =====
function updateMemberCount() {
    const onlineCount = agents.filter(a => a.status === 'online').length;
    document.getElementById('memberCount').textContent = `成员：${agents.length}人 | 在线：${onlineCount}人`;
}

// ===== 加载消息 =====
async function loadMessages() {
    try {
        const response = await fetch('/api/v16/messages?limit=50');
        const data = await response.json();
        messages = data.messages || [];
        renderMessages();
        scrollToBottom();
    } catch (error) {
        console.error('加载消息失败:', error);
    }
}

// ===== 渲染消息 =====
function renderMessages() {
    const container = document.getElementById('messageContainer');
    
    container.innerHTML = messages.map(msg => {
        // 处理@提及高亮
        let content = msg.content;
        if (msg.mentions && msg.mentions.length > 0) {
            msg.mentions.forEach(agentId => {
                const agent = agents.find(a => a.agent_id === agentId);
                if (agent) {
                    const regex = new RegExp(`@${agent.name}`, 'g');
                    content = content.replace(regex, `<span class="mention">@${agent.name}</span>`);
                }
            });
        }
        
        // 处理换行
        content = content.replace(/\n/g, '<br>');
        
        const avatarClass = msg.from_type === 'agent' ? msg.from_id : 'user';
        
        return `
            <div class="message ${msg.from_type}">
                <div class="message-avatar ${avatarClass}">
                    ${msg.from_emoji}
                </div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="message-name">${msg.from_name}</span>
                        <span class="message-time">${formatTime(msg.created_at)}</span>
                    </div>
                    <div class="message-bubble">
                        ${content}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// ===== 格式化时间 =====
function formatTime(timeStr) {
    const date = new Date(timeStr);
    const now = new Date();
    
    if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    } else {
        return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) + 
               ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    }
}

// ===== 滚动到底部 =====
function scrollToBottom() {
    const container = document.getElementById('messageContainer');
    container.scrollTop = container.scrollHeight;
}

// ===== 加载任务 =====
async function loadTasks() {
    try {
        const response = await fetch('/api/v16/tasks');
        const data = await response.json();
        tasks = data.tasks || [];
        renderTasks();
        updateCurrentTask();
    } catch (error) {
        console.error('加载任务失败:', error);
    }
}

// ===== 渲染任务 =====
function renderTasks() {
    const container = document.getElementById('taskList');
    
    if (tasks.length === 0) {
        container.innerHTML = '<div class="empty-state">暂无任务</div>';
        return;
    }
    
    const statusIcon = {
        'pending': '⏳',
        'running': '🔄',
        'completed': '✅',
        'failed': '❌'
    };
    
    container.innerHTML = tasks.slice(0, 5).map(task => {
        const agent = agents.find(a => a.agent_id === task.assignee);
        return `
            <div class="task-item ${task.status}">
                <div class="task-title">${statusIcon[task.status]} ${task.title}</div>
                <div class="task-meta">
                    <span>${agent ? agent.emoji + agent.name : '未分配'}</span>
                    <div class="task-progress-mini">
                        <div class="task-progress-fill" style="width: ${task.progress}%"></div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// ===== 更新当前任务 =====
function updateCurrentTask() {
    const runningTask = tasks.find(t => t.status === 'running');
    if (runningTask) {
        document.getElementById('currentTask').textContent = `当前任务：${runningTask.title}`;
        document.getElementById('taskProgress').style.width = `${runningTask.progress}%`;
    } else {
        document.getElementById('currentTask').textContent = '当前任务：无';
        document.getElementById('taskProgress').style.width = '0%';
    }
}

// ===== 发送消息 =====
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const content = input.value.trim();
    
    if (!content) return;
    
    try {
        const response = await fetch('/api/v16/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                from_type: 'user',
                from_id: 'shaoshuai',
                content: content
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            input.value = '';
            // 消息会通过SSE推送
        } else {
            alert('发送失败：' + data.error);
        }
    } catch (error) {
        console.error('发送消息失败:', error);
        alert('发送失败，请重试');
    }
}

// ===== 处理键盘事件 =====
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// ===== @提及Agent =====
function mentionAgent(agentId, agentName) {
    const input = document.getElementById('messageInput');
    input.value += `@${agentName} `;
    input.focus();
}

// ===== 插入@提及 =====
function insertMention() {
    const input = document.getElementById('messageInput');
    input.value += '@';
    input.focus();
    
    // 显示提及选择器
    showMentionPicker();
}

// ===== 显示提及选择器 =====
function showMentionPicker() {
    const popup = document.getElementById('mentionPopup');
    const list = document.getElementById('mentionList');
    
    list.innerHTML = agents.map(agent => `
        <div class="mention-item" onclick="selectMention('${agent.agent_id}', '${agent.name}')">
            <span class="agent-avatar-small ${agent.agent_id}">${agent.emoji}</span>
            <span>${agent.name}</span>
            <span style="color: var(--gray-medium); font-size: 12px; margin-left: 8px;">${agent.role}</span>
        </div>
    `).join('');
    
    // 定位
    const input = document.getElementById('messageInput');
    const rect = input.getBoundingClientRect();
    popup.style.left = rect.left + 'px';
    popup.style.bottom = (window.innerHeight - rect.top + 10) + 'px';
    popup.style.display = 'block';
}

// ===== 选择提及 =====
function selectMention(agentId, agentName) {
    const input = document.getElementById('messageInput');
    // 移除最后的@
    input.value = input.value.replace(/@$/, '');
    input.value += `@${agentName} `;
    
    document.getElementById('mentionPopup').style.display = 'none';
    input.focus();
}

// ===== 连接SSE =====
function connectSSE() {
    const eventSource = new EventSource('/api/v16/events');
    
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'new_message') {
            messages.push(data.message);
            renderMessages();
            scrollToBottom();
        } else if (data.type === 'task_update') {
            loadTasks();
        }
    };
    
    eventSource.onerror = (error) => {
        console.error('SSE连接错误:', error);
        // 5秒后重连
        setTimeout(connectSSE, 5000);
    };
}

// ===== 表情选择器 =====
function showEmojiPicker() {
    // 简化实现：直接插入一个表情
    const emojis = ['👍', '👏', '🎉', '💪', '🙏', '😊', '🤔', '👍🏻'];
    const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
    
    const input = document.getElementById('messageInput');
    input.value += randomEmoji;
    input.focus();
}

// ===== 点击其他地方关闭弹窗 =====
document.addEventListener('click', (event) => {
    const popup = document.getElementById('mentionPopup');
    if (!event.target.closest('.tool-btn') && !event.target.closest('.mention-popup')) {
        popup.style.display = 'none';
    }
});

console.log('🌿 九星智囊团群聊已加载');
