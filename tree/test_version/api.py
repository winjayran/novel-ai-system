import os
import openai
import time
import logging
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AI_API')

class APIManager:
    """管理AI API调用，处理速率限制和错误重试"""
    
    def __init__(self):
        load_dotenv()  # 加载环境变量
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        openai.api_key = api_key
        self.rate_limit_delay = 1.0  # 默认速率限制延迟
        self.max_retries = 3  # 最大重试次数
        self.model = "gpt-4-turbo"  # 默认模型
    
    def call_api(self, messages, max_tokens=1000, temperature=0.7, system_prompt=None):
        """
        调用AI API并处理错误重试
        
        :param messages: 消息列表
        :param max_tokens: 最大返回token数
        :param temperature: 生成温度
        :param system_prompt: 系统提示词
        :return: API响应内容
        """
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        for attempt in range(self.max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message['content'].strip()
            
            except openai.error.RateLimitError:
                delay = self.rate_limit_delay * (2 ** attempt)  # 指数退避
                logger.warning(f"Rate limit exceeded, retrying in {delay:.1f}s (attempt {attempt+1}/{self.max_retries})")
                time.sleep(delay)
            
            except openai.error.APIError as e:
                logger.error(f"API error: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
                else:
                    raise
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise
        
        raise RuntimeError("Failed to call API after multiple retries")
    
    def set_model(self, model_name):
        """设置使用的AI模型"""
        valid_models = ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
        if model_name not in valid_models:
            raise ValueError(f"Invalid model. Valid options: {', '.join(valid_models)}")
        self.model = model_name
        logger.info(f"Model set to: {model_name}")

# 单例实例
api_manager = APIManager()

if __name__ == "__main__":
    # 测试API调用
    test_messages = [{"role": "user", "content": "Hello, how are you?"}]
    response = api_manager.call_api(test_messages)
    print("API Test Response:", response)