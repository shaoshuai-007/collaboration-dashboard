from flask import Flask, render_template_string

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>测试页面</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        .agent-list { display: flex; gap: 10px; margin-bottom: 20px; }
        .agent-item { 
            padding: 10px 20px; 
            background: #eee; 
            cursor: pointer; 
            border: 2px solid #ccc;
        }
        .agent-item.active { background: #409EFF; color: white; border-color: #007acc; }
        #agentInfoPanel {
            padding: 20px;
            border: 3px solid red;
            background: #ffe;
            min-height: 100px;
            display: block;
        }
    </style>
</head>
<body>
    <h1>点击测试</h1>
    <div class="agent-list">
        <div class="agent-item" onclick="selectAgent('caiwei')">采薇</div>
        <div class="agent-item" onclick="selectAgent('zhijin')">织锦</div>
        <div class="agent-item" onclick="selectAgent('zhutai')">筑台</div>
    </div>
    <div id="agentInfoPanel">
        点击上方专家查看详情
    </div>
    <script>
        var agents = {
            'caiwei': {name:'采薇', role:'需求分析专家', intro:'电信行业资深需求分析专家'},
            'zhijin': {name:'织锦', role:'架构设计师', intro:'系统架构设计专家'},
            'zhutai': {name:'筑台', role:'售前工程师', intro:'资深售前顾问'}
        };
        
        window.selectAgent = function(agentId) {
            var a = agents[agentId];
            var panel = document.getElementById('agentInfoPanel');
            panel.innerHTML = '<h2>' + a.name + '</h2><p>' + a.role + '</p><p>' + a.intro + '</p>';
            alert('已切换到 ' + a.name + '，panel.innerHTML已设置');
        };
    </script>
</body>
</html>
'''

@app.route('/test')
def test():
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
