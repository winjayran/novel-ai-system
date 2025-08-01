import tiktoken
from .api import api_manager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CONTROLLER')

class Controller:
    """管理树结构的控制逻辑"""
    
    def __init__(self, token_limit=2000, summary_style="专业"):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.token_limit = token_limit  # 摘要token限制
        self.summary_style = summary_style
        self.combine_prompt = self._get_combine_prompt()
    
    def _get_combine_prompt(self):
        """获取合并摘要的提示词"""
        styles = {
            "专业": "使用专业、客观的语言，保持学术严谨性",
            "简洁": "用最简洁的语言概括，避免冗余描述",
            "生动": "使用生动的描述性语言，保留有趣的细节",
            "分析": "侧重分析性内容，突出模式和趋势"
        }
        
        style_desc = styles.get(self.summary_style, "使用清晰专业的语言")
        
        return (
            "你是一位专业编辑，负责将多个摘要合并为一个更高级别的摘要。要求：\n"
            f"1. {style_desc}\n"
            "2. 保留所有重要信息\n"
            "3. 识别并整合共同主题\n"
            "4. 突出关键发展和转折点\n"
            "5. 保持逻辑连贯性\n"
            "6. 长度控制在原始摘要总长度的30-40%\n\n"
            "输入摘要列表："
        )
    
    def token_count(self, text):
        """计算文本的token数量"""
        return len(self.tokenizer.encode(text))
    
    def combine_summaries(self, summaries):
        """
        合并多个摘要为一个更高级别的摘要
        
        :param summaries: 摘要列表
        :return: 合并后的摘要
        """
        logger.info(f"Combining {len(summaries)} summaries...")
        
        # 准备输入内容
        input_text = "\n\n".join([
            f"摘要 {i+1}:\n{summary}" 
            for i, summary in enumerate(summaries)
        ])
        
        # 检查token长度，如果过长则截断
        input_tokens = self.token_count(input_text)
        if input_tokens > 8000:
            logger.warning(f"Input too long ({input_tokens} tokens), truncating...")
            input_text = self._truncate_text(input_text, 8000)
        
        messages = [
            {"role": "user", "content": input_text}
        ]
        
        try:
            response = api_manager.call_api(
                messages, 
                system_prompt=self.combine_prompt,
                max_tokens=min(self.token_limit, 1500)
            )
            
            # 验证合并后的摘要长度
            output_tokens = self.token_count(response)
            if output_tokens > self.token_limit:
                logger.warning(f"Combined summary too long ({output_tokens} tokens), truncating...")
                response = response[:self.token_limit * 4]  # 粗略截断
            
            logger.debug(f"Combined summary ({output_tokens} tokens): {response[:100]}...")
            return response
        except Exception as e:
            logger.error(f"Summary combination failed: {e}")
            # 生成基本合并摘要作为后备
            return f"合并摘要 ({len(summaries)}部分): " + "; ".join(s[:100] + "..." for s in summaries)
    
    def should_split(self, node):
        """
        评估节点是否需要分裂
        
        :param node: 树节点
        :return: 布尔值，表示是否需要分裂
        """
        # 基础规则：子节点数量或token数超过阈值
        child_count = len(node.children)
        token_count = node.token_count
        
        # 简单规则：超过硬性限制
        if child_count > 5 or token_count > 3000:
            return True
        
        # 高级规则：评估内容多样性
        if child_count > 3:
            diversity_score = self._assess_diversity(node)
            if diversity_score > 0.7:  # 高多样性
                return True
        
        return False
    
    def _assess_diversity(self, node):
        """
        评估节点内容的多样性（简化实现）
        
        实际实现应使用AI分析内容多样性
        """
        # 简化实现：使用唯一词比例作为多样性代理
        all_text = " ".join(child.content for child in node.children)
        words = all_text.split()
        unique_words = set(words)
        return len(unique_words) / len(words) if words else 0
    
    def _truncate_text(self, text, max_tokens):
        """截断文本到指定的token数量"""
        tokens = self.tokenizer.encode(text)
        truncated_tokens = tokens[:max_tokens]
        return self.tokenizer.decode(truncated_tokens)

# 测试代码
if __name__ == "__main__":
    # 需要设置OPENAI_API_KEY环境变量
    controller = Controller()
    
    # 测试token计数
    text = "这是一个测试句子，用于计算token数量。"
    token_count = controller.token_count(text)
    print(f"Token count: {token_count}")
    
    # 测试摘要合并
    summaries = [
        "第一章：主角离开家乡，开始冒险旅程",
        "第二章：主角在森林中迷路，遇到神秘向导",
        "第三章：主角和向导发现古代遗迹的入口"
    ]
    
    print("\n合并摘要:")
    combined = controller.combine_summaries(summaries)
    print(combined)