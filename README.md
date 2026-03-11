# AI Research Agent

> 基于 ReAct + Function Calling 的智能研究助手，能自主决策使用多种工具完成复杂任务

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Qwen](https://img.shields.io/badge/Qwen--Plus-LLM-6366F1?style=for-the-badge)
![Tavily](https://img.shields.io/badge/Tavily-Search-FF6F61?style=for-the-badge)
![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG-orange?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)

![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Agent](https://img.shields.io/badge/AI-Agent-blue?style=flat-square)
![ReAct](https://img.shields.io/badge/ReAct-Reasoning%2BActing-purple?style=flat-square)
![Function Calling](https://img.shields.io/badge/Function-Calling-orange?style=flat-square)

---

## 项目背景

这是 [资本论 RAG 问答系统](https://github.com/wp958/rag_marx_assistant) 的进阶项目。

RAG 系统的局限性：流程固定，只能检索知识库，无法处理实时信息、数学计算等需求。

本项目引入 AI Agent，将 RAG 变成 Agent 的一个工具，让 LLM 自主决策使用何种工具，从"固定流水线"升级为"智能调度中心"。
项目1（RAG）：用户问 → 检索知识库 → 生成回答（固定流程）
项目2（Agent）：用户问 → AI思考 → 自主选择工具 → 执行 → 回答（动态决策）



---

## 系统架构

                   用户提问
                      |
                      v
           ┌─────────────────────┐
           │    LLM 思考（大脑）   │
           │  "我需要用什么工具？" │
           └──────────┬──────────┘
                      |
        ┌─────────────┼─────────────┐
        |             |             |
        v             v             v
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ web_search │ │calculate │ │ summarize │
│ 网络搜索 │ │ 数学计算 │ │ 文本摘要 │
│ (Tavily) │ │ │ │ │
└──────────────┘ └──────────┘ └──────────────┘
|
v
┌─────────────────────┐
│ knowledge_search │
│ 知识库检索（RAG） │
│ 复用项目1的ChromaDB │
│ 3500个文档块 │
└─────────────────────┘
|
v (所有工具结果返回)
┌─────────────────────┐
│ LLM 综合生成回答 │
└─────────────────────┘



### ReAct 循环
Reasoning（推理）+ Acting（行动）= ReAct

Step 1: 思考 - "这个问题需要搜索实时信息"
Step 2: 行动 - 调用 web_search("AI Agent trends 2024")
Step 3: 观察 - 得到搜索结果
Step 4: 思考 - "信息够了，可以回答"
Step 5: 回答 - 生成最终答案

如果信息不够，循环回到 Step 1 继续思考



---

## 项目亮点

| 能力 | 实现 |
|:---:|:---|
| 🧠 **自主决策** | LLM 通过 Function Calling 自主选择工具，无需硬编码规则 |
| 🔍 **网络搜索** | Tavily API 获取实时互联网信息 |
| 📚 **知识库检索** | 复用 RAG 项目的 ChromaDB 向量数据库（3500个文档块） |
| 🔢 **数学计算** | 安全的表达式计算 |
| 📝 **文本摘要** | 长文本关键信息提取 |
| 🔄 **多步推理** | ReAct 循环，最多5轮工具调用 |
| 👁️ **过程可视化** | 前端展示完整的思考-行动-观察过程 |

---

## 技术选型

| 模块 | 技术 | 选型理由 |
|:---|:---|:---|
| **Agent框架** | 原生实现（无LangChain） | 理解底层原理 |
| **工具调用** | OpenAI Function Calling | Qwen-Plus 原生支持，稳定可靠 |
| **网络搜索** | Tavily API | 专为 AI Agent 设计，返回结构化结果 |
| **知识库** | ChromaDB + text2vec | 复用 RAG 项目，语义检索 |
| **大模型** | Qwen-Plus | Function Calling 支持好，中文能力强 |
| **Web** | Flask | 轻量灵活 |

---

## 与 RAG 项目的关系
┌──────────────────────────────────────────────────────────┐
│ 项目2: AI Agent │
│ │
│ Agent 的工具箱： │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌─────────────────┐ │
│ │ Tavily │ │计算器 │ │摘要 │ │ 知识库检索 │ │
│ │ 搜索 │ │ │ │ │ │ (项目1的数据库) │ │
│ └────────┘ └────────┘ └────────┘ └────────┬────────┘ │
│ │ │
└─────────────────────────────────────────────┼────────────┘
│
│ 共享数据
│
┌─────────────────────────────────────────────┼────────────┐
│ 项目1: RAG 问答系统 │ │
│ │ │
│ ┌─────────────────────────────────────┐ │ │
│ │ ChromaDB 向量数据库 │◄───┘ │
│ │ 资本论全三卷 / 3500 chunks │ │
│ │ text2vec-base-chinese / 768维 │ │
│ └─────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘


---

## 项目结构
ai_research_agent/
├── src/
│ ├── config.py # 配置（API Key / 参数）
│ ├── tools.py # 4个工具实现 + Function定义
│ ├── agent.py # Agent核心：ReAct循环
│ ├── app.py # Flask Web应用
│ └── templates/
│ └── index.html # 前端（思考过程可视化）
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md



---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/wp958/ai_research_agent.git
cd ai_research_agent
2. 安装依赖
Bash

pip install -r requirements.txt
3. 配置 API Key
编辑 src/config.py，填入：

Qwen API Key（通义千问）
Tavily API Key（搜索引擎）
4. 前置条件
本项目的知识库检索工具依赖 RAG 项目 的向量数据库。请先运行 RAG 项目构建索引。

5. 启动
Bash

cd src
python app.py
浏览器打开 http://127.0.0.1:5002

核心实现
Function Calling 工作流
Python

# 1. 定义工具
tools = [
    {"name": "web_search", "description": "搜索互联网"},
    {"name": "knowledge_search", "description": "搜索知识库"},
    {"name": "calculate", "description": "数学计算"},
]

# 2. LLM自主决策
response = llm.chat(messages, tools=tools, tool_choice="auto")

# 3. 如果LLM决定调用工具
if response.tool_calls:
    tool_name = response.tool_calls[0].function.name    # LLM选的工具
    tool_args = response.tool_calls[0].function.arguments  # LLM给的参数
    result = execute_tool(tool_name, tool_args)  # 执行工具
    # 把结果返回给LLM继续思考

# 4. 如果LLM决定直接回答
else:
    final_answer = response.content
ReAct 循环控制
Python

for step in range(MAX_STEPS):   # 最多5轮
    response = llm.chat(messages, tools=tools)
    
    if response.tool_calls:
        # 执行工具 → 结果加入对话 → 继续循环
        ...
    else:
        # 生成最终回答 → 跳出循环
        return response.content
工具决策示例
text

用户："根据资本论，什么是商品？"
Agent思考：这是经济学概念 → knowledge_search
Agent行动：knowledge_search("商品")
Agent观察：找到资本论相关段落
Agent回答：基于原文生成回答

用户："2024年AI Agent最新趋势？"
Agent思考：需要实时信息 → web_search
Agent行动：web_search("2024 AI Agent trends")
Agent观察：搜到3篇文章
Agent回答：总结搜索结果

用户："帮我算 (100*25+300)/5"
Agent思考：数学计算 → calculate
Agent行动：calculate("(100*25+300)/5")
Agent观察：结果是 560
Agent回答：计算结果是560
性能指标
指标	数值
工具数量	4个（搜索/知识库/摘要/计算）
最大推理步数	5步
单工具延迟	2-5秒
多工具延迟	5-10秒
知识库规模	3500 chunks（共享RAG项目）
优化方向
 流式输出（SSE）：实时展示 Agent 思考过程
 更多工具：代码执行、文件读写、数据库查询
 工具并行调用：多个独立工具同时执行
 记忆系统：长期记忆 + 短期记忆管理
 多Agent协作：多个Agent分工合作完成复杂任务
技术栈总览
text

┌─────────────────────────────────────────────────┐
│                  Frontend                        │
│            HTML / CSS / JavaScript               │
└───────────────────────┬─────────────────────────┘
                        |
┌───────────────────────┴─────────────────────────┐
│                  Backend                         │
│                   Flask                          │
└───────────────────────┬─────────────────────────┘
                        |
┌───────────────────────┴─────────────────────────┐
│              Agent Core (ReAct)                  │
│  ┌──────────────────────────────────────────┐   │
│  │         Function Calling Loop            │   │
│  │   Think → Select Tool → Execute → Observe│   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌───────────────┐   │
│  │ Tavily   │ │Calculate │ │ ChromaDB RAG  │   │
│  │ Search   │ │          │ │ (from proj.1) │   │
│  └──────────┘ └──────────┘ └───────────────┘   │
│                                                  │
│              LLM: Qwen-Plus                     │
└─────────────────────────────────────────────────┘
License
MIT License

作者
GitHub: @wp958


相关项目：资本论 RAG 问答系统

