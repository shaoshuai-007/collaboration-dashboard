#!/usr/bin/env python3
"""
生成Token采集系统架构图
"""

from graphviz import Digraph
import os

# 输出目录
OUTPUT_DIR = "/root/.openclaw/workspace/03_输出成果/Token采集需求分析/arch_diagrams"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 颜色定义
COLORS = {
    'primary': '#006EBD',      # 深蓝
    'secondary': '#C93832',    # 电信红
    'neutral': '#595959',      # 灰色
    'light': '#f5f5f5',        # 浅灰
    'white': '#ffffff'
}

def create_overall_arch():
    """创建总体架构图"""
    dot = Digraph(comment='Token采集系统总体架构', format='png')
    dot.attr(rankdir='TB', size='12,16', dpi='150')
    dot.attr('node', shape='box', style='rounded,filled', fontname='SimHei', fontsize='11')
    dot.attr('edge', fontname='SimHei', fontsize='9')
    
    # 数据应用层
    with dot.subgraph(name='cluster_l4') as c:
        c.attr(label='📊 数据应用层 (Layer 4)', style='filled', fillcolor=COLORS['primary'], fontcolor='white')
        c.node('a1', 'Token统计Dashboard', fillcolor='#e8f4ff')
        c.node('a2', '成本分析Dashboard', fillcolor='#e8f4ff')
        c.node('a3', '效果评估Dashboard', fillcolor='#e8f4ff')
        c.node('a4', '可视化报表', fillcolor='#e8f4ff')
        c.node('a5', '数据查询API', fillcolor='#e8f4ff')
    
    # 数据处理层
    with dot.subgraph(name='cluster_l3') as c:
        c.attr(label='⚙️ 数据处理层 (Layer 3)', style='filled', fillcolor=COLORS['primary'], fontcolor='white')
        c.node('p1', '数据清洗', fillcolor='#e8f4ff')
        c.node('p2', '数据转换', fillcolor='#e8f4ff')
        c.node('p3', '数据入库', fillcolor='#e8f4ff')
        c.node('p4', '数据汇总', fillcolor='#e8f4ff')
        c.edge('p1', 'p2')
        c.edge('p2', 'p3')
        c.edge('p3', 'p4')
    
    # 数据采集层
    with dot.subgraph(name='cluster_l2') as c:
        c.attr(label='📥 数据采集层 (Layer 2)', style='filled', fillcolor=COLORS['secondary'], fontcolor='white')
        c.node('c1', 'SFTP接收服务', fillcolor='#ffe8e8')
        c.node('c2', '文件解析服务', fillcolor='#ffe8e8')
        c.node('c3', '文件校验服务', fillcolor='#ffe8e8')
        c.node('c4', '回执生成服务', fillcolor='#ffe8e8')
        c.edge('c1', 'c2')
        c.edge('c2', 'c3')
        c.edge('c3', 'c4')
    
    # 数据源层
    with dot.subgraph(name='cluster_l1') as c:
        c.attr(label='🏢 数据源层 (Layer 1)', style='filled', fillcolor=COLORS['secondary'], fontcolor='white')
        c.node('s1', '总部部门(23个)', fillcolor='#ffe8e8')
        c.node('s2', '专业公司(26个)', fillcolor='#ffe8e8')
        c.node('s3', '省公司(31个)', fillcolor='#ffe8e8')
        c.node('s4', '直属机构(6个)', fillcolor='#ffe8e8')
    
    # 支撑体系
    with dot.subgraph(name='cluster_support') as c:
        c.attr(label='🛠️ 支撑体系', style='filled', fillcolor=COLORS['neutral'], fontcolor='white')
        c.node('m1', '监控告警\nPrometheus', fillcolor='#f5f5f5')
        c.node('m2', '任务调度\nAirflow', fillcolor='#f5f5f5')
        c.node('m3', '日志管理\nLoguru', fillcolor='#f5f5f5')
    
    # 层间连接
    dot.edge('s1', 'c1', label='SFTP', style='dashed')
    dot.edge('s2', 'c1', style='dashed')
    dot.edge('s3', 'c1', style='dashed')
    dot.edge('s4', 'c1', style='dashed')
    
    dot.edge('c4', 'p1', label='数据推送')
    dot.edge('p4', 'a1', label='数据服务')
    
    # 支撑连接
    dot.edge('m1', 'c1', style='dotted', color='gray')
    dot.edge('m2', 'p1', style='dotted', color='gray')
    
    # 渲染
    output_path = os.path.join(OUTPUT_DIR, '总体架构图')
    dot.render(output_path, cleanup=True)
    print(f"✅ 总体架构图: {output_path}.png")
    return f"{output_path}.png"


