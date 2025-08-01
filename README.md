# Readme

## 思路介绍
1. 前期先全部采用icl/prompt_engineering的方法，基本机构构建后，后期采用sft方法
2. 在这个架构里面有：writer, reminder, evaluator, revisor, controller, thinker（可能还会加）
- writer: 故事主笔，相比thinker，其更注重“写”
- reminder: 为writer记录故事大纲、人物设定、处理铺垫，以及writer向reminder提出查询细节后，返回writer特定内容的
- evaluator: 评估当前章节的生成优劣以及向reminder提出查询故事大纲、人物设定、处理铺垫的合理性检验
- revisor: 接收evaluator的评估结果，进行当前章节的润色
- thinker: 章节创意提供者，和writer交互，但是受到evaluator限制
- controller: 见下
3. 为了处理100w+的超长上下文，我创新给出“小说的树折叠结构”---writing_tree，用一颗树来支配整部小说的章节内容，在writer生成一个章节后，reminder都会记录下故事大纲、人物设定、处理铺垫（发挥概括功能）作为一个新的叶子节点加入到writing_tree里面，并且根据writing_tree的controller评估，向上增加父节点进行分裂（类似于B+树）。在树的节点和节点之间，有链将人物情节连在一起，以展现其变化特征。
4. 树上的每一个节点，都由"人物/背景/情节"三维组成，相互关联，reminder的访问，将会向controler访问。

## 预期项目框架
```text
novel-ai-system/
├── agents/                       # 智能体核心模块
│   ├── writer/                   # 写作者智能体
│   │   ├── writer.py             # 主逻辑
│   │   ├── prompts/              # 提示词模板
│   │   │   ├── main.md           # 主提示词
│   │   │   ├── action_scene.md   # 动作场景模板
│   │   │   └── dialogue.md       # 对话模板
│   │   └── utils.py              # 专用工具函数
│   ├── reminder/                 # 记忆管理智能体
│   │   ├── reminder.py
│   │   ├── prompts/
│   │   │   └── summary.md        # 摘要生成提示词
│   │   └── memory_cache.py       # 记忆缓存系统
│   ├── evaluator/                # 评估智能体
│   │   ├── evaluator.py
│   │   ├── metrics/              # 评估指标体系
│   │   │   ├── consistency.py    # 一致性指标
│   │   │   └── engagement.py     # 读者参与度指标
│   │   └── prompts/
│   │       └── evaluation.md
│   ├── revisor/                  # 修订智能体
│   │   ├── revisor.py
│   │   └── prompts/
│   │       └── revision.md
│   ├── thinker/                  # 创意生成智能体
│   │   ├── thinker.py
│   │   └── prompts/
│   │       ├── plot_twist.md     # 情节转折模板
│   │       └── character_dev.md  # 角色发展模板
│   └── controller/               # 树结构控制器
│       ├── controller.py
│       ├── tree_operations.py    # 树操作专用方法
│       └── entropy_calculator.py # 叙事熵计算器
├── tree/                         # 树结构核心模块
│   ├── tree.py                   # 树结构实现
│   ├── node.py                   # 树节点定义
│   ├── chain.py                  # 节点间关系链
│   ├── serialization.py          # 树序列化/反序列化
|   └── test_version/             # 树测试版本
├── fictions/                     # 小说项目存储
│   └── <fiction_name>/           # 单部小说项目
│       ├── chapters/             # 章节存储
│       │   ├── chapter_001.md    # 按章节存储
│       │   └── chapter_002.md
│       ├── current/              # 当前工作区
│       │   ├── draft.md          # 当前草稿
│       │   └── feedback.json     # 评估反馈
│       └── tree_data/            # 树结构数据库
│           ├── nodes/            # 节点数据(LevelDB)
│           ├── relations/        # 关系数据(LevelDB)
│           └── metadata.json     # 树元数据
├── core/                         # 核心系统模块
│   ├── orchestration.py          # 工作流编排引擎
│   ├── state_manager.py          # 状态管理器
│   └── api_client.py             # 统一AI API客户端
├── config/                       # 配置文件
│   ├── agents.yaml               # 智能体配置
│   ├── tree_config.yaml          # 树结构参数
│   └── api_keys.env              # API密钥管理
├── tests/                        # 测试套件
│   ├── unit/                     # 单元测试
│   │   ├── test_tree_ops.py
│   │   └── test_agent_writer.py
│   └── integration/              # 集成测试
│       └── test_full_workflow.py
├── scripts/                      # 实用脚本
│   ├── new_fiction.py            # 创建新小说项目
│   ├── generate_chapter.py       # 生成单章
│   └── visualize_tree.py         # 树结构可视化
├── docs/                         # 项目文档
│   ├── ARCHITECTURE.md           # 系统架构说明
│   └── WORKFLOW.md               # 工作流程详解
├── requirements.txt              # Python依赖
├── .gitignore
└── main.py                       # 主入口
```

## 项目计划
1. 完成`树测试版本`。



## writing_tree初衷
针对目前AI难以处理超长文字处理（例如小说等），100w级别，我给出“树折叠结构”---writing_tree，用一颗树来支配所有内容，每次读入一个新的章节后，reminder都会记录下这段文字多维上面的描述，（假如是小说，就记录故事大纲、人物设定、处理铺垫）（发挥概括功能）作为一个新的叶子节点加入到writing_tree里面，并且根据writing_tree的controller评估，向上传递添加的内容，每上升一层，其概括的内容增加，如果父节点的存储大小超过设定大小，就对父节点进行分裂（类似于B+树），依次往上。在树的节点和节点之间，有链将相关信息连在一起，以展现其变化特征。
其中reminder和controller都是一个agent。