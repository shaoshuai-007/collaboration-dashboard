#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速审核脚本 - Quick Audit Script
用途：快速调用闭环质量系统，审核文档
创建时间：2026-03-23
创建者：南乔

使用方法：
    # 智能模式（推荐）
    python3 scripts/audit_doc.py 文档路径.md
    
    # 强制半自动
    python3 scripts/audit_doc.py 文档路径.md --mode semi
    
    # 强制全自动
    python3 scripts/audit_doc.py 文档路径.md --mode auto
    
    # 批量审核
    python3 scripts/audit_doc.py 03_输出成果/*.md
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from closed_loop_executor import ClosedLoopExecutor


def audit_single_file(file_path: str, mode: str = "smart") -> dict:
    """审核单个文件"""
    executor = ClosedLoopExecutor()
    return executor.execute(file_path, mode=mode)


def audit_batch(pattern: str, mode: str = "smart") -> list:
    """批量审核"""
    results = []
    executor = ClosedLoopExecutor()
    
    # 解析glob模式
    base_path = Path("/root/.openclaw/workspace")
    files = list(base_path.glob(pattern))
    
    print(f"\n{'='*70}")
    print(f"📋 批量审核")
    print(f"{'='*70}")
    print(f"匹配文件：{len(files)}个")
    print(f"模式：{mode}")
    print()
    
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] {file_path.name}")
        print(f"{'─'*70}")
        
        try:
            result = executor.execute(str(file_path), mode=mode)
            results.append({
                "file": str(file_path),
                "result": result,
            })
            
            # 打印结果
            if result["status"] == "passed":
                print(f"✅ 通过 | {result['final_grade']}级 | {result['final_score']}分")
            else:
                print(f"⚠️ {result['status']}")
        except Exception as e:
            print(f"❌ 错误：{e}")
            results.append({
                "file": str(file_path),
                "error": str(e),
            })
    
    # 汇总
    print(f"\n{'='*70}")
    print(f"📊 审核汇总")
    print(f"{'='*70}")
    
    passed = sum(1 for r in results if r.get("result", {}).get("status") == "passed")
    print(f"通过：{passed}/{len(files)}")
    
    return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="快速审核文档质量",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
    # 智能模式审核
    python3 scripts/audit_doc.py 文档.md
    
    # 半自动模式
    python3 scripts/audit_doc.py 文档.md --mode semi
    
    # 全自动模式
    python3 scripts/audit_doc.py 文档.md --mode auto
    
    # 批量审核
    python3 scripts/audit_doc.py "03_输出成果/**/*.md"
        """,
    )
    
    parser.add_argument("file", help="文件路径或glob模式")
    parser.add_argument("--mode", choices=["smart", "semi", "auto"], 
                        default="smart", help="审核模式（默认：smart）")
    parser.add_argument("--batch", action="store_true", 
                        help="批量审核模式")
    
    args = parser.parse_args()
    
    # 判断是单个文件还是批量
    if args.batch or "*" in args.file:
        # 批量模式
        results = audit_batch(args.file, mode=args.mode)
    else:
        # 单个文件
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = Path("/root/.openclaw/workspace") / file_path
        
        if not file_path.exists():
            print(f"❌ 文件不存在：{file_path}")
            sys.exit(1)
        
        result = audit_single_file(str(file_path), mode=args.mode)
        
        # 打印最终结果
        print(f"\n{'='*70}")
        print(f"📊 审核结果")
        print(f"{'='*70}")
        
        if result["status"] == "passed":
            print(f"✅ 审核通过")
            print(f"等级：{result['final_grade']}级")
            print(f"得分：{result['final_score']}分")
            print(f"迭代：{result['iterations']}轮")
        elif result["status"] == "waiting_confirmation":
            print(f"⏸️ 等待人工确认")
            print(f"消息：{result.get('message', '')}")
        else:
            print(f"⚠️ 状态：{result['status']}")


if __name__ == "__main__":
    main()
