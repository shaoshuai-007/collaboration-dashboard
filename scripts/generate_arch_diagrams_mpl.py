#!/usr/bin/env python3
"""
使用matplotlib绘制Token采集系统架构图
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 输出目录
OUTPUT_DIR = "/root/.openclaw/workspace/03_输出成果/Token采集需求分析/arch_diagrams"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 颜色定义
COLORS = {
    'primary': '#006EBD',      # 深蓝
    'secondary': '#C93832',    # 电信红
    'neutral': '#595959',      # 灰色
    'light_blue': '#e8f4ff',
    'light_red': '#ffe8e8',
    'white': '#ffffff'
}


def draw_box(ax, x, y, width, height, text, color, text_color='black', fontsize=10):
    """绘制圆角矩形框"""
    box = FancyBboxPatch((x, y), width, height,
                          boxstyle="round,pad=0.02,rounding_size=0.1",
                          facecolor=color, edgecolor='black', linewidth=1)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text, ha='center', va='center',
            fontsize=fontsize, color=text_color, wrap=True)
    return box


def create_overall_arch():
    """创建总体架构图"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 20))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 20)
    ax.axis('off')
    
    # 标题
    ax.text(8, 19.5, 'Token采集系统总体架构', ha='center', fontsize=16, fontweight='bold')
    
    # Layer 4: 数据应用层
    draw_box(ax, 0.5, 16, 15, 2.5, '', COLORS['primary'])
    ax.text(8, 18.2, '📊 数据应用层 (Layer 4)', ha='center', fontsize=12, color='white', fontweight='bold')
    
    # 应用层组件
    apps = ['Token统计\nDashboard', '成本分析\nDashboard', '效果评估\nDashboard', '可视化报表', '数据查询API']
    for i, app in enumerate(apps):
        draw_box(ax, 1 + i*3, 16.2, 2.5, 1.2, app, COLORS['light_blue'], fontsize=9)
    
    # Layer 3: 数据处理层
    draw_box(ax, 0.5, 12, 15, 3, '', COLORS['primary'])
    ax.text(8, 14.7, '⚙️ 数据处理层 (Layer 3)', ha='center', fontsize=12, color='white', fontweight='bold')
    
    # 处理组件
    proc = ['数据清洗', '数据转换', '数据入库', '数据汇总']
    for i, p in enumerate(proc):
        draw_box(ax, 1 + i*3.5, 12.5, 2.8, 1.2, p, COLORS['light_blue'], fontsize=10)
        if i < 3:
            ax.annotate('', xy=(4.3 + i*3.5, 13.1), xytext=(3.8 + i*3.5, 13.1),
                       arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    # Layer 2: 数据采集层
    draw_box(ax, 0.5, 7, 15, 4, '', COLORS['secondary'])
    ax.text(8, 10.7, '📥 数据采集层 (Layer 2)', ha='center', fontsize=12, color='white', fontweight='bold')
    
    # 采集组件
    collect = ['SFTP接收', '文件解析', '文件校验', '回执生成']
    for i, c in enumerate(collect):
        draw_box(ax, 1 + i*3.5, 8, 2.8, 1.2, c, COLORS['light_red'], fontsize=10)
        if i < 3:
            ax.annotate('', xy=(4.3 + i*3.5, 8.6), xytext=(3.8 + i*3.5, 8.6),
                       arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    # 支撑工具
    tools = ['任务调度\nAirflow', '文件监控\nWatchdog', '日志记录\nLoguru']
    for i, t in enumerate(tools):
        draw_box(ax, 2 + i*4, 7.3, 3, 0.8, t, '#f5f5f5', fontsize=9)
    
    # Layer 1: 数据源层
    draw_box(ax, 0.5, 3, 15, 3, '', COLORS['secondary'])
    ax.text(8, 5.7, '🏢 数据源层 (Layer 1)', ha='center', fontsize=12, color='white', fontweight='bold')
    
    # 数据源
    sources = ['总部部门\n(23个)', '专业公司\n(26个)', '省公司\n(31个)', '直属机构\n(6个)']
    for i, s in enumerate(sources):
        draw_box(ax, 1 + i*3.5, 3.5, 2.8, 1.2, s, COLORS['light_red'], fontsize=10)
    
    # 支撑体系
    draw_box(ax, 0.5, 0.5, 15, 2, '', COLORS['neutral'])
    ax.text(8, 2.3, '🛠️ 支撑体系', ha='center', fontsize=12, color='white', fontweight='bold')
    
    support = ['监控告警\nPrometheus', '日志管理\nELK', '配置管理\nNacos', '访问控制\nRBAC', '数据加密\nTLS']
    for i, s in enumerate(support):
        draw_box(ax, 0.8 + i*2.9, 0.8, 2.5, 1, s, '#f5f5f5', fontsize=8)
    
    # 层间连接箭头
    ax.annotate('', xy=(8, 12), xytext=(8, 11),
               arrowprops=dict(arrowstyle='->', color='gray', lw=2, ls='--'))
    ax.text(8.3, 11.5, 'SFTP传输', fontsize=9, color='gray')
    
    ax.annotate('', xy=(8, 16), xytext=(8, 15),
               arrowprops=dict(arrowstyle='->', color='gray', lw=2, ls='--'))
    ax.text(8.3, 15.5, '数据推送', fontsize=9, color='gray')
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, '总体架构图.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ 总体架构图: {output_path}")
    return output_path


def create_deploy_arch():
    """创建部署架构图"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # 标题
    ax.text(8, 11.5, 'Token采集系统部署架构', ha='center', fontsize=16, fontweight='bold')
    
    # 外部网络
    draw_box(ax, 0.5, 8, 4.5, 3, '', '#e8f4ff')
    ax.text(2.75, 10.7, '🌐 外部网络', ha='center', fontsize=11, fontweight='bold')
    
    ext = ['总部部门\n(23个)', '专业公司\n(26个)', '省公司\n(31个)']
    for i, e in enumerate(ext):
        draw_box(ax, 0.8, 8.3 + i*0.9, 3.9, 0.8, e, COLORS['white'], fontsize=9)
    
    # CN2网络
    draw_box(ax, 5.5, 8, 2, 3, '', '#ffe8e8')
    ax.text(6.5, 10.7, '🔒 CN2网络', ha='center', fontsize=10, fontweight='bold')
    draw_box(ax, 5.7, 8.5, 1.6, 1, '防火墙', COLORS['white'], fontsize=9)
    
    # 生产环境
    draw_box(ax, 8, 5.5, 7.5, 5.5, '', '#e8ffe8')
    ax.text(11.75, 10.7, '🖥️ 生产环境', ha='center', fontsize=11, fontweight='bold')
    
    # 应用集群
    draw_box(ax, 8.3, 7.5, 3, 2.5, '', '#d0f0d0')
    ax.text(9.8, 9.7, '应用集群', ha='center', fontsize=10, fontweight='bold')
    apps = ['SFTP服务\n:12222', '解析服务', '校验服务']
    for i, a in enumerate(apps):
        draw_box(ax, 8.5, 7.7 + i*0.7, 2.6, 0.6, a, COLORS['white'], fontsize=8)
    
    # 大数据平台
    draw_box(ax, 11.8, 7.5, 3.4, 2.5, '', '#d0f0d0')
    ax.text(13.5, 9.7, '大数据平台', ha='center', fontsize=10, fontweight='bold')
    bigdata = ['Spark集群', 'Hive仓库', 'Doris OLAP']
    for i, b in enumerate(bigdata):
        draw_box(ax, 12, 7.7 + i*0.7, 3, 0.6, b, COLORS['white'], fontsize=8)
    
    # 监控平台
    draw_box(ax, 8, 0.5, 7.5, 2, '', '#f5f5f5')
    ax.text(11.75, 2.3, '📊 运维监控平台', ha='center', fontsize=10, fontweight='bold')
    mon = ['Prometheus', 'Grafana', 'AlertManager']
    for i, m in enumerate(mon):
        draw_box(ax, 8.3 + i*2.4, 0.8, 2.2, 0.8, m, COLORS['white'], fontsize=9)
    
    # 网络信息
    draw_box(ax, 0.5, 5, 7, 2.5, '', '#fff8e8')
    ax.text(4, 7.2, '📍 网络信息', ha='center', fontsize=10, fontweight='bold')
    ax.text(4, 6.3, 'SFTP服务器: 10.141.208.176:12222\nCN2-1124 电信专网', 
           ha='center', fontsize=9, va='center')
    draw_box(ax, 0.8, 5.3, 6.4, 0.7, '数据文件传输 (DAT.gz)', COLORS['white'], fontsize=9)
    
    # 连接箭头
    ax.annotate('', xy=(5.5, 9.5), xytext=(5, 9.5),
               arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    ax.annotate('', xy=(8, 8.5), xytext=(7.5, 8.5),
               arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, '部署架构图.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ 部署架构图: {output_path}")
    return output_path


def create_db_arch():
    """创建数据库架构图"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 16))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 16)
    ax.axis('off')
    
    # 标题
    ax.text(7, 15.5, 'Token采集系统数据库架构', ha='center', fontsize=16, fontweight='bold')
    
    # 应用层
    draw_box(ax, 0.5, 12.5, 13, 2, '', COLORS['primary'])
    ax.text(7, 14.3, '📊 应用层 (Doris)', ha='center', fontsize=12, color='white', fontweight='bold')
    apps = ['Dashboard查询', 'API服务', '报表生成']
    for i, a in enumerate(apps):
        draw_box(ax, 1 + i*4, 12.8, 3.5, 1, a, COLORS['light_blue'], fontsize=10)
    
    # 汇总层
    draw_box(ax, 0.5, 9, 13, 2.5, '', COLORS['primary'])
    ax.text(7, 11.2, '📊 汇总层 (Hive)', ha='center', fontsize=12, color='white', fontweight='bold')
    sums = ['日汇总表\ntoken_daily_sum', '月汇总表\ntoken_monthly_sum', '单位汇总表\ntoken_org_sum']
    for i, s in enumerate(sums):
        draw_box(ax, 1 + i*4, 9.3, 3.5, 1.3, s, COLORS['light_blue'], fontsize=9)
    
    # 明细层
    draw_box(ax, 0.5, 5, 13, 3, '', COLORS['secondary'])
    ax.text(7, 7.7, '📝 明细层 (Hive)', ha='center', fontsize=12, color='white', fontweight='bold')
    details = ['Token明细表\ntoken_detail\n分区: data_date', 
               '操作日志表\ntoken_operation_log',
               '错误记录表\ntoken_error_record']
    for i, d in enumerate(details):
        draw_box(ax, 1 + i*4, 5.3, 3.5, 1.5, d, COLORS['light_red'], fontsize=9)
    
    # 主数据层
    draw_box(ax, 0.5, 1.5, 13, 2.5, '', COLORS['neutral'])
    ax.text(7, 3.7, '📚 主数据层 (MySQL/Doris)', ha='center', fontsize=12, color='white', fontweight='bold')
    masters = ['单位主数据\ndim_org', '模型主数据\ndim_model', '硬件主数据\ndim_hardware', '应用主数据\ndim_app']
    for i, m in enumerate(masters):
        draw_box(ax, 0.8 + i*3.1, 1.8, 2.8, 1.2, m, '#f5f5f5', fontsize=9)
    
    # 连接箭头
    ax.annotate('', xy=(7, 9), xytext=(7, 8.5),
               arrowprops=dict(arrowstyle='->', color='gray', lw=2))
    ax.text(7.3, 8.8, '日汇总ETL', fontsize=8, color='gray')
    
    ax.annotate('', xy=(7, 12.5), xytext=(7, 12),
               arrowprops=dict(arrowstyle='->', color='gray', lw=2))
    ax.text(7.3, 12.3, '查询服务', fontsize=8, color='gray')
    
    # 分区策略说明
    draw_box(ax, 0.5, 0.3, 13, 0.8, '', '#fff8e8')
    ax.text(7, 0.7, '⏰ 分区策略: 按data_date日分区 | 生命周期: 明细层180天, 汇总层3年', 
           ha='center', fontsize=9)
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, '数据库架构图.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ 数据库架构图: {output_path}")
    return output_path


if __name__ == '__main__':
    print("=" * 50)
    print("生成Token采集系统架构图 (matplotlib版)")
    print("=" * 50)
    
    img1 = create_overall_arch()
    img2 = create_deploy_arch()
    img3 = create_db_arch()
    
    print("\n✅ 所有架构图生成完成！")
    print(f"输出目录: {OUTPUT_DIR}")
