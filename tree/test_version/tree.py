import os
import pickle
import time

class Node:
    """表示树中的节点"""
    def __init__(self, level, content="", parent=None):
        self.level = level        # 节点层级（0=叶子节点）
        self.content = content    # 节点摘要内容
        self.parent = parent      # 父节点引用
        self.children = []        # 子节点列表
        self.token_count = 0      # 摘要的token计数
        self.created_at = time.time()  # 节点创建时间戳
        self.next_leaf = None     # 指向下一个叶子节点（用于叶子链表）
        
    def __repr__(self):
        return f"Node(L{self.level}, tokens={self.token_count}, children={len(self.children)})"

class WritingTree:
    """树状结构管理系统"""
    def __init__(self, name="novel", max_children=3, max_tokens=100):
        self.name = name          # 树名称/标识符
        self.root = None          # 根节点
        self.max_children = max_children  # 节点最大子节点数
        self.max_tokens = max_tokens      # 节点最大token容量
        self.leaf_head = None     # 首叶子节点
        self.leaf_tail = None     # 尾叶子节点
        self.node_counter = 0     # 节点ID计数器
        self.total_chapters = 0   # 总章节数
        self.version = "1.0"      # 树版本
    
    def insert_chapter(self, chapter_text):
        """插入新章节到树结构中"""
        self.total_chapters += 1
        
        # 1. 调用reminder生成章节摘要
        chapter_summary = FAKE_reminder.summarize(chapter_text)
        
        # 2. 创建叶子节点
        new_leaf = Node(level=0, content=chapter_summary)
        new_leaf.token_count = FAKE_controller.token_count(chapter_summary)
        
        # 3. 处理空树情况
        if self.root is None:
            self.root = new_leaf
            self.leaf_head = new_leaf
            self.leaf_tail = new_leaf
            return new_leaf
        
        # 4. 更新叶子节点链表
        if self.leaf_tail:
            self.leaf_tail.next_leaf = new_leaf
        self.leaf_tail = new_leaf
        if not self.leaf_head:
            self.leaf_head = new_leaf
        
        # 5. 插入节点并更新树结构
        self._insert_node(new_leaf, self.root)
        return new_leaf
    
    def _insert_node(self, new_node, current_node):
        """递归插入节点并更新路径"""
        # 到达叶子层或找到合适插入点
        if current_node.level == new_node.level + 1:
            # 添加到当前节点子集
            current_node.children.append(new_node)
            new_node.parent = current_node
            
            # 更新当前节点摘要
            self._update_node_content(current_node)
            
            # 检查是否需要分裂
            if (len(current_node.children) > self.max_children or 
                current_node.token_count > self.max_tokens):
                self._split_node(current_node)
            return
        
        # 递归寻找插入位置（默认插入到最右子树）
        if current_node.children:
            self._insert_node(new_node, current_node.children[-1])
    
    def _update_node_content(self, node):
        """更新节点摘要和token计数"""
        if not node.children:
            return
        
        # 获取所有子节点摘要
        child_summaries = [child.content for child in node.children]
        
        # 调用controller生成新摘要
        new_content = FAKE_controller.combine_summaries(child_summaries)
        node.content = new_content
        node.token_count = FAKE_controller.token_count(new_content)
        
        # 递归更新父节点
        if node.parent:
            self._update_node_content(node.parent)
    
    def _split_node(self, node):
        """分裂过大的节点"""
        if len(node.children) <= 1:
            return  # 无法分裂
        
        print(f"节点分裂触发 (层级 {node.level}, 子节点数 {len(node.children)})")
        
        # 1. 创建新兄弟节点
        mid_index = len(node.children) // 2
        new_node = Node(level=node.level, parent=node.parent)
        
        # 2. 转移子节点
        new_node.children = node.children[mid_index:]
        node.children = node.children[:mid_index]
        
        # 3. 更新父引用
        for child in new_node.children:
            child.parent = new_node
        
        # 4. 更新节点摘要
        self._update_node_content(node)
        self._update_node_content(new_node)
        
        # 5. 处理根节点分裂
        if node == self.root:
            print("根节点分裂，树高度增加")
            new_root = Node(level=node.level+1, parent=None)
            new_root.children = [node, new_node]
            node.parent = new_root
            new_node.parent = new_root
            self.root = new_root
            self._update_node_content(new_root)
            return
        
        # 6. 添加到父节点
        parent = node.parent
        parent.children.append(new_node)
        
        # 7. 检查父节点是否需要分裂
        if (len(parent.children) > self.max_children or 
            parent.token_count > self.max_tokens):
            self._split_node(parent)
    
    def print_tree(self, node=None, indent=0):
        """打印树结构（调试用）"""
        node = node or self.root
        prefix = "  " * indent
        print(f"{prefix}L{node.level}: {node.content[:30]}{'...' if len(node.content)>30 else ''}")
        for child in node.children:
            self.print_tree(child, indent+1)
    
    def traverse_leaves(self):
        """遍历所有叶子节点（章节）"""
        current = self.leaf_head
        while current:
            yield current
            current = current.next_leaf
    
    def save_tree(self, filename=None):
        """将树结构保存到文件"""
        if not filename:
            filename = f"{self.name}_writing_tree.pkl"
        
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
        print(f"树结构已保存到 {filename}")
        return filename
    
    @staticmethod
    def load_tree(filename):
        """从文件加载树结构"""
        if not os.path.exists(filename):
            raise FileNotFoundError(f"文件 {filename} 不存在")
        
        with open(filename, 'rb') as f:
            tree = pickle.load(f)
        print(f"已从 {filename} 加载树结构")
        return tree
    
    def find_chapter(self, chapter_num):
        """查找特定章节节点（简单实现）"""
        current = self.leaf_head
        count = 1
        while current:
            if count == chapter_num:
                return current
            current = current.next_leaf
            count += 1
        return None

