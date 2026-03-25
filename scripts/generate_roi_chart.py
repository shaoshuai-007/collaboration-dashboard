#!/usr/bin/env python3
# ROI数据图 - 麦肯锡风格（英文版）
import matplotlib.pyplot as plt
import numpy as np

# 麦肯锡配色
COLORS = {
    'primary': '#1A365D',
    'secondary': '#4A5568', 
    'accent': '#3182CE',
    'success': '#38A169',
    'light': '#EDF2F7'
}

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 左图：配案效率提升
ax1 = axes[0]
categories = ['Before\n(Manual)', 'After\n(AI)']
values = [30, 6]  # 分钟
bars1 = ax1.bar(categories, values, color=[COLORS['secondary'], COLORS['accent']], width=0.5)
ax1.set_ylabel('Time (minutes)', fontsize=12, color=COLORS['secondary'])
ax1.set_title('Efficiency: -80%', fontsize=14, fontweight='bold', color=COLORS['primary'])
ax1.set_ylim(0, 35)

# 添加数值标签
for bar, val in zip(bars1, values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
            f'{val}min', ha='center', fontsize=14, fontweight='bold')

# 添加箭头和提升标注
ax1.annotate('', xy=(1, 10), xytext=(0, 25),
            arrowprops=dict(arrowstyle='->', color=COLORS['success'], lw=3))
ax1.text(0.5, 17, '-80%', fontsize=16, fontweight='bold', color=COLORS['success'], ha='center')

# 右图：转化率提升
ax2 = axes[1]
categories = ['Before', 'After']
values = [35, 55]  # 百分比
bars2 = ax2.bar(categories, values, color=[COLORS['secondary'], COLORS['accent']], width=0.5)
ax2.set_ylabel('Conversion Rate (%)', fontsize=12, color=COLORS['secondary'])
ax2.set_title('Conversion: +57%', fontsize=14, fontweight='bold', color=COLORS['primary'])
ax2.set_ylim(0, 65)

# 添加数值标签
for bar, val in zip(bars2, values):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
            f'{val}%', ha='center', fontsize=14, fontweight='bold')

# 添加提升标注
ax2.annotate('', xy=(1, 60), xytext=(0, 40),
            arrowprops=dict(arrowstyle='->', color=COLORS['success'], lw=3))
ax2.text(0.5, 52, '+57%', fontsize=16, fontweight='bold', color=COLORS['success'], ha='center')

plt.suptitle('Hubei Telecom AI Smart Proposal - ROI', fontsize=16, fontweight='bold', color=COLORS['primary'], y=1.02)
plt.tight_layout()
plt.savefig('/root/.openclaw/workspace/03_输出成果/AI智能配案_ROI图.png', dpi=150, bbox_inches='tight', facecolor='white')
print("✅ ROI图已生成")
