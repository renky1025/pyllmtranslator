"""
Ollama本地模型客户端
"""

import requests
import json
import logging
from typing import Optional, Dict, Any
from .client_base import LLMClientBase

class OllamaClient(LLMClientBase):
    """Ollama本地模型客户端"""
    
    def __init__(self, api_key: str = "", model: str = "llama3.2", **kwargs):
        # Ollama不需要API密钥，但保持接口一致性
        super().__init__(api_key, model, **kwargs)
        
        # 配置参数
        self.base_url = kwargs.get('base_url', 'http://localhost:11434')
        self.temperature = kwargs.get('temperature', 0.1)
        self.timeout = kwargs.get('timeout', 120)  # Ollama可能需要更长时间
        self.max_retries = kwargs.get('max_retries', 3)
        
        self.logger = logging.getLogger(__name__)
        
        # 用于取消请求的会话
        self.session = requests.Session()
        self.current_request = None
        
        # 确保base_url格式正确
        if not self.base_url.startswith('http'):
            self.base_url = f'http://{self.base_url}'
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
    
    def translate(self, prompt: str, **kwargs) -> Optional[str]:
        """
        使用Ollama API翻译文本
        
        Args:
            prompt: 完整的翻译提示词
            **kwargs: 其他参数
            
        Returns:
            翻译结果
        """
        # 确保模型可用
        if not self.ensure_model_available():
            self.logger.error("没有可用的模型进行翻译")
            return None
        
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": kwargs.get('max_tokens', 12768)
            }
        }
        
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"发送翻译请求到Ollama (尝试 {attempt + 1}/{self.max_retries})")
                
                # 使用会话发送请求，以便可以取消
                self.current_request = self.session.post(
                    url,
                    json=payload,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )
                response = self.current_request
                
                if response.status_code == 200:
                    result = response.json()
                    if 'response' in result:
                        return result['response'].strip()
                    else:
                        self.logger.warning("Ollama API返回格式异常")
                        return None
                else:
                    self.logger.error(f"Ollama API请求失败: {response.status_code} - {response.text}")
                    if attempt < self.max_retries - 1:
                        continue
                    return None
                    
            except requests.exceptions.ConnectionError as e:
                self.logger.error(f"无法连接到Ollama服务 ({self.base_url}): {e}")
                if attempt < self.max_retries - 1:
                    self.logger.info("等待重试...")
                    continue
                return None
                
            except requests.exceptions.Timeout as e:
                self.logger.warning(f"Ollama请求超时 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    continue
                return None
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Ollama请求异常: {e}")
                if attempt < self.max_retries - 1:
                    continue
                return None
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Ollama响应JSON解析失败: {e}")
                return None
                
            except Exception as e:
                self.logger.error(f"Ollama翻译请求失败: {e}")
                if attempt < self.max_retries - 1:
                    continue
                return None
        
        return None
    
    def ensure_model_available(self) -> bool:
        """
        确保模型可用，如果不可用则自动选择第一个可用模型
        
        Returns:
            是否找到可用模型
        """
        try:
            available_models = self.get_available_models()
            if not available_models:
                self.logger.error("没有找到任何可用模型")
                return False
            
            # 检查当前模型是否可用
            if not any(self.model in name for name in available_models):
                self.logger.warning(f"模型 {self.model} 未找到，可用模型: {available_models}")
                # 自动选择第一个可用模型
                self.model = available_models[0]
                self.logger.info(f"自动选择模型: {self.model}")
            
            return True
        except Exception as e:
            self.logger.error(f"检查模型可用性失败: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        测试Ollama服务连接
        
        Returns:
            连接是否成功
        """
        try:
            # 首先检查服务是否运行
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code != 200:
                self.logger.error(f"Ollama服务不可用: {response.status_code}")
                return False
            
            # 确保模型可用
            if not self.ensure_model_available():
                return False
            
            # 测试简单的生成请求
            test_response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": "Hello",
                    "stream": False,
                    "options": {"num_predict": 5}
                },
                timeout=30
            )
            
            if test_response.status_code == 200:
                result = test_response.json()
                return 'response' in result
            else:
                self.logger.error(f"Ollama测试请求失败: {test_response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.logger.error(f"无法连接到Ollama服务: {self.base_url}")
            return False
        except Exception as e:
            self.logger.error(f"Ollama连接测试失败: {e}")
            return False
    
    def get_available_models(self) -> list:
        """
        获取可用的模型列表
        
        Returns:
            模型名称列表
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model.get('name', '') for model in models]
            else:
                self.logger.error(f"获取模型列表失败: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"获取Ollama模型列表失败: {e}")
            return []
    
    def cancel_request(self):
        """取消当前请求"""
        try:
            if self.current_request:
                # 关闭会话以取消请求
                self.session.close()
                # 重新创建会话
                self.session = requests.Session()
                self.current_request = None
                self.logger.info("已取消Ollama请求")
        except Exception as e:
            self.logger.error(f"取消Ollama请求失败: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        info = super().get_model_info()
        info.update({
            'provider': 'Ollama',
            'base_url': self.base_url,
            'temperature': self.temperature,
            'timeout': self.timeout,
            'available_models': self.get_available_models()
        })
        return info