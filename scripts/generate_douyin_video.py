#!/usr/bin/env python3
"""
NVIDIA GTC 2026 抖音短视频生成器
制作人：南乔 @ 九星智囊团
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
from pathlib import Path

# 配置
OUTPUT_DIR = Path("/root/.openclaw/workspace/03_输出成果")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 视频参数
WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 60  # 60秒

# 颜色
TECH_BLUE = (0, 110, 189)
NVIDIA_GREEN = (118, 185, 0)
DATA_RED = (201, 56, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 字体
def get_font(size):
    """获取字体"""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def create_frame(text_main, text_sub, frame_num, total_frames):
    """创建单帧"""
    # 创建渐变背景
    img = Image.new('RGB', (WIDTH, HEIGHT), TECH_BLUE)
    draw = ImageDraw.Draw(img)
    
    # 绘制渐变效果
    for y in range(HEIGHT):
        alpha = int(100 + 50 * (y / HEIGHT))
        color = (0, max(60, 110 - y // 20), min(189 + y // 10, 255))
        draw.line([(0, y), (WIDTH, y)], fill=color)
    
    # 绘制网格线（科技感）
    for x in range(0, WIDTH, 60):
        draw.line([(x, 0), (x, HEIGHT)], fill=(0, 80, 150, 30), width=1)
    for y in range(0, HEIGHT, 60):
        draw.line([(0, y), (WIDTH, y)], fill=(0, 80, 150, 30), width=1)
    
    # NVIDIA Logo区域（顶部）
    draw.rectangle([(0, 0), (WIDTH, 120)], fill=BLACK)
    font_logo = get_font(48)
    draw.text((40, 40), "NVIDIA GTC 2026", font=font_logo, fill=NVIDIA_GREEN)
    
    # 主标题
    font_main = get_font(120)
    bbox = draw.textbbox((0, 0), text_main, font=font_main)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    y = 600
    draw.text((x, y), text_main, font=font_main, fill=WHITE)
    
    # 副标题
    if text_sub:
        font_sub = get_font(60)
        bbox = draw.textbbox((0, 0), text_sub, font=font_sub)
        text_width = bbox[2] - bbox[0]
        x = (WIDTH - text_width) // 2
        draw.text((x, y + 160), text_sub, font=font_sub, fill=DATA_RED)
    
    # 底部品牌
    draw.rectangle([(0, HEIGHT - 100), (WIDTH, HEIGHT)], fill=BLACK)
    font_brand = get_font(36)
    draw.text((40, HEIGHT - 70), "九星智囊团出品", font=font_brand, fill=WHITE)
    
    return img

def main():
    """主函数"""
    print("开始生成NVIDIA GTC 2026抖音视频...")
    
    # 创建帧目录
    frames_dir = OUTPUT_DIR / "video_frames"
    frames_dir.mkdir(exist_ok=True)
    
    # 视频内容脚本（60秒）
    scenes = [
        # (主文字, 副文字, 持续秒数)
        ("NVIDIA GTC 2026", "黄仁勋主题演讲", 3),
        ("AI计算需求", "两年增长100万倍", 5),
        ("1,000,000倍", "不是100倍，是100万倍", 5),
        ("$1万亿", "AI计算需求预测", 5),
        ("Vera Rubin", "3.6 exaflops算力", 5),
        ("能效提升50倍", "相比Hopper", 5),
        ("OpenClaw开源", "代理计算机的操作系统", 5),
        ("两行命令", "部署AI代理", 5),
        ("自动驾驶", "ChatGPT时刻来临", 5),
        ("1800万辆车", "7大车企年产", 5),
        ("Token经济", "数据中心变工厂", 5),
        ("AI时代", "基础设施革命", 7),
    ]
    
    frame_count = 0
    
    for scene_idx, (main_text, sub_text, duration) in enumerate(scenes):
        frames_in_scene = duration * FPS
        
        print(f"生成场景 {scene_idx + 1}/{len(scenes)}: {main_text}")
        
        for i in range(frames_in_scene):
            img = create_frame(main_text, sub_text, i, frames_in_scene)
            frame_path = frames_dir / f"frame_{frame_count:05d}.png"
            img.save(frame_path)
            frame_count += 1
    
    print(f"共生成 {frame_count} 帧")
    
    # 使用ffmpeg合成视频
    output_video = OUTPUT_DIR / "NVIDIA_GTC_2026_抖音_60秒.mp4"
    
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%05d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        str(output_video)
    ]
    
    print("合成视频...")
    subprocess.run(cmd, capture_output=True)
    
    # 清理帧文件
    print("清理临时文件...")
    for f in frames_dir.glob("*.png"):
        f.unlink()
    frames_dir.rmdir()
    
    print(f"\n✅ 视频生成完成！")
    print(f"文件: {output_video}")
    print(f"分辨率: {WIDTH}x{HEIGHT}")
    print(f"时长: {DURATION}秒")

if __name__ == "__main__":
    main()
