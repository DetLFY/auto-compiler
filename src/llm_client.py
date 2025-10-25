"""
LLM客户端封装
支持OpenAI格式的API调用
"""

import json
import logging
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)


class LLMClient:
    """OpenAI格式的LLM客户端"""
    
    def __init__(self, api_key: str, api_base: str = "https://api.openai.com/v1", 
                 model: str = "gpt-4-turbo-preview"):
        """
        初始化LLM客户端
        
        Args:
            api_key: OpenAI API密钥
            api_base: API基础URL（支持兼容OpenAI的其他服务）
            model: 使用的模型名称
        """
        self.api_key = api_key
        self.api_base = api_base.rstrip('/')
        self.model = model
        self.timeout = 120  # 请求超时时间
        
        logger.info(f"初始化LLM客户端: {api_base}, 模型: {model}")
    
    def chat(self, messages: List[Dict], temperature: float = 0.7, 
             max_tokens: int = 4096) -> str:
        """
        简单的聊天调用
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            str: LLM的回复内容
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API调用失败: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"解析LLM响应失败: {e}")
            raise
    
    def call_with_tools(self, messages: List[Dict], tools: List[Dict], 
                       temperature: float = 0.7) -> Dict:
        """
        带工具调用的API请求
        
        Args:
            messages: 消息列表
            tools: 工具定义列表
            temperature: 温度参数
            
        Returns:
            Dict: 包含工具调用信息的响应
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "temperature": temperature,
            "tool_choice": "auto"
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            message = result['choices'][0]['message']
            
            return {
                'content': message.get('content'),
                'tool_calls': message.get('tool_calls', [])
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API调用失败: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"解析LLM响应失败: {e}")
            raise
    
    def stream_chat(self, messages: List[Dict], temperature: float = 0.7):
        """
        流式聊天调用（用于实时显示生成过程）
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            
        Yields:
            str: 流式返回的内容片段
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line = line[6:]
                        if line.strip() == '[DONE]':
                            break
                        try:
                            chunk = json.loads(line)
                            delta = chunk['choices'][0]['delta']
                            if 'content' in delta:
                                yield delta['content']
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM流式API调用失败: {e}")
            raise
