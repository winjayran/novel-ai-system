import re
from .api import api_manager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('REMINDER')

class Reminder:
    """生成章节摘要和多维分析"""
    
    def __init__(self, genre="小说", language="中文"):
        self.genre = genre
        self.language = language
        self.summary_prompt = self._get_summary_prompt()
        self.analysis_prompt = self._get_analysis_prompt()
    
    def _get_summary_prompt(self):
        """根据类型生成摘要提示词"""
        if self.genre == "小说":
            return (
                "你是一位专业的文学编辑，负责为小说章节撰写摘要。请根据以下章节内容：\n"
                "1. 用150字左右概括本章核心情节\n"
                "2. 突出关键人物发展和重要转折点\n"
                "3. 标记可能的重要伏笔\n"
                "4. 保持专业文学风格\n"
                "输出格式：核心情节概括\n伏笔提示：[伏笔内容]"
            )
        elif self.genre == "学术论文":
            return (
                "你是一位学术编辑，负责为论文章节撰写摘要。请根据以下内容：\n"
                "1. 提炼核心论点和方法论\n"
                "2. 总结重要数据和发现\n"
                "3. 指出可能的局限性和未来研究方向\n"
                "输出格式：核心论点\n重要发现：[发现内容]"
            )
        else:  # 通用摘要
            return (
                "你是一位专业编辑，请为以下内容撰写摘要：\n"
                "1. 提炼核心信息（150字以内）\n"
                "2. 保持原文关键细节\n"
                "3. 使用清晰简洁的语言"
            )
    
    def _get_analysis_prompt(self):
        """根据类型生成分析提示词"""
        if self.genre == "小说":
            return (
                "你是一位文学分析师，请分析以下文本：\n"
                "1. 列出所有出场人物及其关键特征\n"
                "2. 标记所有伏笔和悬念\n"
                "3. 分析情感基调和主题发展\n"
                "4. 评估情节推进节奏\n"
                "输出格式：JSON格式，包含字段：characters, foreshadowing, tone, pacing"
            )
        elif self.genre == "学术论文":
            return (
                "你是一位学术评审，请分析以下文本：\n"
                "1. 提取核心概念和术语\n"
                "2. 评估论证逻辑强度\n"
                "3. 标记研究方法优缺点\n"
                "4. 识别潜在引用来源\n"
                "输出格式：JSON格式，包含字段：concepts, arguments, methods, references"
            )
        else:  # 通用分析
            return (
                "你是一位内容分析师，请分析以下文本：\n"
                "1. 提取关键实体和概念\n"
                "2. 分析信息结构和逻辑流\n"
                "3. 评估内容质量和完整性\n"
                "输出格式：JSON格式"
            )
    
    def summarize(self, text):
        """
        生成章节摘要
        :param text: 章节文本
        :return: 摘要字符串
        """
        logger.info(f"Generating summary for {len(text)} characters of text...")
        
        messages = [
            {"role": "user", "content": f"文本内容：\n{text[:10000]}"}  # 限制输入长度
        ]
        
        try:
            response = api_manager.call_api(
                messages, 
                system_prompt=self.summary_prompt,
                max_tokens=500
            )
            logger.debug(f"Summary generated: {response[:100]}...")
            return response
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            # 生成基本摘要作为后备
            return f"摘要生成失败，原始文本开头: {text[:200]}..."
    
    def analyze(self, text):
        """
        多维分析文本内容
        :param text: 文本内容
        :return: 分析结果字典
        """
        logger.info(f"Analyzing {len(text)} characters of text...")
        
        messages = [
            {"role": "user", "content": f"分析文本：\n{text[:8000]}"}  # 限制输入长度
        ]
        
        try:
            response = api_manager.call_api(
                messages, 
                system_prompt=self.analysis_prompt,
                max_tokens=800
            )
            logger.debug(f"Analysis response: {response[:200]}...")
            return self._parse_analysis(response)
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"error": str(e)}
    
    def _parse_analysis(self, response):
        """尝试解析分析结果为JSON格式"""
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group(0))
            else:
                # 如果找不到JSON，返回原始文本
                return {"raw_analysis": response}
        except Exception as e:
            logger.warning(f"JSON parsing failed: {e}")
            return {"raw_analysis": response}

# 测试代码
if __name__ == "__main__":
    # 需要设置OPENAI_API_KEY环境变量
    reminder = Reminder(genre="小说")
    sample_text = """
    第二章：神秘的地图
    
    在阁楼的旧箱子底部，艾米丽发现了一张泛黄的地图。地图上标记着森林深处的"月光泉"，
    旁边有一行小字："当满月升起时，真相将显现"。当她触摸地图时，奇怪的事情发生了—— 
    地图上的线条开始发光，形成一个狐狸的图案。突然，她听到楼下传来脚步声...
    """
    
    print("生成摘要:")
    summary = reminder.summarize(sample_text)
    print(summary)
    
    print("\n多维分析:")
    analysis = reminder.analyze(sample_text)
    print(analysis)