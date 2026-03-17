#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复V15多任务识别问题
"""

# 读取原文件
with open('collaboration_dashboard_v14.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到问题代码并替换
old_code = '''    else:
        # V15识别出多个产出物 → 使用V14多任务识别逻辑
        # 这样可以保证每个产出物都有正确的task_code
        print(f"[V15] 识别到{len(outputs)}个产出物，使用V14多任务调度")
        schedule_results = intelligent_scheduler.process_multi(task)
        
        # 如果V14也识别出多个任务，使用V14的结果
        if len(schedule_results) >= len(outputs):
            print(f"[V14] 识别到{len(schedule_results)}个任务")
        else:
            # 否则手动构建schedule_results
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
            })'''

new_code = '''    else:
        # V15识别出多个产出物 → 使用V14多任务识别逻辑
        # 这样可以保证每个产出物都有正确的task_code
        print(f"[V15] 识别到{len(outputs)}个产出物，使用V14多任务调度")
        schedule_results = intelligent_scheduler.process_multi(task)
        print(f"[V14] 识别到{len(schedule_results)}个任务")
        
        # 更新outputs为V14结果
        outputs = []
        for r in schedule_results:
            outputs.append({
                'name': r['output_template'],
                'code': r['task_code'],
                'owner': AGENT_NAMES.get(r['schedule']['lead_agent'], '采薇')
            })
        
        # 更新复杂度
        if len(schedule_results) > 1:
            complexity = 'medium' if len(schedule_results) <= 3 else 'high'
'''

if old_code in content:
    content = content.replace(old_code, new_code)
    print("✅ 已修复多任务识别问题")
else:
    print("❌ 未找到问题代码，可能已被修改")
    # 尝试另一种方式
    import re
    # 找到else块并替换
    pattern = r"else:\s*# V15识别出多个产出物.*?schedule_results\.append\([^)]+\}\)"
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, new_code, content, flags=re.DOTALL)
        print("✅ 使用正则修复")

# 写回文件
with open('collaboration_dashboard_v14.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("修复完成")