class FAKE_reminder:
    """模拟reminder代理的类"""
    @staticmethod
    def summarize(text):
        """生成章节摘要（模拟）"""
        # 真实实现应使用AI模型生成摘要
        words = text.split()[:10]  # 取前10个单词
        return f"摘要: {' '.join(words)}..."
    
    @staticmethod
    def analyze_characters(text):
        """分析人物（模拟）"""
        return ["主角A", "配角B"]  # 返回检测到的人物列表

class FAKE_controller:
    """模拟controller代理的类"""
    @staticmethod
    def token_count(text):
        """计算token数（模拟）"""
        # 真实实现应使用实际tokenizer
        return len(text.split())  # 简单分词计数
    
    @staticmethod
    def combine_summaries(summaries):
        """合并多个摘要（模拟）"""
        # 真实实现应使用AI模型生成高级摘要
        return f"合并摘要({len(summaries)}节点): " + "; ".join(
            s[:15] + "..." if len(s) > 15 else s for s in summaries
        )
    
    @staticmethod
    def should_split(node_children, node_tokens, max_children, max_tokens):
        """判断是否需要分裂（模拟）"""
        return len(node_children) > max_children or node_tokens > max_tokens

# 示例使用
if __name__ == "__main__":
    # 创建树
    novel_tree = WritingTree(name="my_novel", max_children=3, max_tokens=50)
    
    # 插入章节
    chapters = [
        "第一章：故事开始于一个风雨交加的夜晚，主角小明在森林中迷路了...",
        "第二章：小明遇到了一位神秘的老人，老人给了他一张古老的地图...",
        "第三章：根据地图指示，小明来到了一座废弃的城堡，发现了一个秘密通道...",
        "第四章：在通道深处，小明发现了一本记载着古老魔法的书籍...",
        "第五章：学习魔法后，小明意外召唤出了一个友善的精灵伙伴...",
        "第六章：精灵告诉小明关于城堡被诅咒的历史，以及解除诅咒的方法...",
        "第七章：小明开始寻找解除诅咒所需的三种神秘元素...",
        "第八章：在寻找第一个元素时，小明遇到了守护兽的挑战...",
        "第九章：经过一番苦战，小明成功获得了第一个元素...",
        "第十章：在寻找第二个元素的途中，小明发现了一个关于自己身世的惊人秘密..."
    ]
    
    for i, chapter in enumerate(chapters, 1):
        print(f"\n插入第{i}章: {chapter[:20]}...")
        novel_tree.insert_chapter(chapter)
        
        # 每3章打印一次树结构
        if i % 3 == 0:
            print(f"\n当前树结构 (第{i}章后):")
            novel_tree.print_tree()
    
    # 保存树结构
    saved_file = novel_tree.save_tree()
    
    # 遍历叶子节点
    print("\n所有章节摘要:")
    for i, leaf in enumerate(novel_tree.traverse_leaves(), 1):
        print(f"第{i}章: {leaf.content}")
    
    # 查找特定章节
    chapter5 = novel_tree.find_chapter(5)
    if chapter5:
        print(f"\n找到第5章: {chapter5.content}")
    
    # 从文件加载树结构
    print("\n从文件加载树结构...")
    loaded_tree = WritingTree.load_tree(saved_file)
    
    # 打印加载的树结构
    print("\n加载后的树结构:")
    loaded_tree.print_tree()
    
    # 检查树属性
    print(f"\n树统计信息:")
    print(f"名称: {loaded_tree.name}")
    print(f"总章节数: {loaded_tree.total_chapters}")
    print(f"树高度: {loaded_tree.root.level + 1}")
    print(f"叶子节点数: {sum(1 for _ in loaded_tree.traverse_leaves())}")