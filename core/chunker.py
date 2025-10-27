"""
文本分块模块
负责将大文本分割成适合LLM处理的块
"""

import re
from typing import List
import math

class TextChunker:
    """文本分块器"""
    
    def __init__(self):
        # 句子分割的正则表达式
        self.sentence_patterns = [
            r'[.!?]+\s+',  # 英文句子结束
            r'[。！？]+\s*',  # 中文句子结束
            r'[.!?。！？]+\n',  # 换行结束的句子
        ]
        
    def estimate_tokens(self, text: str) -> int:
        """
        估算文本的token数量
        粗略估算：英文约4字符=1token，中文约1.5字符=1token
        
        Args:
            text: 输入文本
            
        Returns:
            估算的token数量
        """
        if not text:
            return 0
            
        # 统计中英文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        other_chars = len(text) - chinese_chars
        
        # 中文字符按1.5字符=1token，其他按4字符=1token估算
        estimated_tokens = math.ceil(chinese_chars / 1.5) + math.ceil(other_chars / 4)
        
        return max(estimated_tokens, 1)
    
    def chunk_text(self, text: str, max_tokens: int = 4000, 
                   prefer_boundary: List[str] = None) -> List[str]:
        """
        将文本分割成块
        
        Args:
            text: 输入文本
            max_tokens: 每块最大token数
            prefer_boundary: 优先边界类型 ["paragraph", "sentence"]
            
        Returns:
            文本块列表
        """
        if not text.strip():
            return []
            
        if prefer_boundary is None:
            prefer_boundary = ["paragraph", "sentence"]
            
        # 如果文本很短，直接返回
        if self.estimate_tokens(text) <= max_tokens:
            return [text]
        
        chunks = []
        
        # 首先按段落分割
        if "paragraph" in prefer_boundary:
            paragraphs = self._split_by_paragraphs(text)
            chunks = self._process_chunks(paragraphs, max_tokens, "sentence" in prefer_boundary)
        else:
            # 直接按句子分割
            chunks = self._process_chunks([text], max_tokens, "sentence" in prefer_boundary)
        
        return [chunk.strip() for chunk in chunks if chunk.strip()]
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """按段落分割文本"""
        # 按双换行分割段落
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """按句子分割文本"""
        sentences = []
        current_text = text
        
        for pattern in self.sentence_patterns:
            parts = re.split(f'({pattern})', current_text)
            if len(parts) > 1:
                sentences = []
                for i in range(0, len(parts) - 1, 2):
                    sentence = parts[i]
                    if i + 1 < len(parts):
                        sentence += parts[i + 1]
                    if sentence.strip():
                        sentences.append(sentence.strip())
                break
        
        # 如果没有找到句子分割符，按长度强制分割
        if not sentences:
            sentences = self._force_split(current_text, 500)  # 按500字符强制分割
            
        return sentences
    
    def _force_split(self, text: str, max_chars: int) -> List[str]:
        """强制按字符数分割"""
        chunks = []
        for i in range(0, len(text), max_chars):
            chunks.append(text[i:i + max_chars])
        return chunks
    
    def _process_chunks(self, initial_chunks: List[str], max_tokens: int, 
                       allow_sentence_split: bool) -> List[str]:
        """处理文本块，确保不超过token限制"""
        final_chunks = []
        
        for chunk in initial_chunks:
            if self.estimate_tokens(chunk) <= max_tokens:
                final_chunks.append(chunk)
            else:
                # 需要进一步分割
                if allow_sentence_split:
                    sentences = self._split_by_sentences(chunk)
                    sub_chunks = self._merge_small_chunks(sentences, max_tokens)
                else:
                    # 强制按字符分割
                    max_chars = max_tokens * 3  # 粗略估算
                    sub_chunks = self._force_split(chunk, max_chars)
                
                final_chunks.extend(sub_chunks)
        
        return final_chunks
    
    def _merge_small_chunks(self, chunks: List[str], max_tokens: int) -> List[str]:
        """合并小的文本块"""
        if not chunks:
            return []
            
        merged_chunks = []
        current_chunk = ""
        
        for chunk in chunks:
            test_chunk = current_chunk + "\n" + chunk if current_chunk else chunk
            
            if self.estimate_tokens(test_chunk) <= max_tokens:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    merged_chunks.append(current_chunk)
                
                # 如果单个chunk太大，需要强制分割
                if self.estimate_tokens(chunk) > max_tokens:
                    max_chars = max_tokens * 3
                    sub_chunks = self._force_split(chunk, max_chars)
                    merged_chunks.extend(sub_chunks[:-1])
                    current_chunk = sub_chunks[-1] if sub_chunks else ""
                else:
                    current_chunk = chunk
        
        if current_chunk:
            merged_chunks.append(current_chunk)
            
        return merged_chunks