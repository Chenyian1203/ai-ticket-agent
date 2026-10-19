import sqlite3

def init_db():
    # 1. 连接数据库（如果文件不存在，会自动创建）
    conn = sqlite3.connect('ticket.db')
    cursor = conn.cursor()

    # 2. 创建订单表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            product_name TEXT,
            status TEXT,
            amount REAL
        )
    ''')

    # 3. 创建工单表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            issue_description TEXT,
            status TEXT
        )
    ''')

    # 4. 塞入两条测试数据（如果不存在才塞）
    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO orders VALUES ('10085', '小米 14', '已发货', 3999.0)")
        cursor.execute("INSERT INTO orders VALUES ('10086', 'iPhone 15', '已发货', 5999.0)")
        cursor.execute("INSERT INTO orders VALUES ('10087', 'MacBook Pro', '待发货', 12999.0)")
    
        conn.commit()
        print("✅ 测试订单数据已写入数据库")

    conn.close()
    print("✅ 数据库初始化完成！")

if __name__ == "__main__":
    init_db()