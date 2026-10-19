from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from tools import get_order_status, create_refund_ticket

# 1. 加载环境变量（读取你的 DeepSeek Key）
load_dotenv()

# 2. 把咱们昨天写的纯 Python 函数，包装成 AI 能看懂的"工具"
# 注意：AI 是靠函数上面的注释（docstring）来理解这个工具是干嘛的，所以注释必须写清楚
@tool
def tool_get_order_status(order_id: str) -> str:
    """根据订单号查询订单状态。当你需要确认用户的订单是否存在时，调用此工具。"""
    return get_order_status(order_id)

@tool
def tool_create_refund_ticket(order_id: str, issue_description: str) -> str:
    """当用户需要退款，且你已经核实过订单后，调用此工具来创建退款工单。"""
    return create_refund_ticket(order_id, issue_description)

tools = [tool_get_order_status, tool_create_refund_ticket]

# 3. 初始化大模型（大脑）
llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0
)

# 4. 告诉 AI 它的角色和工作流程
prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业且严谨的电商售后客服 AI。
    你的工作流程是：
    1. 必须先从用户的话中提取出【订单号】和【问题描述】。
    2. 如果用户没说订单号，请礼貌地询问。
    3. 拿到订单号后，必须调用 `tool_get_order_status` 查询订单。
    4. 确认订单存在后，调用 `tool_create_refund_ticket` 帮用户创建退款工单。
    5. 绝对不要自己编造订单信息！
    """),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"), # 这是给 AI 自己思考用的占位符
])

# 5. 组装 AI 智能体（Agent）
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True) # verbose=True 可以看到 AI 的思考过程

# 6. 本地测试
if __name__ == "__main__":
    print("🤖 客服 AI 已上线！输入 '退出' 结束对话。")
    while True:
        user_input = input("\n👤 客户: ")
        if user_input == "退出":
            break
        
        # AI 开始干活
        response = agent_executor.invoke({"input": user_input})
        print(f"\n🤖 AI 客服: {response['output']}")