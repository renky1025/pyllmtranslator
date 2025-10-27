"""
翻译管理模块
负责协调整个翻译流程
"""

from pathlib import Path
from typing import Dict, List, Optional, Callable
import time
import logging

from .file_manager import FileManager
from .chunker import TextChunker
from .prompt_manager import PromptManager
from llm.openai_client import OpenAIClient
from llm.ollama_client import OllamaClient

class TranslationManager:
    """翻译管理器"""
    
    def __init__(self):
        self.file_manager = FileManager()
        self.chunker = TextChunker()
        self.prompt_manager = PromptManager()
        self.llm_client = None
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def translate_file(self, file_path: Path, config: Dict) -> bool:
        """
        翻译单个文件
        
        Args:
            file_path: 文件路径
            config: 翻译配置
            
        Returns:
            翻译是否成功
        """
        try:
            # 初始化LLM客户端
            if not self.llm_client:
                self.llm_client = self._create_llm_client(config)
            
            # 读取文件
            self.logger.info(f"读取文件: {file_path}")
            content = self.file_manager.read_file(file_path)
            
            if not content.strip():
                self.logger.warning(f"文件为空: {file_path}")
                return False
            
            # 分块处理
            self.logger.info(f"分块处理文本，最大token: {config['max_tokens']}")
            chunks = self.chunker.chunk_text(
                content, 
                max_tokens=config['max_tokens']
            )
            
            self.logger.info(f"文本分为 {len(chunks)} 块")
            
            # 翻译每个块
            translated_chunks = []
            for i, chunk in enumerate(chunks):
                self.logger.info(f"翻译第 {i+1}/{len(chunks)} 块")
                
                # 格式化prompt
                formatted_prompt = self.prompt_manager.format_prompt(
                    config['prompt'],
                    config['source_lang'],
                    config['target_lang'],
                    chunk
                )
                
                # 调用LLM翻译
                translated_chunk = self.llm_client.translate(formatted_prompt)
                
                if translated_chunk:
                    translated_chunks.append(translated_chunk)
                    # 添加延迟避免API限制
                    time.sleep(0.5)
                else:
                    self.logger.error(f"翻译失败: 第 {i+1} 块")
                    return False
            
            # 合并翻译结果
            translated_content = self._merge_chunks(translated_chunks)
            
            # 写入输出文件
            output_path = Path(config.get('output_path', file_path.parent))
            output_file = self.file_manager.write_file(
                output_path,
                file_path,
                translated_content,
                config.get('preserve_structure', True)
            )
            
            self.logger.info(f"翻译完成，输出文件: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"翻译文件失败 {file_path}: {str(e)}")
            return False
    
    def translate_files(self, files: List[Path], config: Dict, 
                       progress_callback: Optional[Callable] = None) -> Dict[Path, bool]:
        """
        批量翻译文件
        
        Args:
            files: 文件路径列表
            config: 翻译配置
            progress_callback: 进度回调函数
            
        Returns:
            翻译结果字典 {文件路径: 是否成功}
        """
        results = {}
        total_files = len(files)
        
        for i, file_path in enumerate(files):
            self.logger.info(f"处理文件 {i+1}/{total_files}: {file_path}")
            
            success = self.translate_file(file_path, config)
            results[file_path] = success
            
            # 调用进度回调
            if progress_callback:
                progress_callback(i + 1, total_files, file_path, success)
        
        return results
    
    def _create_llm_client(self, config: Dict):
        """
        根据配置创建LLM客户端
        
        Args:
            config: 翻译配置
            
        Returns:
            LLM客户端实例
        """
        provider = config.get('provider', 'openai').lower()
        
        if provider == 'ollama':
            self.logger.info("使用Ollama本地模型")
            return OllamaClient(
                model=config.get('ollama_model', config.get('model', 'llama3.2')),
                base_url=config.get('ollama_base_url', 'http://localhost:11434'),
                temperature=config.get('temperature', 0.1),
                timeout=config.get('ollama_timeout', config.get('timeout', 120)),
                max_retries=config.get('max_retries', 3)
            )
        elif provider == 'openai':
            self.logger.info("使用OpenAI API")
            return OpenAIClient(
                api_key=config['api_key'],
                model=config.get('model', 'gpt-4o-mini'),
                temperature=config.get('temperature', 0.1),
                max_tokens=config.get('max_tokens', 2000),
                timeout=config.get('timeout', 60),
                max_retries=config.get('max_retries', 3)
            )
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")
    
    def _merge_chunks(self, chunks: List[str]) -> str:
        """
        合并翻译后的文本块
        
        Args:
            chunks: 翻译后的文本块列表
            
        Returns:
            合并后的文本
        """
        if not chunks:
            return ""
        
        # 简单的合并策略：用双换行连接
        # 可以根据需要改进合并逻辑
        merged = ""
        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if chunk:
                if i > 0:
                    # 检查是否需要添加分隔符
                    if not merged.endswith('\n\n') and not chunk.startswith('\n'):
                        merged += '\n\n'
                merged += chunk
        
        return merged
    
    def cancel_current_request(self):
        """取消当前的翻译请求"""
        if self.llm_client and hasattr(self.llm_client, 'cancel_request'):
            self.llm_client.cancel_request()
            self.logger.info("已取消当前翻译请求")
    
    def estimate_cost(self, files: List[Path], config: Dict) -> Dict:
        """
        估算翻译成本
        
        Args:
            files: 文件列表
            config: 翻译配置
            
        Returns:
            成本估算信息
        """
        total_chars = 0
        total_tokens = 0
        
        for file_path in files:
            try:
                content = self.file_manager.read_file(file_path)
                chars = len(content)
                tokens = self.chunker.estimate_tokens(content)
                
                total_chars += chars
                total_tokens += tokens
                
            except Exception as e:
                self.logger.warning(f"无法读取文件 {file_path}: {e}")
        
        # 粗略的成本估算（需要根据实际API定价调整）
        estimated_cost = total_tokens * 0.0001  # 假设每1000 tokens $0.1
        
        return {
            'total_files': len(files),
            'total_characters': total_chars,
            'total_tokens': total_tokens,
            'estimated_cost_usd': estimated_cost,
            'estimated_time_minutes': len(files) * 2  # 假设每文件2分钟
        }