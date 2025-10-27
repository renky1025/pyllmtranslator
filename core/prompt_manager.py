"""
Prompt管理模块
负责管理翻译提示词模板
"""

import json
from pathlib import Path
from typing import Dict, Optional

class PromptManager:
    """Prompt管理器"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path.home() / '.llm_translator'
        
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        self.prompts_file = self.config_dir / 'prompts.json'
        
        # 初始化默认模板
        self._init_default_templates()
    
    def _init_default_templates(self):
        """初始化默认Prompt模板"""
        default_templates = {
            "通用翻译": """你是一个专业的翻译专家。请将以下{source_lang}文本翻译成{target_lang}。

要求：
1. 保持原文的格式和结构
2. 保留代码块、标记语言标签等特殊格式
3. 翻译要准确、流畅、符合目标语言习惯
4. 不要添加任何解释或注释

原文：
{text}

翻译：""",
            
            "技术文档翻译": """你是一个专业的技术文档翻译专家。请将以下{source_lang}技术文档翻译成{target_lang}。

要求：
1. 保持所有Markdown格式、代码块、链接等
2. 技术术语要准确，保持一致性
3. 代码注释也需要翻译
4. 保持专业性和准确性

原文：
{text}

翻译：""",
            
            "文学翻译": """你是一个专业的文学翻译家。请将以下{source_lang}文本翻译成{target_lang}。

要求：
1. 保持原文的文学风格和语调
2. 注重语言的优美和流畅
3. 保持情感表达的准确性
4. 适当考虑文化背景差异

原文：
{text}

翻译：""",
            
            "商务翻译": """你是一个专业的商务翻译专家。请将以下{source_lang}商务文本翻译成{target_lang}。

要求：
1. 使用正式、专业的商务语言
2. 保持礼貌和尊重的语调
3. 确保术语的准确性
4. 符合商务沟通习惯

原文：
{text}

翻译："""
        }
        
        # 如果配置文件不存在，创建默认配置
        if not self.prompts_file.exists():
            self.save_templates(default_templates)
    
    def get_templates(self) -> Dict[str, str]:
        """获取所有Prompt模板"""
        try:
            if self.prompts_file.exists():
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"加载Prompt模板失败: {e}")
            return {}
    
    def save_templates(self, templates: Dict[str, str]):
        """保存Prompt模板"""
        try:
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存Prompt模板失败: {e}")
    
    def add_template(self, name: str, template: str):
        """添加新的Prompt模板"""
        templates = self.get_templates()
        templates[name] = template
        self.save_templates(templates)
    
    def delete_template(self, name: str):
        """删除Prompt模板"""
        templates = self.get_templates()
        if name in templates:
            del templates[name]
            self.save_templates(templates)
    
    def get_template(self, name: str) -> Optional[str]:
        """获取指定的Prompt模板"""
        templates = self.get_templates()
        return templates.get(name)
    
    def format_prompt(self, template: str, source_lang: str, 
                     target_lang: str, text: str) -> str:
        """格式化Prompt模板"""
        try:
            return template.format(
                source_lang=source_lang,
                target_lang=target_lang,
                text=text
            )
        except Exception as e:
            print(f"格式化Prompt失败: {e}")
            return f"请将以下{source_lang}文本翻译成{target_lang}：\n\n{text}"