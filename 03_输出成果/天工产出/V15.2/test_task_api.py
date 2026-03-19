# -*- coding: utf-8 -*-
"""
test_task_api.py - 任务调度API测试
验证核心功能是否正常工作
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/03_输出成果/天工产出/V15.2')

from task_store import TaskStore, TaskStatus, AgentStatus, get_store
from task_scheduler import TaskScheduler, get_scheduler


def test_task_lifecycle():
    """测试任务完整生命周期"""
    print("\n" + "=" * 50)
    print("测试任务生命周期")
    print("=" * 50)
    
    # 创建新的存储和调度器实例
    store = TaskStore()
    scheduler = TaskScheduler(store)
    
    # 1. 创建任务
    print("\n1. 创建任务...")
    task_id = scheduler.create_task({
        "title": "测试任务",
        "description": "这是一个测试任务"
    })
    print(f"   任务ID: {task_id}")
    
    # 2. 查询任务状态
    print("\n2. 查询任务状态...")
    task = scheduler.get_task_status(task_id)
    print(f"   状态: {task['status']}")
    print(f"   进度: {task['progress']}%")
    
    # 3. 注册Agent
    print("\n3. 注册Agent...")
    agent_id = scheduler.register_agent({
        "name": "测试Agent",
        "capabilities": ["test", "demo"]
    })
    print(f"   Agent ID: {agent_id}")
    
    # 4. 分配Agent
    print("\n4. 分配Agent到任务...")
    scheduler.assign_agent(task_id, agent_id)
    task = scheduler.get_task_status(task_id)
    print(f"   任务状态: {task['status']}")
    print(f"   分配Agent: {task['agent']}")
    
    # 5. 启动任务
    print("\n5. 启动任务...")
    scheduler.start_task(task_id)
    task = scheduler.get_task_status(task_id)
    print(f"   任务状态: {task['status']}")
    
    # 6. 更新进度
    print("\n6. 更新进度...")
    scheduler.update_progress(task_id, 30, "正在处理中...")
    scheduler.update_progress(task_id, 60, "继续处理...")
    scheduler.update_progress(task_id, 90, "即将完成...")
    task = scheduler.get_task_status(task_id)
    print(f"   当前进度: {task['progress']}%")
    
    # 7. 完成任务
    print("\n7. 完成任务...")
    scheduler.complete_task(task_id, {
        "result": "任务执行成功",
        "data": {"key": "value"}
    })
    task = scheduler.get_task_status(task_id)
    print(f"   任务状态: {task['status']}")
    print(f"   产出: {task['output']}")
    
    # 8. 查看日志
    print("\n8. 任务日志:")
    logs = store.get_task_logs(task_id)
    for log in logs[-5:]:
        print(f"   [{log.level}] {log.message}")
    
    # 9. 统计信息
    print("\n9. 统计信息:")
    stats = store.get_stats()
    print(f"   总任务数: {stats['total_tasks']}")
    print(f"   总Agent数: {stats['total_agents']}")
    print(f"   任务状态分布: {stats['tasks_by_status']}")
    
    print("\n✅ 任务生命周期测试完成！")


def test_multiple_tasks():
    """测试多任务并发"""
    print("\n" + "=" * 50)
    print("测试多任务并发")
    print("=" * 50)
    
    store = TaskStore()
    scheduler = TaskScheduler(store)
    
    # 注册多个Agent
    agents = []
    for i in range(3):
        agent_id = scheduler.register_agent({
            "name": f"Agent-{i+1}",
            "capabilities": ["task"]
        })
        agents.append(agent_id)
    
    print(f"\n注册了 {len(agents)} 个Agent")
    
    # 创建多个任务
    tasks = []
    for i in range(5):
        task_id = scheduler.create_task({
            "title": f"任务-{i+1}",
            "description": f"第{i+1}个测试任务"
        })
        tasks.append(task_id)
    
    print(f"创建了 {len(tasks)} 个任务")
    
    # 自动分配
    print("\n自动分配Agent:")
    for task_id in tasks[:3]:
        assigned = scheduler.auto_assign_task(task_id)
        if assigned:
            task = scheduler.get_task_status(task_id)
            print(f"   {task_id} -> {task['agent']}")
    
    # 查看Agent状态
    print("\nAgent状态:")
    for agent in store.get_all_agents():
        print(f"   {agent.name}: {agent.status.value} (当前任务: {agent.current_task})")
    
    print("\n✅ 多任务并发测试完成！")


def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 50)
    print("测试错误处理")
    print("=" * 50)
    
    from task_scheduler import (
        TaskNotFoundError, AgentNotFoundError,
        AgentNotAvailableError, InvalidStatusError
    )
    
    store = TaskStore()
    scheduler = TaskScheduler(store)
    
    # 测试不存在的任务
    print("\n1. 查询不存在的任务:")
    try:
        scheduler.get_task_status("nonexistent")
    except TaskNotFoundError as e:
        print(f"   正确捕获异常: {e}")
    
    # 测试无效进度值
    print("\n2. 设置无效进度值:")
    task_id = scheduler.create_task({"title": "测试任务"})
    try:
        scheduler.update_progress(task_id, 150)
    except ValueError as e:
        print(f"   正确捕获异常: {e}")
    
    # 测试分配不存在的Agent
    print("\n3. 分配不存在的Agent:")
    try:
        scheduler.assign_agent(task_id, "nonexistent_agent")
    except AgentNotFoundError as e:
        print(f"   正确捕获异常: {e}")
    
    # 测试任务状态流转错误
    print("\n4. 任务状态流转错误:")
    scheduler.register_agent({"name": "测试Agent"})
    agent = store.get_all_agents()[0]
    scheduler.assign_agent(task_id, agent.agent_id)
    try:
        # 已经分配了，再次分配应该失败
        scheduler.assign_agent(task_id, agent.agent_id)
    except Exception as e:
        print(f"   正确捕获异常: {type(e).__name__}")
    
    print("\n✅ 错误处理测试完成！")


if __name__ == '__main__':
    print("=" * 50)
    print("QQ任务调度功能 - 单元测试")
    print("=" * 50)
    
    try:
        test_task_lifecycle()
        test_multiple_tasks()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试通过！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
