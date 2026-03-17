#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V15深度融合补丁脚本
"""

# 读取原文件
with open('collaboration_dashboard_v14.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到api_task函数的开始和结束
start_line = None
end_line = None

for i, line in enumerate(lines):
    if "@app.route('/api/task'" in line:
        start_line = i
    elif start_line and line.strip().startswith("@app.route"):
        end_line = i
        break

print(f"api_task函数: {start_line + 1} - {end_line}行")

# 新的api_task函数
new_api_task = '''@app.route('/api/task', methods=['POST'])
def api_task():
    """
    任务处理接口 - V15深度融合版
    
    核心改进：
    1. 使用南乔意图分析器识别项目名称、产出物、复杂度
    2. 多产出物工作流（拓扑排序）
    3. 讨论结束后自动生成会议纪要
    """
    global agent_status, discussion_completed

    data = request.json
    task = data.get('task', '')

    # 重置状态
    discussion_completed = False
    memory.clear()
    agent_status = {aid: 'idle' for aid in AGENTS.keys()}

    # ========== V15深度融合：意图分析 ==========
    intent_result = None
    outputs = []
    project_name = "待定"
    complexity = "low"
    participants = []
    discussion_rounds = 1
    
    if load_v15_modules():
        try:
            intent_analyzer = NanqiaoIntentAnalyzer()
            intent_result = intent_analyzer.analyze(task)
            
            # 使用V15的分析结果
            project_name = intent_result.project_name
            outputs = intent_result.outputs
            complexity = intent_result.complexity
            participants = intent_result.participants
            discussion_rounds = intent_result.discussion_rounds
            
            print(f"[V15] 意图分析成功")
            print(f"[V15] 项目：{project_name}")
            print(f"[V15] 产出物：{[o['name'] for o in outputs]}")
            print(f"[V15] 复杂度：{complexity}")
            print(f"[V15] 参与者：{participants}")
            print(f"[V15] 讨论轮次：{discussion_rounds}")
        except Exception as e:
            print(f"[V15] 意图分析失败，回退到V14逻辑: {e}")
            import traceback
            traceback.print_exc()
    
    # 如果V15分析失败，使用V14逻辑
    if not outputs:
        schedule_results = intelligent_scheduler.process_multi(task)
        outputs = []
        for r in schedule_results:
            outputs.append({
                'name': r['output_template'],
                'code': r['task_code'],
                'owner': AGENT_NAMES.get(r['schedule']['lead_agent'], '采薇')
            })
        participants = schedule_results[0]['schedule']['participants'] if schedule_results else ['caiwei', 'yuheng']
        complexity = schedule_results[0].get('complexity', 'low')
        discussion_rounds = 1
    else:
        # V15结果转换为V14格式
        schedule_results = []
        for output in outputs:
            task_code = output.get('code', 'REQ-02')
            owner_id = output.get('owner', '采薇')
            owner_id_lower = None
            for aid, name in AGENT_NAMES.items():
                if name == owner_id:
                    owner_id_lower = aid
                    break
            if not owner_id_lower:
                owner_id_lower = 'caiwei'
            
            schedule_results.append({
                'task_code': task_code,
                'task_name': output['name'],
                'output_template': output['name'],
                'complexity': complexity,
                'estimated_time': '3-5天' if complexity == 'low' else ('5-10天' if complexity == 'medium' else '10-15天'),
                'schedule': {
                    'lead_agent': owner_id_lower,
                    'participants': participants if isinstance(participants[0], str) and participants[0] in AGENTS else ['caiwei', 'yuheng'],
                    'discussion_flow': participants if isinstance(participants[0], str) and participants[0] in AGENTS else ['caiwei', 'yuheng'],
                    'time_estimate': '3-5天'
                }
            })

    print(f"[DEBUG] 用户输入: {task}")
    print(f"[DEBUG] 产出物数: {len(outputs)}")

    memory.current_task = task
    memory.start_time = datetime.now()
    memory.add_turn('user', '少帅', task)

    # 动态轮次上限
    num_tasks = len(schedule_results)
    if complexity == 'high':
        dynamic_turn_limit = min(20 + num_tasks * 3, 30)
    elif complexity == 'medium':
        dynamic_turn_limit = min(15 + num_tasks * 2, 25)
    else:
        dynamic_turn_limit = min(10 + num_tasks * 1, 20)

    # 调度提示
    if len(schedule_results) > 1:
        task_names = [r['task_name'] for r in schedule_results]
        schedule_msg = responder.generate_system_message('schedule', {
            'multi': True,
            'task_list': '、'.join(task_names),
            'tasks': task_names
        })
    else:
        participants_cn = [AGENT_NAMES.get(aid, aid) if aid in AGENTS else aid for aid in (participants if isinstance(participants[0], str) else [p['owner'] for p in participants])]
        schedule_msg = responder.generate_system_message('schedule', {
            'multi': False,
            'task_name': outputs[0]['name'] if outputs else '任务',
            'lead_agent': participants_cn[0] if participants_cn else '采薇',
            'participants': '、'.join(participants_cn),
            'est_time': schedule_results[0].get('estimated_time', '3-5天') if schedule_results else '3-5天',
            'complexity': complexity
        })
    memory.add_turn('nanqiao', '南乔', schedule_msg, msg_type='system')

    total_tasks = len(schedule_results)

    def run_multi_task_discussion():
        global discussion_completed, agent_status
        
        try:
            for task_idx, schedule_result in enumerate(schedule_results):
                task_name = schedule_result['task_name']
                est_time = schedule_result.get('estimated_time', '3-5天')
                
                if total_tasks > 1:
                    task_start_msg = responder.generate_system_message('task_start', {
                        'current': task_idx + 1,
                        'total': total_tasks,
                        'task_name': task_name,
                        'est_time': est_time
                    })
                    memory.add_turn('nanqiao', '南乔', task_start_msg, msg_type='system')
                    time.sleep(0.5)

                discussion_flow = schedule_result['schedule']['discussion_flow']
                task_complexity = schedule_result['complexity']
                lead_agent = schedule_result['schedule']['lead_agent']

                # ========== V15多轮讨论 ==========
                for round_num in range(discussion_rounds):
                    print(f"[V15] 第{round_num + 1}轮讨论")
                    
                    for agent_key in discussion_flow:
                        if len(memory.history) >= dynamic_turn_limit:
                            break
                        if agent_key not in AGENTS:
                            continue

                        time.sleep(0.5)
                        agent_status[agent_key] = 'speaking'
                        
                        context_prefix = ""
                        if round_num > 0:
                            context_prefix = f"【第{round_num + 1}轮讨论】请深化分析或提出质疑。\\n\\n"
                        
                        try:
                            response, is_challenge, reply_to = responder.generate(
                                AGENTS[agent_key], context_prefix + task, memory
                            )
                        except Exception as e:
                            response, is_challenge, reply_to = responder._fallback(AGENTS[agent_key], task, memory.get_context())

                        if agent_key == lead_agent and round_num == 0:
                            est_msg = responder.generate_estimate_message(
                                AGENTS[agent_key].name, task_name, est_time, task_complexity
                            )
                            response += f"\\n\\n{est_msg}"

                        agent_status[agent_key] = 'challenge' if is_challenge else 'speaking'
                        memory.add_turn(agent_key, AGENTS[agent_key].name, response,
                                      is_challenging=is_challenge, reply_to=reply_to)
                        time.sleep(2)
                        agent_status[agent_key] = 'idle'
                    
                    if len(memory.history) >= dynamic_turn_limit:
                        break

                # 风险辩论
                if task_complexity == 'high' and len(memory.history) < dynamic_turn_limit:
                    risk_msg = responder.generate_system_message('risk_debate', {})
                    memory.add_turn('nanqiao', '南乔', risk_msg, msg_type='system')

                    for agent_key in AGENTS.keys():
                        if len(memory.history) >= dynamic_turn_limit:
                            break
                        if agent_key == 'nanqiao' or agent_key in discussion_flow:
                            continue
                        time.sleep(0.3)
                        agent_status[agent_key] = 'speaking'
                        try:
                            response, is_challenge, reply_to = responder.generate(AGENTS[agent_key], task, memory)
                        except Exception as e:
                            response, is_challenge, reply_to = responder._fallback(AGENTS[agent_key], task, memory.get_context())
                        memory.add_turn(agent_key, AGENTS[agent_key].name, response,
                                      is_challenging=True, reply_to=reply_to)
                        time.sleep(1.5)
                        agent_status[agent_key] = 'idle'

                if total_tasks > 1 and task_idx < total_tasks - 1:
                    task_done_msg = responder.generate_system_message('task_done', {
                        'current': task_idx + 1,
                        'task_name': task_name,
                        'consensus': memory.get_consensus_level(),
                        'next_task': schedule_results[task_idx + 1]['task_name']
                    })
                    memory.add_turn('nanqiao', '南乔', task_done_msg, msg_type='system')

            # 最终共识
            time.sleep(0.5)
            agent_status['nanqiao'] = 'speaking'
            consensus = memory.get_consensus_level()

            if total_tasks > 1:
                summary = responder.generate_system_message('all_done', {
                    'total': total_tasks,
                    'consensus': consensus,
                    'outputs': [r['output_template'] for r in schedule_results],
                    'discussion_summary': memory.get_context()[:2000]
                })
            else:
                summary = responder.generate_system_message('consensus', {
                    'consensus': consensus,
                    'output': schedule_results[0]['output_template'] if schedule_results else '产出物',
                    'discussion_summary': memory.get_context()[:2000]
                })

            memory.add_turn('nanqiao', '南乔', summary, msg_type='conclusion')
            agent_status['nanqiao'] = 'idle'

        except Exception as e:
            print(f"[ERROR] 讨论线程异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            discussion_completed = True
            print(f"[DEBUG] 讨论完成，共识度: {memory.get_consensus_level()}%")
            
            # ========== V15自动生成会议纪要 ==========
            if load_v15_modules() and intent_result:
                try:
                    print("[V15] 正在生成会议纪要...")
                    minutes_gen = MeetingMinutesGenerator()
                    
                    discussion_data = {
                        'rounds': [{'round_num': 1, 'messages': []}],
                        'consensus_reached': True,
                        'key_decisions': [],
                        'project_name': project_name,
                        'complexity': complexity,
                        'participants': participants
                    }
                    
                    for turn in memory.history:
                        if turn.speaker != 'user':
                            discussion_data['rounds'][0]['messages'].append({
                                'speaker': turn.speaker_name,
                                'content': turn.content[:500]
                            })
                    
                    minutes = minutes_gen.generate(intent_result.__dict__, discussion_data)
                    minutes_file = minutes_gen.export_to_file(minutes)
                    print(f"[V15] 会议纪要已生成: {minutes_file}")
                    
                    memory.add_turn('nanqiao', '南乔', 
                        f"\\n\\n📄 **会议纪要已自动生成**\\n文件路径：{minutes_file}", 
                        msg_type='system')
                except Exception as e:
                    print(f"[V15] 会议纪要生成失败: {e}")
                    import traceback
                    traceback.print_exc()

    thread = threading.Thread(target=run_multi_task_discussion)
    thread.start()

    return jsonify({
        'status': 'ok',
        'v15_mode': intent_result is not None,
        'project_name': project_name,
        'outputs': outputs,
        'complexity': complexity,
        'discussion_rounds': discussion_rounds,
        'schedule': schedule_results[0] if len(schedule_results) == 1 else {'multi': len(schedule_results)},
        'tasks': [r['task_name'] for r in schedule_results],
        'estimated_times': [r.get('estimated_time', '3-5天') for r in schedule_results]
    })


'''

# 替换
new_lines = lines[:start_line] + [new_api_task] + lines[end_line:]

# 写回文件
with open('collaboration_dashboard_v14.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ V15深度融合补丁已应用")
print(f"原文件: {len(lines)}行")
print(f"新文件: {len(new_lines)}行")
