import os
import re
import requests
import hashlib
from urllib.parse import urlparse

patternstr = r'!\[([^\]]*)\]\(([^)]+)\)'
judge_list = ('https://', 'http://') 

def download_image(url, save_dir):
    """
    下载图片并返回保存路径
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # 使用URL的MD5作为文件名,保留原始扩展名
            url_hash = hashlib.md5(url.encode()).hexdigest()
            ext = os.path.splitext(urlparse(url).path)[1]
            if not ext:
                ext = '.jpg'  # 默认扩展名
            
            filename = f"{url_hash}{ext}"
            save_path = os.path.join(save_dir, filename)
            
            # 确保图片目录存在
            os.makedirs(save_dir, exist_ok=True)
            
            # 保存图片
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return save_path
    except Exception as e:
        print(f"下载图片失败: {url}")
        print(f"错误信息: {str(e)}")
        return None

def process_markdown_file(file_path, file):
    """
    处理单个Markdown文件
    """
    # 创建与markdown文件同名的目录用于存储图片
    dirname, _ = os.path.splitext(file)
    images_dir = os.path.join(os.path.dirname(file_path), dirname)
    
    try:
        os.makedirs(images_dir)
        print(f'{dirname}目录创建成功')
    except FileExistsError:
        print(f'{dirname}目录已存在')
    except OSError as error:
        print(f'{dirname}目录创建失败: {error}')
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    def replace_link(match):
        alt_text = match.group(1)
        url = match.group(2)
        
        if not url.startswith(judge_list):
            return match.group(0)
            
        # 下载图片到指定目录
        local_path = download_image(url, images_dir)
        if local_path:
            # 转换为相对路径
            rel_path = os.path.relpath(local_path, os.path.dirname(file_path))
            rel_path = rel_path.replace('\\', '/')  # 统一使用正斜杠
            return f'![{alt_text}]({rel_path})'
        
        return match.group(0)

    new_content = re.sub(patternstr, replace_link, content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"已处理文件: {file_path}")

def process_directory(directory):
    """
    处理目录下的所有markdown文件
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.md', '.markdown')):
                file_path = os.path.join(root, file)
                process_markdown_file(file_path, file)

if __name__ == '__main__':
    current_dir = os.getcwd()
    print(f"开始处理目录: {current_dir}")
    process_directory(current_dir)
    print("处理完成!")