"""
文件管理模块
负责文件的读取、写入和路径管理
"""

from pathlib import Path
from typing import List, Optional
import os
import shutil

class FileManager:
    """文件管理器"""
    
    SUPPORTED_EXTENSIONS = {'.txt', '.md', '.rst', '.py', '.js', '.html', '.xml', '.json'}
    
    def __init__(self):
        pass
    
    def list_files(self, path: Path, recursive: bool = True) -> List[Path]:
        """
        列出指定路径下的文件
        
        Args:
            path: 文件或文件夹路径
            recursive: 是否递归搜索子文件夹
            
        Returns:
            文件路径列表
        """
        files = []
        
        if path.is_file():
            if self._is_supported_file(path):
                files.append(path)
        elif path.is_dir():
            if recursive:
                for file_path in path.rglob('*'):
                    if file_path.is_file() and self._is_supported_file(file_path):
                        files.append(file_path)
            else:
                for file_path in path.iterdir():
                    if file_path.is_file() and self._is_supported_file(file_path):
                        files.append(file_path)
        
        return sorted(files)
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """检查文件是否支持"""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def read_file(self, file_path: Path) -> str:
        """
        读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容字符串
        """
        try:
            # 尝试不同的编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            
            # 如果所有编码都失败，使用二进制模式读取并尝试解码
            with open(file_path, 'rb') as f:
                content = f.read()
                return content.decode('utf-8', errors='ignore')
                
        except Exception as e:
            raise Exception(f"读取文件失败 {file_path}: {str(e)}")
    
    def write_file(self, output_root: Path, original_path: Path, content: str, 
                   preserve_structure: bool = True) -> Path:
        """
        写入翻译后的文件
        
        Args:
            output_root: 输出根目录
            original_path: 原始文件路径
            content: 翻译后的内容
            preserve_structure: 是否保留目录结构
            
        Returns:
            输出文件路径
        """
        try:
            # 确保输出目录存在
            output_root.mkdir(parents=True, exist_ok=True)
            
            # 生成输出文件名，添加翻译后缀
            stem = original_path.stem
            suffix = original_path.suffix
            output_filename = f"{stem}_translated{suffix}"
            
            # 直接保存到指定文件夹，不创建额外的目录结构
            output_path = output_root / output_filename
            
            # 如果文件已存在，添加数字后缀
            counter = 1
            while output_path.exists():
                output_filename = f"{stem}_translated_{counter}{suffix}"
                output_path = output_root / output_filename
                counter += 1
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"写入文件失败 {output_path}: {str(e)}")
    
    def get_file_info(self, file_path: Path) -> dict:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        try:
            stat = file_path.stat()
            return {
                'name': file_path.name,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'extension': file_path.suffix,
                'path': str(file_path)
            }
        except Exception as e:
            return {
                'name': file_path.name,
                'size': 0,
                'modified': 0,
                'extension': file_path.suffix,
                'path': str(file_path),
                'error': str(e)
            }