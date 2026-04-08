import os
import json
from pathlib import Path

def print_directory_tree(root_dir, indent='', max_depth=4, current_depth=0, 
                        exclude_dirs=None, exclude_extensions=None):
    """
    打印目录树状结构
    
    Args:
        root_dir: 根目录路径
        indent: 缩进字符串
        max_depth: 最大递归深度
        current_depth: 当前深度
        exclude_dirs: 要排除的目录列表
        exclude_extensions: 要排除的文件扩展名列表
    """
    if exclude_dirs is None:
        exclude_dirs = ['.git', '__pycache__', '.pytest_cache', 'venv', '.env']
    if exclude_extensions is None:
        exclude_extensions = ['.pyc', '.pyo']
    
    if current_depth > max_depth:
        return
    
    try:
        items = os.listdir(root_dir)
    except PermissionError:
        print(f"{indent}[权限被拒绝] {os.path.basename(root_dir)}/")
        return
    except FileNotFoundError:
        print(f"{indent}[目录不存在] {root_dir}")
        return
    
    # 分离文件和目录
    dirs = []
    files = []
    for item in items:
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):
            if item not in exclude_dirs:
                dirs.append(item)
        else:
            # 检查文件扩展名
            _, ext = os.path.splitext(item)
            if ext not in exclude_extensions:
                files.append(item)
    
    # 排序
    dirs.sort()
    files.sort()
    
    # 打印当前目录
    if current_depth == 0:
        print(f"📁 {os.path.abspath(root_dir)}")
    else:
        print(f"{indent}📁 {os.path.basename(root_dir)}/")
    
    # 打印文件
    for i, file in enumerate(files):
        is_last = (i == len(files) - 1 and len(dirs) == 0)
        prefix = "└── " if is_last else "├── "
        
        # 获取文件大小
        file_path = os.path.join(root_dir, file)
        try:
            size = os.path.getsize(file_path)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024*1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"
        except:
            size_str = "?"
        
        print(f"{indent}{prefix}{file} ({size_str})")
    
    # 递归打印目录
    for i, dir_name in enumerate(dirs):
        is_last = (i == len(dirs) - 1)
        prefix = "└── " if is_last else "├── "
        
        print(f"{indent}{prefix}📁 {dir_name}/")
        next_indent = indent + ("    " if is_last else "│   ")
        print_directory_tree(
            os.path.join(root_dir, dir_name),
            next_indent,
            max_depth,
            current_depth + 1,
            exclude_dirs,
            exclude_extensions
        )

def get_project_summary():
    """获取项目统计摘要"""
    print("\n" + "="*60)
    print("📊 项目统计摘要")
    print("="*60)
    
    # 统计文件类型
    file_types = {}
    total_size = 0
    total_files = 0
    total_dirs = 0
    
    for root, dirs, files in os.walk('.'):
        # 过滤排除的目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'venv']]
        
        total_dirs += len(dirs)
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                continue
                
            total_files += 1
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                total_size += size
            except:
                pass
            
            # 统计文件类型
            _, ext = os.path.splitext(file)
            ext = ext.lower() if ext else '[无扩展名]'
            file_types[ext] = file_types.get(ext, 0) + 1
    
    # 打印统计信息
    print(f"📁 总目录数: {total_dirs}")
    print(f"📄 总文件数: {total_files}")
    print(f"💾 总大小: {total_size/(1024*1024):.2f} MB")
    print("\n文件类型分布:")
    for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_files) * 100
        print(f"  {ext}: {count} 个 ({percentage:.1f}%)")

def check_critical_files():
    """检查关键文件是否存在"""
    print("\n" + "="*60)
    print("🔍 关键文件检查")
    print("="*60)
    
    critical_files = {
        'main.py': 'FastAPI主应用',
        'llm_client.py': 'LLM客户端',
        'grader.py': '代码评分器',
        'evaluation/evaluator.py': '评估器',
        'dataset/dataset_index.json': '数据集索引',
        '.env': '环境变量（重要！）'
    }
    
    all_exist = True
    for file, description in critical_files.items():
        if os.path.exists(file):
            status = "✅"
        else:
            status = "❌"
            all_exist = False
        print(f"{status} {file:30} - {description}")
    
    if all_exist:
        print("\n🎉 所有关键文件都存在！")
    else:
        print("\n⚠️  缺少一些关键文件，请检查。")

if __name__ == "__main__":
    # 设置工作目录为项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🌳 项目目录结构")
    print("="*60)
    print_directory_tree('.', max_depth=3)
    
    # 获取项目统计
    get_project_summary()
    
    # 检查关键文件
    check_critical_files()
    
    # 显示当前环境信息
    print("\n" + "="*60)
    print("💻 环境信息")
    print("="*60)
    import platform
    import sys
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")