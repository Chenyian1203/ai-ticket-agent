import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from tools import get_order_status, create_refund_ticket, get_all_pending_tickets, approve_ticket

# 加载环境变量
load_dotenv()

# ==================== 1. 组装企业级 Agent ====================
@tool
def tool_get_order_status(order_id: str) -> str:
    """根据订单号查询订单状态。当你需要确认用户的订单是否存在时，调用此工具。"""
    return get_order_status(order_id)

@tool
def tool_create_refund_ticket(order_id: str, issue_description: str) -> str:
    """当用户需要退款，且你已经核实过订单后，调用此工具来创建退款工单。"""
    return create_refund_ticket(order_id, issue_description)

tools = [tool_get_order_status, tool_create_refund_ticket]
llm = ChatOpenAI(model="deepseek-chat", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业且严谨的电商售后客服 AI。
    你的工作流程是：
    1. 必须先从用户的话中提取出【订单号】和【问题描述】。
    2. 如果用户没说订单号，请礼貌地询问。
    3. 拿到订单号后，必须调用 `tool_get_order_status` 查询订单。
    4. 确认订单存在后，调用 `tool_create_refund_ticket` 帮用户创建退款工单。
    5. 绝对不要自己编造订单信息！回答要简短、专业、有温度。
    """),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

# ==================== 2. 页面基础配置 & 淘宝大厂级 UI ====================
st.set_page_config(page_title="智能售后客服中心", page_icon="🛒", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    header {visibility: hidden;}
    
    /* 全局背景：极度干净的浅灰色，让白色卡片凸显出来 */
    .stApp {
        background-color: #F5F6F8;
    }

    /* 顶部导航栏：大厂白底 + 品牌色 Logo */
    .top-bar {
        background-color: #FFFFFF;
        padding: 1rem 2rem;
        border-bottom: 1px solid #EBEBEB;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #333;
        border-radius: 0 0 12px 12px;
        margin-top: -4rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    }
    .logo { 
        font-weight: 800; 
        font-size: 1.3rem; 
        display: flex; 
        gap: 10px; 
        align-items: center; 
        /* 淘宝/拼多多经典的渐变红橙色 */
        background: -webkit-linear-gradient(45deg, #FF5000, #FF8C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 管理员后台卡片：清爽的绿色警示色 */
    .admin-card {
        background-color: #FFFFFF;
        border-left: 6px solid #00B578;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        border-top: 1px solid #EBEBEB;
        border-right: 1px solid #EBEBEB;
        border-bottom: 1px solid #EBEBEB;
    }

    /* 聊天卡片：丝滑圆角 */
    .chat-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        color: #333;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        border: 1px solid #F0F0F0;
    }
    
    /* 客户气泡：品牌橙色边框点缀 */
    .user-card { border-right: 4px solid #FF5000; }
    
    /* AI 气泡：专业蓝色边框点缀 */
    .ai-card { border-left: 4px solid #1677FF; }

    /* 强行干掉输入框的丑陋黑底，改成高级白框 */
    [data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 24px !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05) !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #333 !important;
    }
</style>
""", unsafe_allow_html=True)

# 顶部假导航
st.markdown("""
<div class="top-bar">
    <div class="logo">🛒 智能售后客服中心</div>
    <div style="color: #999; font-size: 0.9rem; font-weight: 500;">Enterprise AI Platform</div>
</div>
""", unsafe_allow_html=True)

# ==================== 3. 管理员审核工作台 ====================
st.markdown('<div class="admin-card">', unsafe_allow_html=True)
st.markdown("<h3 style='color: #333; margin-top: 0; font-weight: bold;'>🧑‍💼 主管审核面板</h3>", unsafe_allow_html=True)
st.markdown("<p style='color: #888; font-size: 0.9rem;'>AI 客服创建退款单后，主管在此一键审核。</p>", unsafe_allow_html=True)

try:
    pending_tickets = get_all_pending_tickets()
    if not pending_tickets:
        st.success("✅ 当前没有待审核的工单，系统运行平稳。")
    else:
        for t in pending_tickets:
            ticket_id, order_id, issue, status = t
            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.info(f"📦 **待审核工单：** TK-{ticket_id} | **订单号：** {order_id} | **原因：** {issue}")
            with col_btn:
                # 使用自定义的淘宝橙色按钮
                if st.button(f"同意退款", key=f"btn_{ticket_id}"):
                    result = approve_ticket(ticket_id)
                    st.toast(f"🎉 {result}")
                    st.rerun()
except Exception as e:
    st.error(f"读取工单失败，请检查 tools.py: {e}")
st.markdown('</div>', unsafe_allow_html=True)

# ==================== 4. 聊天主界面 ====================
st.markdown("<h3 style='color: #333; font-weight: bold; margin-top: 2rem;'>💬 在线客服咨询</h3>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "亲，您好！我是您的专属智能售后客服。请问有什么可以帮您？如果您要申请退款，请提供订单号。"}]

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-card user-card"><strong style="color: #FF5000;">👤 客户：</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-card ai-card"><strong style="color: #1677FF;">🤖 AI 客服：</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)

if user_input := st.chat_input("请描述您遇到的问题..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f'<div class="chat-card user-card"><strong style="color: #FF5000;">👤 客户：</strong><br>{user_input}</div>', unsafe_allow_html=True)

    with st.spinner("AI 正在为您核实订单..."):
        try:
            response = agent_executor.invoke({"input": user_input})
            answer = response['output']
            st.markdown(f'<div class="chat-card ai-card"><strong style="color: #1677FF;">🤖 AI 客服：</strong><br>{answer}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"系统繁忙，请稍后再试。错误信息：{e}")