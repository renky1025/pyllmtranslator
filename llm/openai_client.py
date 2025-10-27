"""
OpenAI API客户端
"""

import openai
import time
import logging
from typing import Optional, Dict, Any
from .client_base import LLMClientBase

class OpenAIClient(LLMClientBase):
    """OpenAI API客户端"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", **kwargs):
        super().__init__(api_key, model, **kwargs)
        
        # 设置OpenAI API密钥
        openai.api_key = self.api_key
        
        # 配置参数
        self.temperature = kwargs.get('temperature', 0.1)
        self.max_tokens = kwargs.get('max_tokens', 2000)
        self.timeout = kwargs.get('timeout', 60)
        self.max_retries = kwargs.get('max_retries', 3)
        
        # 用于取消请求的标志
        self.should_cancel = False
        
        self.logger = logging.getLogger(__name__)
    
    def translate(self, prompt: str, **kwargs) -> Optional[str]:
        """
        使用OpenAI API翻译文本
        
        Args:
            prompt: 完整的翻译提示词
            **kwargs: 其他参数
            
        Returns:
            翻译结果
        """
        # 重置取消标志
        self.should_cancel = False
        
        for attempt in range(self.max_retries):
            # 检查是否需要取消
            if self.should_cancel:
                self.logger.info("OpenAI请求已被取消")
                return None
                
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    timeout=self.timeout
                )
                
                if response.choices and response.choices[0].message:
                    return response.choices[0].message.content.strip()
                else:
                    self.logger.warning("OpenAI API返回空响应")
                    return None
                    
            except openai.error.RateLimitError as e:
                self.logger.warning(f"API速率限制，等待重试... (尝试 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    self.logger.error(f"API速率限制，重试失败: {e}")
                    return None
                    
            except openai.error.APIError as e:
                self.logger.error(f"OpenAI API错误: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                else:
                    return None
                    
            except openai.error.AuthenticationError as e:
                self.logger.error(f"OpenAI API认证失败: {e}")
                return None
                
            except Exception as e:
                self.logger.error(f"翻译请求失败: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                else:
                    return None
        
        return None
    
    def test_connection(self) -> bool:
        """
        测试OpenAI API连接
        
        Returns:
            连接是否成功
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=10,
                timeout=10
            )
            return True
        except Exception as e:
            self.logger.error(f"OpenAI API连接测试失败: {e}")
            return False
    
    def cancel_request(self):
        """取消当前请求"""
        self.should_cancel = True
        self.logger.info("已标记取消OpenAI请求")
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        info = super().get_model_info()
        info.update({
            'provider': 'OpenAI',
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'timeout': self.timeout
        })
        return info