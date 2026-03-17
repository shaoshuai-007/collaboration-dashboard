'''
改进版单智能体工作区 - V15.1

修改内容：
1. 支持专家切换（可随时切换，保留历史）
2. 流式输出（渐进式显示）
3. 输入框固定底部
4. 详细的专家介绍和引导
'''

# 新增：获取专家详细信息API
@app.route('/api/agent/info/<agent_id>')
def api_agent_info(agent_id):
    """获取专家详细信息"""
    if agent_id not in AGENT_DETAILS:
        return jsonify({'status': 'error', 'message': '未知专家'})
    return jsonify({
        'status': 'ok',
        'agent': AGENT_DETAILS[agent_id]
    })

# 新增：流式输出API
@app.route('/api/agent/stream', methods=['POST'])
def api_agent_stream():
    """流式输出API - SSE"""
    data = request.json
    agent_id = data.get('agent_id')
    message = data.get('message')
    history = data.get('history', [])
    
    if agent_id not in AGENTS:
        return jsonify({'status': 'error', 'message': '未知专家'})
    
    agent = AGENTS[agent_id]
    
    def generate():
        # 构建对话历史
        history_text = ""
        if history:
            history_text = "\n\n【对话历史】\n"
            for h in history[-6:]:
                speaker = "用户" if h['speaker'] == 'user' else agent.name
                history_text += f"{speaker}: {h['content'][:200]}\n"
        
        # 构建Prompt
        prompt = f"""{agent.system_prompt}
{history_text}

【用户问题】
{message}

请以{agent.name}的身份，从{agent.role}的专业角度回答。要求专业、准确、简洁（不超过300字）。"""
        
        # 调用千帆流式API
        try:
            url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro"
            headers = {
                "Authorization": f"Bearer {QIANFAN_API_KEY}",
                "Content-Type": "application/json"
            }
            combined_message = f"{agent.system_prompt}\n\n---\n\n{prompt}"
            payload = {
                "messages": [{"role": "user", "content": combined_message}],
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": True
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60, stream=True)
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        data_str = line_text[6:]
                        if data_str.strip():
                            try:
                                data = json.loads(data_str)
                                if 'result' in data:
                                    yield f"data: {json.dumps({'text': data['result']})}\n\n"
                            except:
                                continue
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')
