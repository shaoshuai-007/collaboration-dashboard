#!/usr/bin/env python3
"""
湖北电信AI智能配案系统 - 麦肯锡配色版
配色：#1A365D #4A5568 #3182CE
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 麦肯锡配色方案
color_scheme = {
    "color1": "#1A365D",  # 主色 - 数据应用层 / 基础支撑
    "color2": "#3182CE",  # 辅色 - 数据处理层、数据采集层
    "color3": "#4A5568",  # 基底色 - 数据源层
    "support": "#1A365D", # 基础支撑
}

fig, ax = plt.subplots(1, 1, figsize=(18, 11))
ax.set_xlim(0, 18)
ax.set_ylim(0, 11)
ax.axis('off')
fig.patch.set_facecolor('#F8FAFC')

ax.text(9, 10.5, "湖北电信AI智能配案系统", fontsize=22, fontweight='bold', 
        ha='center', va='center', color='#1E293B')

# 布局参数
left_margin = 0.3
right_margin = 3.5
content_width = 18 - left_margin - right_margin

layer_height = 1.4
layer_gap = 0.35
start_y = 9.5

# 五层架构
layers = [
    {"name": "数据应用层", "components": ["营销推荐引擎", "配案生成器", "数据分析看板"]},
    {"name": "数据处理层", "components": ["需求解析", "产品匹配", "方案组装"]},
    {"name": "数据采集层", "components": ["客户数据", "产品数据", "行为数据"]},
    {"name": "数据源层", "components": ["BOSS系统", "CRM系统", "营销平台"]},
    {"name": "基础支撑", "components": ["大模型能力", "知识库", "安全认证"]}
]

# 麦肯锡配色：主色-辅色-辅色-基底色-主色
layer_colors = [color_scheme["color1"], color_scheme["color2"], 
               color_scheme["color2"], color_scheme["color3"], color_scheme["color1"]]

total_content_height = len(layers) * layer_height + (len(layers) - 1) * layer_gap
content_top = start_y + layer_height/2 + 0.08
content_bottom = start_y - (len(layers) - 1) * (layer_height + layer_gap) - layer_height/2 - 0.08

comp_width = 2.5
comp_height = 1.0
gap = 0.5

for i, layer in enumerate(layers):
    y = start_y - i * (layer_height + layer_gap)
    layer_color = layer_colors[i]
    
    layer_bg = FancyBboxPatch(
        (left_margin, y - layer_height/2 - 0.08), content_width, layer_height + 0.16,
        boxstyle="round,pad=0.04,rounding_size=0.15",
        facecolor=layer_color, alpha=0.06, edgecolor=layer_color, linewidth=1.5
    )
    ax.add_patch(layer_bg)
    
    ax.text(left_margin - 0.1, y, layer["name"], fontsize=12, fontweight='bold',
            ha='right', va='center', color=layer_color, rotation=90)
    
    components = layer["components"]
    n_comp = len(components)
    comp_total_width = n_comp * comp_width + (n_comp - 1) * gap
    comp_start_x = left_margin + (content_width - comp_total_width) / 2
    
    for j, comp in enumerate(components):
        x = comp_start_x + j * (comp_width + gap)
        comp_box = FancyBboxPatch(
            (x, y - comp_height/2), comp_width, comp_height,
            boxstyle="round,pad=0.02,rounding_size=0.1",
            facecolor=layer_color, edgecolor='white', linewidth=1.5, alpha=0.9
        )
        ax.add_patch(comp_box)
        ax.text(x + comp_width/2, y, comp, fontsize=10,
                ha='center', va='center', color='white', fontweight='bold')
    
    if i < len(layers) - 1:
        arrow_y = y - layer_height/2 - layer_gap/2
        ax.annotate('', xy=(8, arrow_y - 0.12), xytext=(8, arrow_y + 0.12),
                   arrowprops=dict(arrowstyle='-|>', color='#64748B', lw=2, mutation_scale=12))

ax.text(8, 0.35, "数据流向：数据源层 → 数据采集层 → 数据处理层 → 数据应用层", 
        fontsize=10, ha='center', va='center', color='#64748B', style='italic')

plt.tight_layout()
plt.savefig("/root/.openclaw/workspace/03_输出成果/AI智能配案_架构图_v3.png", 
            dpi=150, bbox_inches='tight', facecolor='#F8FAFC')
plt.close()
print("生成完成!")
