# import ebooklib
# from ebooklib import epub
# import os

# book = epub.read_epub('Adventures_of_Huckleberry_Finn_pg76-images-3.epub')
# for i, item in enumerate(book.get_items()):
#     if item.get_type() == ebooklib.ITEM_DOCUMENT:
#         with open(f'chapter_{i+1:02d}.md', 'w') as f:
#             f.write(item.get_content().decode('utf-8'))
import re
from pathlib import Path

def roman_to_int(roman):
    """将罗马数字转换为整数（用于排序）"""
    roman_numerals = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }
    total = 0
    prev_value = 0
    for char in reversed(roman):
        value = roman_numerals[char]
        if value < prev_value:
            total -= value
        else:
            total += value
        prev_value = value
    return total

def split_txt_to_md(input_file, output_dir):
    # 创建输出目录
    Path(output_dir).mkdir(exist_ok=True)
    
    # 读取文本文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式分割章节
    # 匹配 "CHAPTER [罗马数字或THE LAST]." 格式
    chapters = re.split(r'(CHAPTER [IVXLCDM]+\.|CHAPTER THE LAST\.)', content)
    
    # 第一个元素是章节之前的内容（可能是前言），跳过
    chapters = chapters[1:]
    
    # 成对处理章节标题和内容
    for i in range(0, len(chapters), 2):
        chapter_title = chapters[i].strip()
        chapter_content = chapters[i+1].strip() if i+1 < len(chapters) else ""
        
        # 确定文件名
        if "THE LAST" in chapter_title:
            chapter_num = "last"
            file_name = f"chapter_{chapter_num}.md"
        else:
            # 提取罗马数字部分
            roman_num = re.search(r'CHAPTER ([IVXLCDM]+)\.', chapter_title).group(1)
            chapter_num = roman_to_int(roman_num)
            file_name = f"chapter_{chapter_num}.md"
        
        # 写入Markdown文件
        output_path = Path(output_dir) / file_name
        with open(output_path, 'w', encoding='utf-8') as f:
            # 添加Markdown标题（# 一级标题）
            f.write(f"# chapter {i//2 + 1}\n\n")
            f.write(chapter_content)
    
    print(f"成功分割为 {len(chapters)//2} 个章节文件到 {output_dir} 目录")

# 使用示例
input_txt = "book.txt"  # 替换为你的TXT文件路径
output_directory = "./"    # 输出目录

split_txt_to_md(input_txt, output_directory)