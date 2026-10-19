# 🛒 企业级 AI 智能售后客服 Agent (Agentic AI)

<p align="center">
  <img src="assets/界面截图1.jpg" alt="系统界面预览" width="800">
</p>

## 🌟 项目简介
本项目是一个**全栈式、高保真**的电商售后智能客服系统。针对传统客服行业“查单慢、手动建单繁琐、容易引发客诉”的痛点，基于 LangChain 框架与 DeepSeek 大模型，打造了真正的 **Agentic AI（自主智能体）**。

用户可以通过自然语言直接申请退款，AI 会**自主决策**并调用后端 Python 脚本，完成查库、核实订单、生成工单的全流程。主管可在页面顶部的一体化面板中一键审核，实现了**“AI 自动提单 + 人工一键审核”**的完整企业级业务闭环。

## 🛠️ 核心技术栈
- **核心框架**：Python, Streamlit (前端 UI), LangChain (Agent 调度)
- **大模型引擎**：DeepSeek API (支持 Function Calling 工具调用)
- **后端数据库**：SQLite (轻量级企业业务存储)
- **工程化规范**：`.env` 环境变量隔离, `.gitignore` 安全防泄漏, `requirements.txt` 依赖管理
- **UI 设计**：淘宝大厂级红橙 + 纯白高保真商业配色，丝滑的交互动效

## ✨ 核心亮点 (面试高光点)
1. **真正的智能体 (Agent)**：AI 不再只会“聊天”。它具备 Function Calling 能力，能自主判断用户意图，并决定何时去查数据库、何时去创建工单，极大降低了大模型的“幻觉”。
2. **防重复退款风控**：具备严格的业务边界约束。若查询到订单状态已是【已退款】，AI 会果断拒绝用户的二次退款请求，保障企业资金安全。
3. **完整的业务闭环**：客户在前端对话 -> AI 跨端调用 Python 查库 -> 自动在 SQLite 写入真实工单 -> 主管在后台点击审核 -> 状态同步更新为已退款。

## 🚧 踩坑与工程化解决 (真实开发记录)
在项目本地开发与部署过程中，我独立排查并解决了多个底层工程 Bug：
1. **Windows 系统 Unicode 编码报错 (`UnicodeEncodeError: ascii/latin-1`)**：
   * *原因*：Windows 默认编码与 HTTP 库底层请求头不兼容，导致传递中文字符（如“墨菲定律”）时崩溃。
   * *解决*：放弃外部库的隐式编码，采用原生 `json.dumps(..., ensure_ascii=True)` 强制将所有中文载荷序列化为纯英文字符串再发送，彻底绕开操作系统编码限制。
2. **大模型 LangChain 版本冲突 (`ImportError`)**：
   * *原因*：LangChain 1.0 后废弃了旧版 `AgentExecutor` 路径。
   * *解决*：安装 `langchain-classic` 兼容包，并重写导入路径，保证了 Agent 的平稳运行。
3. **SQLite 数据类型不匹配 (`IntegrityError`)**：
   * *原因*：自增主键强行插入字符串。
   * *解决*：利用 `cursor.lastrowid` 获取数据库自动生成的 ID，完美解决主键冲突。



## 🚀 快速启动
```bash
# 1. 克隆项目
git clone https://github.com/ChenYian1203/ai-ticket-agent.git
cd ai-ticket-agent

# 2. 安装依赖 (推荐使用清华源)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 配置环境变量
# 在根目录新建 .env 文件，填入你的 DeepSeek API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.deepseek.com/v1

# 4. 初始化数据库并运行
python database.py
streamlit run app.py
