#!/usr/bin/env python3
"""
批量/单文件翻译工具 - 程序入口
基于 Python + PyQt + LLM
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QDir

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.main_window import MainWindow

def main():
    """程序主入口"""
    app = QApplication(sys.argv)
    app.setApplicationName("LLM翻译工具")
    app.setApplicationVersion("1.0.0")
    
    # 设置应用图标和样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())