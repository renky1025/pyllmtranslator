"""
主窗口界面
"""

from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, 
                             QWidget, QComboBox, QLabel, QPushButton, QFileDialog,
                             QTableWidget, QTableWidgetItem, QTextEdit, QSpinBox,
                             QCheckBox, QProgressBar, QSplitter, QGroupBox,
                             QLineEdit, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path
import json
import sys
import os

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.translator import TranslationManager
from core.file_manager import FileManager
from core.prompt_manager import PromptManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.translation_manager = TranslationManager()
        self.file_manager = FileManager()
        self.prompt_manager = PromptManager()
        
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("LLM批量翻译工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件和选项卡
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 创建各个选项卡
        self.create_language_tab()
        self.create_files_tab()
        self.create_settings_tab()
        self.create_run_tab()
        
    def create_language_tab(self):
        """创建语言设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 语言选择组
        lang_group = QGroupBox("语言设置")
        lang_layout = QVBoxLayout(lang_group)
        
        # 源语言
        src_layout = QHBoxLayout()
        src_layout.addWidget(QLabel("源语言:"))
        self.src_lang_combo = QComboBox()
        self.src_lang_combo.addItems(["中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文"])
        src_layout.addWidget(self.src_lang_combo)
        src_layout.addStretch()
        lang_layout.addLayout(src_layout)
        
        # 目标语言
        tgt_layout = QHBoxLayout()
        tgt_layout.addWidget(QLabel("目标语言:"))
        self.tgt_lang_combo = QComboBox()
        self.tgt_lang_combo.addItems(["英文", "中文", "日文", "韩文", "法文", "德文", "西班牙文"])
        tgt_layout.addWidget(self.tgt_lang_combo)
        tgt_layout.addStretch()
        lang_layout.addLayout(tgt_layout)
        
        # 自动检测
        self.auto_detect_cb = QCheckBox("自动检测源语言")
        lang_layout.addWidget(self.auto_detect_cb)
        
        layout.addWidget(lang_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "语言设置")
        
    def create_files_tab(self):
        """创建文件选择选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 文件选择按钮
        btn_layout = QHBoxLayout()
        self.select_file_btn = QPushButton("选择单个文件")
        self.select_folder_btn = QPushButton("选择文件夹")
        self.clear_files_btn = QPushButton("清空列表")
        
        self.select_file_btn.clicked.connect(self.select_file)
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.clear_files_btn.clicked.connect(self.clear_files)
        
        btn_layout.addWidget(self.select_file_btn)
        btn_layout.addWidget(self.select_folder_btn)
        btn_layout.addWidget(self.clear_files_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # 递归选项
        self.recursive_cb = QCheckBox("递归搜索子文件夹")
        self.recursive_cb.setChecked(True)
        layout.addWidget(self.recursive_cb)
        
        # 文件列表
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(4)
        self.files_table.setHorizontalHeaderLabels(["文件名", "大小", "状态", "路径"])
        
        # 设置表格列宽
        header = self.files_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 文件名
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 大小
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 状态
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # 路径
        
        layout.addWidget(self.files_table)
        
        self.tab_widget.addTab(tab, "文件选择")
        
    def create_settings_tab(self):
        """创建翻译设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 输出设置
        output_group = QGroupBox("输出设置")
        output_layout = QVBoxLayout(output_group)
        
        output_path_layout = QHBoxLayout()
        output_path_layout.addWidget(QLabel("输出路径:"))
        self.output_path_edit = QLineEdit()
        self.output_path_btn = QPushButton("浏览")
        self.output_path_btn.clicked.connect(self.select_output_path)
        output_path_layout.addWidget(self.output_path_edit)
        output_path_layout.addWidget(self.output_path_btn)
        output_layout.addLayout(output_path_layout)
        
        self.preserve_structure_cb = QCheckBox("保留原目录结构")
        self.preserve_structure_cb.setChecked(True)
        output_layout.addWidget(self.preserve_structure_cb)
        
        layout.addWidget(output_group)
        
        # 分块设置
        chunk_group = QGroupBox("分块设置")
        chunk_layout = QVBoxLayout(chunk_group)
        
        chunk_layout1 = QHBoxLayout()
        chunk_layout1.addWidget(QLabel("最大Token数:"))
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 4000)
        self.max_tokens_spin.setValue(1000)
        chunk_layout1.addWidget(self.max_tokens_spin)
        chunk_layout1.addStretch()
        chunk_layout.addLayout(chunk_layout1)
        
        chunk_layout2 = QHBoxLayout()
        chunk_layout2.addWidget(QLabel("最大字符数:"))
        self.max_chars_spin = QSpinBox()
        self.max_chars_spin.setRange(500, 10000)
        self.max_chars_spin.setValue(2000)
        chunk_layout2.addWidget(self.max_chars_spin)
        chunk_layout2.addStretch()
        chunk_layout.addLayout(chunk_layout2)
        
        layout.addWidget(chunk_group)
        
        # LLM设置
        llm_group = QGroupBox("LLM设置")
        llm_layout = QVBoxLayout(llm_group)
        
        # 提供商选择
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("提供商:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Ollama"])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_combo)
        provider_layout.addStretch()
        llm_layout.addLayout(provider_layout)
        
        # 模型选择
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("模型:"))
        self.model_combo = QComboBox()
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        llm_layout.addLayout(model_layout)
        
        # OpenAI设置
        self.openai_group = QGroupBox("OpenAI设置")
        openai_layout = QVBoxLayout(self.openai_group)
        
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("API Key:"))
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        api_key_layout.addWidget(self.api_key_edit)
        openai_layout.addLayout(api_key_layout)
        
        llm_layout.addWidget(self.openai_group)
        
        # Ollama设置
        self.ollama_group = QGroupBox("Ollama设置")
        ollama_layout = QVBoxLayout(self.ollama_group)
        
        base_url_layout = QHBoxLayout()
        base_url_layout.addWidget(QLabel("服务地址:"))
        self.ollama_url_edit = QLineEdit()
        self.ollama_url_edit.setText("http://localhost:11434")
        base_url_layout.addWidget(self.ollama_url_edit)
        ollama_layout.addLayout(base_url_layout)
        
        # 测试连接按钮
        test_layout = QHBoxLayout()
        self.test_ollama_btn = QPushButton("测试连接")
        self.test_ollama_btn.clicked.connect(self.test_ollama_connection)
        self.refresh_models_btn = QPushButton("刷新模型")
        self.refresh_models_btn.clicked.connect(self.refresh_ollama_models)
        test_layout.addWidget(self.test_ollama_btn)
        test_layout.addWidget(self.refresh_models_btn)
        test_layout.addStretch()
        ollama_layout.addLayout(test_layout)
        
        llm_layout.addWidget(self.ollama_group)
        
        # 初始化提供商设置
        self.on_provider_changed("OpenAI")
        
        layout.addWidget(llm_group)
        
        # Prompt设置
        prompt_group = QGroupBox("Prompt设置")
        prompt_layout = QVBoxLayout(prompt_group)
        
        prompt_select_layout = QHBoxLayout()
        prompt_select_layout.addWidget(QLabel("模板:"))
        self.prompt_combo = QComboBox()
        prompt_select_layout.addWidget(self.prompt_combo)
        prompt_select_layout.addStretch()
        prompt_layout.addLayout(prompt_select_layout)
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setMaximumHeight(150)
        prompt_layout.addWidget(self.prompt_edit)
        
        # Load prompt templates after creating the widgets
        self.load_prompt_templates()
        
        layout.addWidget(prompt_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "翻译设置")
        
    def create_run_tab(self):
        """创建运行和日志选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始翻译")
        self.stop_btn = QPushButton("停止")
        
        self.start_btn.clicked.connect(self.start_translation)
        self.stop_btn.clicked.connect(self.stop_translation)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # 进度条
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("总进度:"))
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        layout.addLayout(progress_layout)
        
        # 日志输出
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(tab, "运行日志")
        
    def select_file(self):
        """选择单个文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", 
            "文本文件 (*.txt *.md);;所有文件 (*.*)"
        )
        if file_path:
            self.add_file_to_table(Path(file_path))
            
    def select_folder(self):
        """选择文件夹"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            files = self.file_manager.list_files(
                Path(folder_path), 
                recursive=self.recursive_cb.isChecked()
            )
            for file_path in files:
                self.add_file_to_table(file_path)
                
    def add_file_to_table(self, file_path: Path):
        """添加文件到表格"""
        row = self.files_table.rowCount()
        self.files_table.insertRow(row)
        
        self.files_table.setItem(row, 0, QTableWidgetItem(file_path.name))
        self.files_table.setItem(row, 1, QTableWidgetItem(f"{file_path.stat().st_size} bytes"))
        self.files_table.setItem(row, 2, QTableWidgetItem("待翻译"))
        self.files_table.setItem(row, 3, QTableWidgetItem(str(file_path)))
        
    def clear_files(self):
        """清空文件列表"""
        self.files_table.setRowCount(0)
        
    def select_output_path(self):
        """选择输出路径"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if folder_path:
            self.output_path_edit.setText(folder_path)
            
    def load_prompt_templates(self):
        """加载Prompt模板"""
        templates = self.prompt_manager.get_templates()
        self.prompt_combo.clear()
        for name in templates.keys():
            self.prompt_combo.addItem(name)
        
        # 连接选择事件
        self.prompt_combo.currentTextChanged.connect(self.on_prompt_template_changed)
        
        # 加载默认模板
        if templates:
            first_template = list(templates.keys())[0]
            self.prompt_edit.setText(templates[first_template])
            
    def on_prompt_template_changed(self, template_name):
        """Prompt模板改变时的处理"""
        templates = self.prompt_manager.get_templates()
        if template_name in templates:
            self.prompt_edit.setText(templates[template_name])
    
    def on_provider_changed(self, provider):
        """提供商改变时的处理"""
        if provider == "OpenAI":
            self.openai_group.setVisible(True)
            self.ollama_group.setVisible(False)
            # 设置OpenAI模型
            self.model_combo.clear()
            self.model_combo.addItems(["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4"])
        elif provider == "Ollama":
            self.openai_group.setVisible(False)
            self.ollama_group.setVisible(True)
            # 设置默认Ollama模型
            self.model_combo.clear()
            self.model_combo.addItems(["llama3.2", "llama3.1", "qwen2.5", "gemma2"])
            # 尝试刷新可用模型
            self.refresh_ollama_models()
    
    def test_ollama_connection(self):
        """测试Ollama连接"""
        try:
            from llm.ollama_client import OllamaClient
            
            base_url = self.ollama_url_edit.text().strip()
            if not base_url:
                base_url = "http://localhost:11434"
            
            client = OllamaClient(base_url=base_url)
            
            if client.test_connection():
                QMessageBox.information(self, "连接测试", "Ollama连接成功！")
                self.add_log_message("Ollama连接测试成功")
                # 自动刷新模型列表
                self.refresh_ollama_models()
            else:
                QMessageBox.warning(self, "连接测试", "Ollama连接失败，请检查服务是否运行")
                self.add_log_message("Ollama连接测试失败")
                
        except Exception as e:
            QMessageBox.critical(self, "连接测试", f"连接测试出错: {str(e)}")
            self.add_log_message(f"Ollama连接测试出错: {str(e)}")
    
    def refresh_ollama_models(self):
        """刷新Ollama模型列表"""
        try:
            from llm.ollama_client import OllamaClient
            
            base_url = self.ollama_url_edit.text().strip()
            if not base_url:
                base_url = "http://localhost:11434"
            
            client = OllamaClient(base_url=base_url)
            models = client.get_available_models()
            
            if models:
                current_model = self.model_combo.currentText()
                self.model_combo.clear()
                self.model_combo.addItems(models)
                
                # 尝试恢复之前选择的模型
                if current_model in models:
                    self.model_combo.setCurrentText(current_model)
                
                self.add_log_message(f"已刷新Ollama模型列表，找到 {len(models)} 个模型")
            else:
                self.add_log_message("未找到可用的Ollama模型")
                
        except Exception as e:
            self.add_log_message(f"刷新Ollama模型列表失败: {str(e)}")
            
    def start_translation(self):
        """开始翻译"""
        # 获取文件列表
        files = []
        for row in range(self.files_table.rowCount()):
            file_path = self.files_table.item(row, 3).text()
            files.append(Path(file_path))
            
        if not files:
            QMessageBox.warning(self, "警告", "请先选择要翻译的文件")
            return
            
        # 检查必要的配置
        provider = self.provider_combo.currentText().lower()
        if provider == "openai" and not self.api_key_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入OpenAI API Key")
            return
        elif provider == "ollama":
            # 对于Ollama，检查连接和模型
            if not self.model_combo.currentText():
                QMessageBox.warning(self, "警告", "请选择Ollama模型")
                return
            
        # 配置翻译参数
        config = {
            'provider': provider,
            'source_lang': self.src_lang_combo.currentText(),
            'target_lang': self.tgt_lang_combo.currentText(),
            'model': self.model_combo.currentText(),
            'max_tokens': self.max_tokens_spin.value(),
            'max_chars': self.max_chars_spin.value(),
            'prompt': self.prompt_edit.toPlainText(),
            'output_path': self.output_path_edit.text(),
            'preserve_structure': self.preserve_structure_cb.isChecked(),
            'temperature': 0.1,
            'timeout': 120 if provider == "ollama" else 60,
            'max_retries': 3
        }
        
        # 添加提供商特定的配置
        if provider == "openai":
            config['api_key'] = self.api_key_edit.text()
        elif provider == "ollama":
            config['ollama_base_url'] = self.ollama_url_edit.text().strip() or "http://localhost:11434"
            config['ollama_model'] = self.model_combo.currentText()
            config['ollama_timeout'] = 120
        
        # 启动翻译线程
        self.translation_thread = TranslationThread(files, config, self.translation_manager)
        self.translation_thread.progress_updated.connect(self.update_progress)
        self.translation_thread.file_completed.connect(self.update_file_status)
        self.translation_thread.log_message.connect(self.add_log_message)
        self.translation_thread.finished.connect(self.translation_finished)
        
        self.translation_thread.start()
        
        # 更新按钮状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        

        
    def stop_translation(self):
        """停止翻译"""
        if hasattr(self, 'translation_thread'):
            self.translation_thread.stop()
            
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def update_file_status(self, file_path, status):
        """更新文件状态"""
        for row in range(self.files_table.rowCount()):
            if self.files_table.item(row, 3).text() == str(file_path):
                self.files_table.setItem(row, 2, QTableWidgetItem(status))
                break
                
    def add_log_message(self, message):
        """添加日志消息"""
        self.log_text.append(message)
        
    def translation_finished(self):
        """翻译完成"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.add_log_message("翻译任务完成!")
        
    def load_config(self):
        """加载配置"""
        # TODO: 从配置文件加载设置
        pass
        
    def save_config(self):
        """保存配置"""
        # TODO: 保存设置到配置文件
        pass


