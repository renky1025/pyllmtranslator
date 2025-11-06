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
            "通用翻译": """你是专业的翻译专家，请将下方<SOURCE_TEXT>中的{source_lang}内容译为{target_lang}。

严格要求：
1. 只输出译文本身，不要添加任何额外文字、前后缀或标签（例如“Translation:”“译文：”等）。
2. 保持原文的格式和结构（包括换行、缩进、列表、标记、代码块等）。
3. 如果遇到代码、标记语言或内联标记，请保留其结构并仅翻译注释或自然语言部分（若不确定，则完整保留原样）。
4. 不得解释、总结、润色说明，不得加入任何与译文无关的内容。

<SOURCE_TEXT>
{text}
</SOURCE_TEXT>""",
            
            "技术文档翻译": """你是专业的技术文档译者，请将下方<SOURCE_TEXT>中的{source_lang}技术文本译为{target_lang}。

严格要求：
1. 保持Markdown/标记语法、标题、列表、表格、链接、代码块等的结构与格式。
2. 术语统一、准确；变量名、函数名、路径、命令等保持原样；注释与说明自然流畅。
3. 代码仅在注释中翻译自然语言，不改动代码逻辑与标识符。
4. 只输出译文本身，不要任何额外文字、标签或前后缀。

<SOURCE_TEXT>
{text}
</SOURCE_TEXT>""",
            
            "文学翻译": """你是专业的文学译者，请将下方<SOURCE_TEXT>中的{source_lang}内容译为{target_lang}。

严格要求：
1. 保持原文的文体、语气与节奏；忠实传达情感与意象。
2. 保持段落与换行结构，避免随意合并或拆分。
3. 只输出译文本身，不要任何额外文字、标签或前后缀。

<SOURCE_TEXT>
{text}
</SOURCE_TEXT>""",
            
            "商务翻译": """你是专业的商务译者，请将下方<SOURCE_TEXT>中的{source_lang}内容译为{target_lang}。

严格要求：
1. 用词正式、准确、礼貌；符合商务沟通习惯。
2. 保持条款、列表、编号、表格等的结构与层级。
3. 只输出译文本身，不要任何额外文字、标签或前后缀。

<SOURCE_TEXT>
{text}
</SOURCE_TEXT>"""
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
        """格式化Prompt模板，使用安全边界包裹原文，避免特殊字符破坏结构"""
        try:
            # 使用极少出现的包裹标签，降低与原文冲突概率
            # 同时避免在模板中出现格式化歧义
            safe_text = text
            return template.format(
                source_lang=source_lang,
                target_lang=target_lang,
                text=safe_text
            )
        except Exception as e:
            print(f"格式化Prompt失败: {e}")
            return (
                "你是专业的翻译专家。只输出译文，不要任何多余内容。\n\n"
                f"<SOURCE_TEXT>\n{text}\n</SOURCE_TEXT>"
            )