#!/usr/bin/env python3
# 生成麦肯锡风格架构图
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

plt.rcParams['font.family'] = ['DejaVu Sans', 'WenQuanYi Zen Hei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 麦肯锡配色
COLOR = {
    'primary': '#1A365D',      # 深蓝
    'secondary': '#4A5568',     # 灰
    'accent': '#3182CE',        # 强调蓝
    'white': '#FFFFFF',
    'light': '#EDF2F7',
    'text': '#1A202C'
}

fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis('off')

# 标题
ax.text(7, 9.5, '湖北电信AI智能配案系统 - 总体架构', 
       ha='center', va='top', fontsize=20, fontweight='bold', color=COLOR['primary'])

# 五层架构
layers = [
    {'name': '数据应用层', 'y': 7.5, 'items': ['营销推荐引擎', '配案生成器', '数据分析看板'], 'color': '#2B6CB0'},
    {'name': '数据处理层', 'y': 5.8, 'items': ['需求解析', '产品匹配', '方案组装'], 'color': '#3182CE'},
    {'name': '数据采集层', 'y': 4.1, 'items': ['客户数据', '产品数据', '行为数据'], 'color': '#4299E1'},
    {'name': '数据源层', 'y': 2.4, 'items': ['BOSS系统', 'CRM系统', '营销平台'], 'color': '#63B3ED'},
    {'name': '基础支撑', 'y': 0.7, 'items': ['大模型能力', '知识库', '安全认证'], 'color': '#90CDF4'},
]

for layer in layers:
    # 层标题
    ax.text(1, layer['y'] + 0.3, layer['name'], fontsize=14, fontweight='bold', color=COLOR['primary'])
    
    # 层背景
    rect = FancyBboxPatch((0.5, layer['y'] - 0.2), 13, 1.2, 
                          boxstyle="round,pad=0.05", 
                          facecolor=COLOR['light'], 
                          edgecolor=COLOR['secondary'],
                          linewidth=1)
    ax.add_patch(rect)
    
    # 组件
    n = len(layer['items'])
    spacing = 12 / (n + 1)
    for i, item in enumerate(layer['items']):
        x = spacing * (i + 1)
        box = FancyBboxPatch((x - 1.3, layer['y']), 2.6, 0.8,
                            boxstyle="round,pad=0.02",
                            facecolor=COLOR['white'],
                            edgecolor=layer['color'],
                            linewidth=2)
        ax.add_patch(box)
        ax.text(x, layer['y'] + 0.4, item, ha='center', va='center', 
               fontsize=10, color=COLOR['text'], fontweight='bold')

# 箭头（层之间）
for i in range(len(layers)-1):
    ax.annotate('', xy=(7, layers[i+1]['y']+0.5), xytext=(7, layers[i]['y']-0.2),
               arrowprops=dict(arrowstyle='->', color=COLOR['secondary'], lw=2))

plt.tight_layout()
plt.savefig('/root/.openclaw/workspace/03_输出成果/AI智能配案_架构图.png', 
            dpi=150, bbox_inches='tight', facecolor='white')
print("✅ 架构图已生成")