def create_deploy_arch():
    """创建部署架构图"""
    dot = Digraph(comment='部署架构', format='png')
    dot.attr(rankdir='LR', size='14,10', dpi='150')
    dot.attr('node', shape='box', style='rounded,filled', fontname='SimHei', fontsize='11')
    dot.attr('edge', fontname='SimHei', fontsize='9')
    
    # 外部网络
    with dot.subgraph(name='cluster_external') as c:
        c.attr(label='🌐 外部网络', style='filled', fillcolor='#e8f4ff')
        c.node('ext1', '总部部门\n(23个单位)', fillcolor='#ffffff')
        c.node('ext2', '专业公司\n(26个单位)', fillcolor='#ffffff')
        c.node('ext3', '省公司\n(31个单位)', fillcolor='#ffffff')
    
    # CN2网络
    with dot.subgraph(name='cluster_cn2') as c:
        c.attr(label='🔒 CN2-1124 电信专网', style='filled', fillcolor='#ffe8e8')
        c.node('fw', '防火墙', fillcolor='#ffffff', shape='diamond')
    
    # 生产环境
    with dot.subgraph(name='cluster_prod') as c:
        c.attr(label='🖥️ 生产环境', style='filled', fillcolor='#e8ffe8')
        with c.subgraph(name='cluster_app') as app:
            app.attr(label='应用集群', style='dashed')
            app.node('sftp', 'SFTP服务\n端口:12222', fillcolor='#ffffff')
            app.node('parse', '解析服务', fillcolor='#ffffff')
            app.node('valid', '校验服务', fillcolor='#ffffff')
        with c.subgraph(name='cluster_bigdata') as bd:
            bd.attr(label='大数据平台', style='dashed')
            bd.node('spark', 'Spark\n集群', fillcolor='#ffffff')
            bd.node('hive', 'Hive\n数据仓库', fillcolor='#ffffff')
            bd.node('doris', 'Doris\nOLAP', fillcolor='#ffffff')
    
    # 监控平台
    with dot.subgraph(name='cluster_monitor') as c:
        c.attr(label='📊 运维监控平台', style='filled', fillcolor='#f5f5f5')
        c.node('prom', 'Prometheus', fillcolor='#ffffff')
        c.node('graf', 'Grafana', fillcolor='#ffffff')
        c.node('alert', 'AlertManager', fillcolor='#ffffff')
    
    # 连接
    dot.edge('ext1', 'fw', label='SFTP')
    dot.edge('ext2', 'fw')
    dot.edge('ext3', 'fw')
    dot.edge('fw', 'sftp', label='CN2网络\n10.141.208.176:12222')
    
    dot.edge('sftp', 'parse')
    dot.edge('parse', 'valid')
    dot.edge('valid', 'spark')
    dot.edge('spark', 'hive')
    dot.edge('spark', 'doris')
    
    dot.edge('prom', 'sftp', style='dotted', label='监控')
    dot.edge('graf', 'prom')
    
    # 渲染
    output_path = os.path.join(OUTPUT_DIR, '部署架构图')
    dot.render(output_path, cleanup=True)
    print(f"✅ 部署架构图: {output_path}.png")
    return f"{output_path}.png"


def create_db_arch():
    """创建数据库架构图"""
    dot = Digraph(comment='数据库架构', format='png')
    dot.attr(rankdir='TB', size='12,14', dpi='150')
    dot.attr('node', shape='box', style='rounded,filled', fontname='SimHei', fontsize='11')
    dot.attr('edge', fontname='SimHei', fontsize='9')
    
    # 应用层
    with dot.subgraph(name='cluster_app') as c:
        c.attr(label='📊 应用层 (Doris)', style='filled', fillcolor=COLORS['primary'], fontcolor='white')
        c.node('dash', 'Dashboard查询', fillcolor='#e8f4ff')
        c.node('api', 'API服务', fillcolor='#e8f4ff')
        c.node('report', '报表生成', fillcolor='#e8f4ff')
    
    # 汇总层
    with dot.subgraph(name='cluster_sum') as c:
        c.attr(label='📊 汇总层 (Hive)', style='filled', fillcolor='#006EBD', fontcolor='white')
        c.node('daily', '日汇总表\ntoken_daily_sum', fillcolor='#e8f4ff')
        c.node('monthly', '月汇总表\ntoken_monthly_sum', fillcolor='#e8f4ff')
        c.node('org', '单位汇总表\ntoken_org_sum', fillcolor='#e8f4ff')
    
    # 明细层
    with dot.subgraph(name='cluster_detail') as c:
        c.attr(label='📝 明细层 (Hive)', style='filled', fillcolor=COLORS['secondary'], fontcolor='white')
        c.node('detail', 'Token明细表\ntoken_detail\n分区: data_date', fillcolor='#ffe8e8')
        c.node('log', '操作日志表\ntoken_operation_log', fillcolor='#ffe8e8')
        c.node('err', '错误记录表\ntoken_error_record', fillcolor='#ffe8e8')
    
    # 主数据层
    with dot.subgraph(name='cluster_master') as c:
        c.attr(label='📚 主数据层 (MySQL/Doris)', style='filled', fillcolor=COLORS['neutral'], fontcolor='white')
        c.node('org_m', '单位主数据\ndim_org', fillcolor='#f5f5f5')
        c.node('model_m', '模型主数据\ndim_model', fillcolor='#f5f5f5')
        c.node('hw_m', '硬件主数据\ndim_hardware', fillcolor='#f5f5f5')
    
    # 连接
    dot.edge('detail', 'daily', label='日汇总\nETL')
    dot.edge('daily', 'monthly', label='月汇总')
    dot.edge('detail', 'org', label='单位汇总')
    
    dot.edge('daily', 'dash')
    dot.edge('monthly', 'report')
    dot.edge('detail', 'api')
    
    dot.edge('org_m', 'detail', style='dotted', label='关联')
    dot.edge('model_m', 'detail', style='dotted')
    
    # 渲染
    output_path = os.path.join(OUTPUT_DIR, '数据库架构图')
    dot.render(output_path, cleanup=True)
    print(f"✅ 数据库架构图: {output_path}.png")
    return f"{output_path}.png"


if __name__ == '__main__':
    print("=" * 50)
    print("生成Token采集系统架构图")
    print("=" * 50)
    
    img1 = create_overall_arch()
    img2 = create_deploy_arch()
    img3 = create_db_arch()
    
    print("\n✅ 所有架构图生成完成！")
    print(f"输出目录: {OUTPUT_DIR}")
