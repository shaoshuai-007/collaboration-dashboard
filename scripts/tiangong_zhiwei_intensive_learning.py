#!/usr/bin/env python3
"""
天工和知微集中学习任务清单
今晚完成4周训练内容

Author: 南乔
Date: 2026-03-17
"""

# 天工学习任务清单（4周压缩为今晚）
TIANGONG_LEARNING_TASKS = {
    "第1周-知识武装": {
        "电信业务流程": [
            "用户管理流程（开户/变更/销户）",
            "计费结算流程（实时计费/月结）",
            "套餐管理流程",
            "AI智能配案流程"
        ],
        "开发规范": [
            "Python编码规范（PEP8）",
            "数据库设计规范",
            "API接口设计规范（RESTful）",
            "代码质量工具（Pylint/Black/mypy）"
        ],
        "技术栈": [
            "Flask/FastAPI框架",
            "MySQL数据库优化",
            "Redis缓存策略",
            "JWT认证机制"
        ]
    },
    
    "第2周-任务演练": {
        "API开发": [
            "设计用户管理RESTful API",
            "实现增删改查接口",
            "编写Swagger文档"
        ],
        "数据库设计": [
            "设计用户表、套餐表、订单表",
            "创建索引和约束",
            "编写数据模型代码"
        ],
        "接口文档": [
            "编写完整的API文档",
            "添加请求/响应示例",
            "编写错误码说明"
        ]
    },
    
    "第3周-实战项目": {
        "智能配案系统后端": [
            "需求分析：理解配案业务逻辑",
            "数据库设计：用户表、套餐表、订单表",
            "API开发：用户接口、套餐接口、配案接口",
            "单元测试：接口测试、数据测试",
            "文档编写：API文档、部署文档"
        ]
    },
    
    "第4周-能力固化": {
        "知识沉淀": [
            "总结开发经验",
            "整理技术文档",
            "更新知识库",
            "编写能力评估报告"
        ]
    }
}

# 知微学习任务清单（4周压缩为今晚）
ZHIWEI_LEARNING_TASKS = {
    "第1周-知识武装": {
        "电信指标": [
            "ARPU/MOU/DOU指标",
            "用户留存率/流失率",
            "套餐渗透率/转化率",
            "用户增长率/接通率/投诉率"
        ],
        "分析方法": [
            "数据分析六步法",
            "RFM模型",
            "用户画像构建方法",
            "流失预测方法论"
        ],
        "可视化规范": [
            "图表设计规范",
            "数据可视化原则",
            "BI报表设计"
        ]
    },
    
    "第2周-任务演练": {
        "数据分析": [
            "用户ARPU分析",
            "用户行为分析",
            "流失特征分析"
        ],
        "用户画像": [
            "画像维度设计",
            "标签体系构建",
            "画像分析方法"
        ],
        "可视化报表": [
            "设计用户价值分析报表",
            "设计流失预警仪表盘",
            "编写分析报告"
        ]
    },
    
    "第3周-实战项目": {
        "用户流失分析与预测": [
            "数据理解：用户行为数据、消费数据",
            "数据清洗：缺失值、异常值处理",
            "特征工程：流失特征构建",
            "分析建模：流失预测模型",
            "报告编写：分析报告、策略建议"
        ]
    },
    
    "第4周-能力固化": {
        "知识沉淀": [
            "总结分析方法",
            "输出报告模板",
            "更新知识库",
            "编写能力评估报告"
        ]
    }
}

def print_task_summary():
    """打印任务摘要"""
    print("=" * 60)
    print("🚀 天工和知微今晚集中学习计划")
    print("=" * 60)
    print()
    
    # 天工任务统计
    tiangong_total = 0
    for week, tasks in TIANGONG_LEARNING_TASKS.items():
        week_count = sum(len(items) for items in tasks.values())
        tiangong_total += week_count
        print(f"💻 天工 - {week}: {week_count}个学习点")
    
    print(f"\n💻 天工总计: {tiangong_total}个学习点")
    print()
    
    # 知微任务统计
    zhiwei_total = 0
    for week, tasks in ZHIWEI_LEARNING_TASKS.items():
        week_count = sum(len(items) for items in tasks.values())
        zhiwei_total += week_count
        print(f"📊 知微 - {week}: {week_count}个学习点")
    
    print(f"\n📊 知微总计: {zhiwei_total}个学习点")
    print()
    print(f"🎯 总计: {tiangong_total + zhiwei_total}个学习点")
    print("=" * 60)

if __name__ == "__main__":
    print_task_summary()
