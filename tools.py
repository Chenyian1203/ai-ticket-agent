import sqlite3
import random

def get_order_status(order_id: str) -> str:
    """
    工具一：根据订单号查询订单状态
    """
    conn = sqlite3.connect('ticket.db')
    cursor = conn.cursor()
    cursor.execute("SELECT product_name, status, amount FROM orders WHERE order_id = ?", (order_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        product, status, amount = result
        return f"订单号 {order_id} 查询成功：商品为 {product}，当前状态是【{status}】，金额 {amount} 元。"
    else:
        return f"未找到订单号为 {order_id} 的记录，请让用户核对订单号。"

def create_refund_ticket(order_id: str, issue_description: str) -> str:
    """
    工具二：创建退款工单
    """
    conn = sqlite3.connect('ticket.db')
    cursor = conn.cursor()
    # 注意这里：去掉了 ticket_id，只插入另外三个字段，让数据库自动生成 ID
    cursor.execute(
        "INSERT INTO tickets (order_id, issue_description, status) VALUES (?, ?, ?)",
        (order_id, issue_description, "待审核")
    )
    # 获取刚刚自动生成的工单号
    generated_ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return f"系统已成功创建退款工单，工单号为 TK-{generated_ticket_id}，关联订单 {order_id}，问题描述：{issue_description}。当前状态：待审核。"
# 这是本地测试代码，你可以自己改着玩
if __name__ == "__main__":
    print("【测试查订单】")
    print(get_order_status("10086"))
    print(get_order_status("99999"))
    
    print("\n【测试建工单】")
    print(create_refund_ticket("10086", "客户反馈屏幕碎裂"))

def get_all_pending_tickets() -> list:
    """获取所有待审核的工单"""
    conn = sqlite3.connect('ticket.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ticket_id, order_id, issue_description, status FROM tickets WHERE status = '待审核'")
    results = cursor.fetchall()
    conn.close()
    return results

def approve_ticket(ticket_id: int) -> str:
    """管理员审核通过工单，并更新订单状态"""
    conn = sqlite3.connect('ticket.db')
    cursor = conn.cursor()
    # 1. 更新工单状态为“已退款”
    cursor.execute("UPDATE tickets SET status = '已退款' WHERE ticket_id = ?", (ticket_id,))
    # 2. 顺便把对应的订单状态改成“已退款”
    cursor.execute("SELECT order_id FROM tickets WHERE ticket_id = ?", (ticket_id,))
    order = cursor.fetchone()
    if order:
        cursor.execute("UPDATE orders SET status = '已退款' WHERE order_id = ?", (order[0],))
    
    conn.commit()
    conn.close()
    return f"工单 {ticket_id} 已审核通过，款项已原路退回。"