#!/usr/bin/env python3
"""
项目打包脚本 - 使用PyInstaller打包成exe
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller安装成功!")
    except subprocess.CalledProcessError:
        print("PyInstaller安装失败，请手动安装: pip install pyinstaller")
        return False
    return True

def create_spec_file():
    """创建PyInstaller配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'openai',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LLM翻译工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('app.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("已创建PyInstaller配置文件: app.spec")

def build_exe():
    """执行打包"""
    print("开始打包exe文件...")
    
    # 清理之前的构建
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    try:
        # 使用spec文件打包
        subprocess.check_call(['pyinstaller', '--clean', 'app.spec'])
        
        print("\n" + "="*50)
        print("打包完成!")
        print(f"exe文件位置: {os.path.abspath('dist/LLM翻译工具.exe')}")
        print("="*50)
        
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("LLM翻译工具 - exe打包脚本")
    print("="*40)
    
    # 检查是否安装了PyInstaller
    try:
        import PyInstaller
        print("PyInstaller已安装")
    except ImportError:
        if not install_pyinstaller():
            return
    
    # 创建配置文件
    create_spec_file()
    
    # 执行打包
    if build_exe():
        print("\n打包成功! 可以在dist目录找到exe文件")
    else:
        print("\n打包失败，请检查错误信息")

if __name__ == "__main__":
    main()