class TranslationThread(QThread):
    """翻译线程"""
    progress_updated = pyqtSignal(int)
    file_completed = pyqtSignal(Path, str)
    log_message = pyqtSignal(str)
    
    def __init__(self, files, config, translation_manager):
        super().__init__()
        self.files = files
        self.config = config
        self.translation_manager = translation_manager
        self.should_stop = False
        
    def run(self):
        """运行翻译任务"""
        total_files = len(self.files)
        
        for i, file_path in enumerate(self.files):
            # 检查是否需要停止
            if self.should_stop:
                self.log_message.emit("翻译已停止")
                break
                
            try:
                self.log_message.emit(f"开始翻译: {file_path.name}")
                self.file_completed.emit(file_path, "翻译中")
                
                # 执行翻译
                success = self.translation_manager.translate_file(file_path, self.config)
                
                if self.should_stop:
                    self.file_completed.emit(file_path, "已停止")
                    break
                    
                if success:
                    self.file_completed.emit(file_path, "完成")
                    self.log_message.emit(f"翻译完成: {file_path.name}")
                else:
                    self.file_completed.emit(file_path, "失败")
                    self.log_message.emit(f"翻译失败: {file_path.name}")
                    
            except Exception as e:
                if self.should_stop:
                    self.file_completed.emit(file_path, "已停止")
                    break
                else:
                    self.file_completed.emit(file_path, "错误")
                    self.log_message.emit(f"翻译错误: {file_path.name} - {str(e)}")
                
            # 更新进度
            progress = int((i + 1) / total_files * 100)
            self.progress_updated.emit(progress)
        
    def stop(self):
        """停止翻译"""
        self.should_stop = True
        
        # 通知翻译管理器停止当前请求
        if hasattr(self.translation_manager, 'cancel_current_request'):
            self.translation_manager.cancel_current_request()
        
        # 如果线程正在运行，等待其结束
        if self.isRunning():
            self.wait(5000)  # 等待最多5秒