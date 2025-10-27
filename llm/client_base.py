"""
LLM客户端基类
定义统一的接口规范
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class LLMClientBase(ABC):
    """LLM客户端基类"""
    
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    def translate(self, prompt: str, **kwargs) -> Optional[str]:
        """
        翻译文本
        
        Args:
            prompt: 完整的翻译提示词
            **kwargs: 其他参数
            
        Returns:
            翻译结果，失败返回None
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        测试连接是否正常
        
        Returns:
            连接是否成功
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        return {
            'model': self.model,
            'provider': self.__class__.__name__
        }