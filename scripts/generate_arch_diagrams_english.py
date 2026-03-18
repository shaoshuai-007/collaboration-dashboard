#!/usr/bin/env python3
"""
Token Collection System Architecture Diagrams (English Version)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

# Output directory
OUTPUT_DIR = "/root/.openclaw/workspace/03_输出成果/Token采集需求分析/arch_diagrams"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Color scheme
COLORS = {
    'primary': '#006EBD',      # Deep Blue
    'secondary': '#C93832',    # Red
    'neutral': '#595959',      # Gray
    'light_blue': '#e8f4ff',
    'light_red': '#ffe8e8',
    'white': '#ffffff'
}


def draw_box(ax, x, y, width, height, text, color, text_color='black', fontsize=10):
    """Draw rounded rectangle box"""
    box = FancyBboxPatch((x, y), width, height,
                          boxstyle="round,pad=0.02,rounding_size=0.1",
                          facecolor=color, edgecolor='black', linewidth=1)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text, ha='center', va='center',
            fontsize=fontsize, color=text_color, wrap=True)
    return box


def create_overall_arch():
    """Create Overall Architecture Diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 20))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 20)
    ax.axis('off')
    
    # Title
    ax.text(8, 19.5, 'Token Collection System - Overall Architecture', 
            ha='center', fontsize=16, fontweight='bold')
    
    # Layer 4: Data Application Layer
    draw_box(ax, 0.5, 16, 15, 2.5, '', COLORS['primary'])
    ax.text(8, 18.2, 'Layer 4: Data Application', ha='center', fontsize=12, 
            color='white', fontweight='bold')
    
    # Application components
    apps = ['Token Stats\nDashboard', 'Cost Analysis\nDashboard', 'Evaluation\nDashboard', 
            'Visual Reports', 'Query API']
    for i, app in enumerate(apps):
        draw_box(ax, 1 + i*3, 16.2, 2.5, 1.2, app, COLORS['light_blue'], fontsize=9)
    
    # Layer 3: Data Processing Layer
    draw_box(ax, 0.5, 12, 15, 3, '', COLORS['primary'])
    ax.text(8, 14.7, 'Layer 3: Data Processing', ha='center', fontsize=12, 
            color='white', fontweight='bold')
    
    # Processing components
    proc = ['Data Cleaning', 'Data Transform', 'Data Loading', 'Data Summary']
    for i, p in enumerate(proc):
        draw_box(ax, 1 + i*3.5, 12.5, 2.8, 1.2, p, COLORS['light_blue'], fontsize=10)
        if i < 3:
            ax.annotate('', xy=(4.3 + i*3.5, 13.1), xytext=(3.8 + i*3.5, 13.1),
                       arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    # Layer 2: Data Collection Layer
    draw_box(ax, 0.5, 7, 15, 4, '', COLORS['secondary'])
    ax.text(8, 10.7, 'Layer 2: Data Collection', ha='center', fontsize=12, 
            color='white', fontweight='bold')
    
    # Collection components
    collect = ['SFTP Receiver', 'File Parser', 'File Validator', 'Receipt Generator']
    for i, c in enumerate(collect):
        draw_box(ax, 1 + i*3.5, 8, 2.8, 1.2, c, COLORS['light_red'], fontsize=10)
        if i < 3:
            ax.annotate('', xy=(4.3 + i*3.5, 8.6), xytext=(3.8 + i*3.5, 8.6),
                       arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    # Support tools
    tools = ['Task Scheduler\n(Airflow)', 'File Monitor\n(Watchdog)', 'Logging\n(Loguru)']
    for i, t in enumerate(tools):
        draw_box(ax, 2 + i*4, 7.3, 3, 0.8, t, '#f5f5f5', fontsize=9)
    
    # Layer 1: Data Source Layer
    draw_box(ax, 0.5, 3, 15, 3, '', COLORS['secondary'])
    ax.text(8, 5.7, 'Layer 1: Data Sources', ha='center', fontsize=12, 
            color='white', fontweight='bold')
    
    # Data sources
    sources = ['HQ Departments\n(23 units)', 'Subsidiaries\n(26 units)', 
               'Provincial\n(31 units)', 'Branches\n(6 units)']
    for i, s in enumerate(sources):
        draw_box(ax, 1 + i*3.5, 3.5, 2.8, 1.2, s, COLORS['light_red'], fontsize=10)
    
    # Support System
    draw_box(ax, 0.5, 0.5, 15, 2, '', COLORS['neutral'])
    ax.text(8, 2.3, 'Support System', ha='center', fontsize=12, 
            color='white', fontweight='bold')
    
    support = ['Monitoring\nPrometheus', 'Logging\nELK', 'Config\nNacos', 
               'Access Control\nRBAC', 'Encryption\nTLS']
    for i, s in enumerate(support):
        draw_box(ax, 0.8 + i*2.9, 0.8, 2.5, 1, s, '#f5f5f5', fontsize=8)
    
    # Layer connections
    ax.annotate('', xy=(8, 12), xytext=(8, 11),
               arrowprops=dict(arrowstyle='->', color='gray', lw=2, ls='--'))
    ax.text(8.3, 11.5, 'SFTP Transfer', fontsize=9, color='gray')
    
    ax.annotate('', xy=(8, 16), xytext=(8, 15),
               arrowprops=dict(arrowstyle='->', color='gray', lw=2, ls='--'))
    ax.text(8.3, 15.5, 'Data Push', fontsize=9, color='gray')
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'Overall_Architecture.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Overall Architecture: {output_path}")
    return output_path


def create_deploy_arch():
    """Create Deployment Architecture Diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(8, 11.5, 'Token Collection System - Deployment Architecture', 
            ha='center', fontsize=16, fontweight='bold')
    
    # External Network
    draw_box(ax, 0.5, 8, 4.5, 3, '', '#e8f4ff')
    ax.text(2.75, 10.7, 'External Network', ha='center', fontsize=11, fontweight='bold')
    
    ext = ['HQ Depts\n(23 units)', 'Subsidiaries\n(26 units)', 'Provinces\n(31 units)']
    for i, e in enumerate(ext):
        draw_box(ax, 0.8, 8.3 + i*0.9, 3.9, 0.8, e, COLORS['white'], fontsize=9)
    
    # CN2 Network
    draw_box(ax, 5.5, 8, 2, 3, '', '#ffe8e8')
    ax.text(6.5, 10.7, 'CN2 Network', ha='center', fontsize=10, fontweight='bold')
    draw_box(ax, 5.7, 8.5, 1.6, 1, 'Firewall', COLORS['white'], fontsize=9)
    
    # Production Environment
    draw_box(ax, 8, 5.5, 7.5, 5.5, '', '#e8ffe8')
    ax.text(11.75, 10.7, 'Production Environment', ha='center', fontsize=11, fontweight='bold')
    
    # Application Cluster
    draw_box(ax, 8.3, 7.5, 3, 2.5, '', '#d0f0d0')
    ax.text(9.8, 9.7, 'App Cluster', ha='center', fontsize=10, fontweight='bold')
    apps = ['SFTP Server\n:12222', 'Parser Service', 'Validator Service']
    for i, a in enumerate(apps):
        draw_box(ax, 8.5, 7.7 + i*0.7, 2.6, 0.6, a, COLORS['white'], fontsize=8)
    
    # Big Data Platform
    draw_box(ax, 11.8, 7.5, 3.4, 2.5, '', '#d0f0d0')
    ax.text(13.5, 9.7, 'Big Data Platform', ha='center', fontsize=10, fontweight='bold')
    bigdata = ['Spark Cluster', 'Hive Warehouse', 'Doris OLAP']
    for i, b in enumerate(bigdata):
        draw_box(ax, 12, 7.7 + i*0.7, 3, 0.6, b, COLORS['white'], fontsize=8)
    
    # Monitoring Platform
    draw_box(ax, 8, 0.5, 7.5, 2, '', '#f5f5f5')
    ax.text(11.75, 2.3, 'Operations Monitoring', ha='center', fontsize=10, fontweight='bold')
    mon = ['Prometheus', 'Grafana', 'AlertManager']
    for i, m in enumerate(mon):
        draw_box(ax, 8.3 + i*2.4, 0.8, 2.2, 0.8, m, COLORS['white'], fontsize=9)
    
    # Network Info
    draw_box(ax, 0.5, 5, 7, 2.5, '', '#fff8e8')
    ax.text(4, 7.2, 'Network Info', ha='center', fontsize=10, fontweight='bold')
    ax.text(4, 6.3, 'SFTP Server: 10.141.208.176:12222\nCN2-1124 Telecom Network', 
           ha='center', fontsize=9, va='center')
    draw_box(ax, 0.8, 5.3, 6.4, 0.7, 'Data File Transfer (DAT.gz)', COLORS['white'], fontsize=9)
    
    # Connection arrows
    ax.annotate('', xy=(5.5, 9.5), xytext=(5, 9.5),
               arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    ax.annotate('', xy=(8, 8.5), xytext=(7.5, 8.5),
               arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'Deployment_Architecture.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Deployment Architecture: {output_path}")
    return output_path


def create_db_arch():
    """Create Database Architecture Diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 16))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 16)
    ax.axis('off')
    
    # Title
    ax.text(7, 15.5, 'Token Collection System - Database Architecture', 
            ha='center', fontsize=16, fontweight='bold')
    
    # Application Layer
    draw_box(ax, 0.5, 12.5, 13, 2, '', COLORS['primary'])
    ax.text(7, 14.3, 'Application Layer (Doris)', ha='center', fontsize=12, 
            color='white', fontweight='bold')
    apps = ['Dashboard Query', 'API Service', 'Report Generation']
    for i, a in enumerate(apps):
        draw_box(ax, 1 + i*4, 12.8, 3.5, 1, a, COLORS['light_blue'], fontsize=10)
    
    # Summary Layer
    draw_box(ax, 0.5, 9, 13, 2.5, '', COLORS['primary'])
    ax.text(7, 11.2, 'Summary Layer (Hive)', ha='center', fontsize=12, 
            color='white', fontweight='bold')
    sums = ['Daily Summary\ntoken_daily_sum', 'Monthly Summary\ntoken_monthly_sum', 
            'Org Summary\ntoken_org_sum']
    for i, s in enumerate(sums):
        draw_box(ax, 1 + i*4, 9.3, 3.5, 1.3, s, COLORS['light_blue'], fontsize=9)
    
    # Detail Layer
    draw_box(ax, 0.5, 5, 13, 3, '', COLORS['secondary'])
    ax.text(7, 7.7, 'Detail Layer (Hive)', ha='center', fontsize=12, 
            color='white', fontweight='bold')
    details = ['Token Detail\ntoken_detail\nPartition: data_date', 
               'Operation Log\ntoken_operation_log',
               'Error Record\ntoken_error_record']
    for i, d in enumerate(details):
        draw_box(ax, 1 + i*4, 5.3, 3.5, 1.5, d, COLORS['light_red'], fontsize=9)
    
    # Master Data Layer
    draw_box(ax, 0.5, 1.5, 13, 2.5, '', COLORS['neutral'])
    ax.text(7, 3.7, 'Master Data Layer (MySQL/Doris)', ha='center', fontsize=12, 
            color='white', fontweight='bold')
    masters = ['Org Master\ndim_org', 'Model Master\ndim_model', 
               'Hardware Master\ndim_hardware', 'App Master\ndim_app']
    for i, m in enumerate(masters):
        draw_box(ax, 0.8 + i*3.1, 1.8, 2.8, 1.2, m, '#f5f5f5', fontsize=9)
    
    # Connection arrows
    ax.annotate('', xy=(7, 9), xytext=(7, 8.5),
               arrowprops=dict(arrowstyle='->', color='gray', lw=2))
    ax.text(7.3, 8.8, 'Daily ETL', fontsize=8, color='gray')
    
    ax.annotate('', xy=(7, 12.5), xytext=(7, 12),
               arrowprops=dict(arrowstyle='->', color='gray', lw=2))
    ax.text(7.3, 12.3, 'Query Service', fontsize=8, color='gray')
    
    # Partition strategy
    draw_box(ax, 0.5, 0.3, 13, 0.8, '', '#fff8e8')
    ax.text(7, 0.7, 'Partition: Daily by data_date | Retention: Detail 180 days, Summary 3 years', 
           ha='center', fontsize=9)
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'Database_Architecture.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Database Architecture: {output_path}")
    return output_path


if __name__ == '__main__':
    print("=" * 60)
    print("Token Collection System Architecture Diagrams (English)")
    print("=" * 60)
    
    img1 = create_overall_arch()
    img2 = create_deploy_arch()
    img3 = create_db_arch()
    
    print("\nAll diagrams generated successfully!")
    print(f"Output directory: {OUTPUT_DIR}")
