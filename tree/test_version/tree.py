class Node:
    def __init__(self, level, content="", parent=None):
        self.level = level        # 节点层级（0=叶子节点）
        self.content = content    # 节点摘要内容
        self.parent = parent      # 父节点引用
        self.children = []       # 子节点列表
        self.token_count = 0     # 摘要的token计数
        
    def __repr__(self):
        return f"Node(L{self.level}, tokens={self.token_count}, children={len(self.children)})"

class WritingTree:
    def __init__(self, max_children=3, max_tokens=100):
        self.root = None
        self.max_children = max_children  # 节点最大子节点数
        self.max_tokens = max_tokens      # 节点最大token容量
        self.leaf_head = None             # 首叶子节点
        self.leaf_tail = None             # 尾叶子节点
        self.node_counter = 0             # 节点ID计数器
    
    def insert_chapter(self, chapter_text):
        """插入新章节到树结构中"""
        # 1. 调用reminder生成章节摘要
        chapter_summary = reminder.summarize(chapter_text)
        
        # 2. 创建叶子节点
        new_leaf = Node(level=0, content=chapter_summary)
        new_leaf.token_count = controller.token_count(chapter_summary)
        
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
        
        # 递归寻找插入位置
        if current_node.children:
            self._insert_node(new_node, current_node.children[-1])
    
    def _update_node_content(self, node):
        """更新节点摘要和token计数"""
        if not node.children:
            return
        
        # 获取所有子节点摘要
        child_summaries = [child.content for child in node.children]
        
        # 调用controller生成新摘要
        new_content = controller.combine_summaries(child_summaries)
        node.content = new_content
        node.token_count = controller.token_count(new_content)
    
    def _split_node(self, node):
        """分裂过大的节点"""
        if len(node.children) <= 1:
            return  # 无法分裂
        
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

# 示例使用
if __name__ == "__main__":
    # 模拟reminder和controller的简单实现
    class reminder:
        @staticmethod
        def summarize(text):
            return f"摘要[{text[:15]}...]"  # 简化的摘要生成
        
    class controller:
        @staticmethod
        def token_count(text):
            return len(text.split())  # 简单分词计数
        
        @staticmethod
        def combine_summaries(summaries):
            return f"合并({len(summaries)}节点): " + "; ".join(summaries)
    
    # 创建树并插入章节
    tree = WritingTree(max_children=3, max_tokens=50)
    for i in range(1, 6):
        text = f"第{i}章内容: {'文本数据' * i * 10}"
        tree.insert_chapter(text)
        print(f"插入第{i}章后树结构:")
        tree.print_tree()
        print("\n" + "="*50 + "\n")