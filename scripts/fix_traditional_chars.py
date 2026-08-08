#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复转录结果中的繁体字问题
"""

import os
import sys
import json
from pathlib import Path

# 导入改进的转换器
try:
    from improved_converter import convert_to_simplified_chinese, detect_traditional_chars
    print("成功导入改进的转换器")
except ImportError:
    print("警告：无法导入改进的转换器，使用原版转换器")
    # 使用原版的转换逻辑
    def convert_to_simplified_chinese(text):
        """简化的繁体字转换"""
        if not text:
            return text

        try:
            from opencc import OpenCC
            cc = OpenCC('t2s')
            return cc.convert(text)
        except:
            # 基本替换
            basic_map = {
                '會': '会', '務': '务', '術': '术', '預': '预', '寫': '写', '檔': '档',
                '實': '实', '現': '现', '學': '学', '習': '习', '資': '资', '料': '料',
                '計': '计', '畫': '画', '過': '过', '為': '为', '這': '这', '樣': '样'
            }
            result = text
            for k, v in basic_map.items():
                result = result.replace(k, v)
            return result

def fix_single_transcript(file_path):
    """修复单个转录文件"""
    md_file = Path(file_path)

    if not md_file.exists():
        print(f"文件不存在: {md_file}")
        return False

    try:
        # 读取文件
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检测繁体字
        traditional_chars = detect_traditional_chars(content)

        if traditional_chars:
            print(f"  发现 {len(traditional_chars)} 个繁体字")
            print(f"  前10个繁体字: {traditional_chars[:10]}")

            # 转换为简体
            simplified_content = convert_to_simplified_chinese(content)

            # 保存修复后的文件
            backup_file = md_file.with_suffix('.md.backup')
            os.rename(md_file, backup_file)

            with open(md_file, 'w', encoding='utf-8-sig') as f:
                f.write(simplified_content)

            print(f"  [成功] 已修复并创建备份")
            return True
        else:
            print(f"  [成功] 已是简体中文，无需修复")
            return False

    except Exception as e:
        print(f"  [失败] 处理失败: {e}")
        return False

def fix_existing_transcripts():
    """修复已存在的转录文件"""
    # 查找转录文件
    transcript_dir = Path(r"C:\Users\lenovo\translate")

    if not transcript_dir.exists():
        print(f"转录目录不存在: {transcript_dir}")
        return

    # 查找所有 .md 文件
    md_files = list(transcript_dir.glob("**/*.md"))

    print(f"找到 {len(md_files)} 个转录文件")

    fixed_files = []

    for md_file in md_files:
        print(f"\n正在处理: {md_file.name}")

        try:
            # 读取文件
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检测繁体字
            traditional_chars = detect_traditional_chars(content)

            if traditional_chars:
                print(f"  发现 {len(traditional_chars)} 个繁体字")
                print(f"  前10个繁体字: {traditional_chars[:10]}")

                # 转换为简体
                simplified_content = convert_to_simplified_chinese(content)

                # 保存修复后的文件
                backup_file = md_file.with_suffix('.md.backup')
                os.rename(md_file, backup_file)

                with open(md_file, 'w', encoding='utf-8-sig') as f:
                    f.write(simplified_content)

                fixed_files.append({
                    'file': str(md_file),
                    'backup': str(backup_file),
                    'traditional_count': len(traditional_chars)
                })

                print(f"  [成功] 已修复并创建备份")
            else:
                print(f"  [成功] 已是简体中文，无需修复")

        except Exception as e:
            print(f"  [失败] 处理失败: {e}")

    # 修复报告
    if fixed_files:
        report_file = transcript_dir / "繁体字修复报告.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(fixed_files, f, ensure_ascii=False, indent=2)

        print(f"\n修复完成！")
        print(f"修复了 {len(fixed_files)} 个文件")
        print(f"修复报告已保存到: {report_file}")
    else:
        print("\n没有需要修复的文件")

def test_conversion():
    """测试转换功能"""
    print("\n" + "="*50)
    print("测试繁简转换功能")
    print("="*50)

    test_texts = [
        "繁體字測試",
        "會務術預寫檔",
        "搶奪罪是對物暴力",
        "本課程配套圖書",
        "盡在瑞達"
    ]

    for text in test_texts:
        print(f"\n原始: {text}")
        simplified = convert_to_simplified_chinese(text)
        print(f"简体: {simplified}")

if __name__ == "__main__":
    print("Link-Text 繁体字修复工具")
    print("=" * 50)

    # 运行测试
    test_conversion()

    # 修复现有文件
    print("\n")
    fix_existing_transcripts()