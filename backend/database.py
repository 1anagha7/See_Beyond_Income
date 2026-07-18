import sqlite3
import os
import uuid
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "see_beyond_income.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        xp INTEGER DEFAULT 0,
        streak INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        total_savings REAL DEFAULT 0.0
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        date TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quests (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        category TEXT NOT NULL,
        target REAL NOT NULL,
        reduction_percentage REAL NOT NULL,
        duration INTEGER NOT NULL,
        reward TEXT NOT NULL,
        status TEXT NOT NULL, -- 'active', 'completed', 'failed'
        current_spend REAL DEFAULT 0.0,
        current_day INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        analysis TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learning_cards (
        id TEXT PRIMARY KEY,
        quest_id TEXT NOT NULL,
        product_name TEXT NOT NULL,
        subtitle TEXT,
        explainer TEXT,
        benefits TEXT, -- stored as JSON string
        unlocked INTEGER DEFAULT 0, -- 0 = locked, 1 = unlocked
        adopted INTEGER DEFAULT 0, -- 0 = no, 1 = yes
        FOREIGN KEY(quest_id) REFERENCES quests(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        channel TEXT DEFAULT 'whatsapp',
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    
    # Seed default user if not exists
    cursor.execute("SELECT * FROM users WHERE id = ?", ("user_123",))
    if not cursor.fetchone():
        # Default active user
        cursor.execute("""
            INSERT INTO users (id, name, xp, streak, level, total_savings)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("user_123", "Akshaya", 150, 3, 1, 1250.0))
        
        # Populate initial transactions matching frontend mock data
        initial_transactions = [
            ("tx_1", "user_123", 850.0, "Food & Dining", "Zomato Order", "2026-07-10"),
            ("tx_2", "user_123", 2400.0, "Food & Dining", "Dinner at Restaurant", "2026-07-11"),
            ("tx_3", "user_123", 1200.0, "Shopping", "Amazon Purchase", "2026-07-12"),
            ("tx_4", "user_123", 650.0, "Food & Dining", "Swiggy Grocery", "2026-07-13"),
            ("tx_5", "user_123", 300.0, "Transport", "Uber Ride", "2026-07-14"),
            ("tx_6", "user_123", 450.0, "Food & Dining", "Starbucks Coffee", "2026-07-15"),
            ("tx_7", "user_123", 799.0, "Utilities", "Mobile Bill", "2026-07-16")
        ]
        cursor.executemany("""
            INSERT INTO transactions (id, user_id, amount, category, description, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, initial_transactions)
        
        # Seed other customers for Bank Admin analytics
        other_users = [
            ("user_456", "Rahul Sharma", 2400, 12, 3, 4500.0),
            ("user_789", "Ananya Sen", 950, 5, 1, 2000.0),
            ("user_abc", "Vikram Malhotra", 3600, 21, 4, 8500.0)
        ]
        cursor.executemany("""
            INSERT INTO users (id, name, xp, streak, level, total_savings)
            VALUES (?, ?, ?, ?, ?, ?)
        """, other_users)
        
        # Seed historical completed/active quests for other users
        historical_quests = [
            ("q_1", "user_456", "Shopping", 4000.0, 20.0, 14, "SBI Recurring Deposit", "completed", 3500.0, 14, "2026-06-15", "Reducing electronics/apparel shopping run-rate."),
            ("q_2", "user_789", "Food & Dining", 2000.0, 15.0, 7, "SBI Savings Account Plus", "completed", 1850.0, 7, "2026-06-20", "Cutting down restaurant dinners."),
            ("q_3", "user_abc", "Travel", 5000.0, 25.0, 30, "SBI Mutual Fund SIP", "completed", 4200.0, 30, "2026-06-01", "Minimize premium cab spend."),
            ("q_4", "user_456", "Utilities", 3000.0, 10.0, 30, "SBI Life Insurance", "active", 1200.0, 10, "2026-07-08", "Control electricity & subs.")
        ]
        cursor.executemany("""
            INSERT INTO quests (id, user_id, category, target, reduction_percentage, duration, reward, status, current_spend, current_day, created_at, analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, historical_quests)
        
        # Seed matching learning cards and adoptions for conversion analytics
        learning_cards_init = [
            ("lc_1", "q_1", "SBI Recurring Deposit", "Guaranteed returns made easy", "Build wealth securely with regular monthly savings.", '["Interest rate up to 7.1%", "Flexible tenures", "Guaranteed returns"]', 1, 1),
            ("lc_2", "q_2", "SBI Savings Account Plus", "Earn more on your idle cash", "Sweeps surplus money into high-yield Fixed Deposits automatically.", '["Auto-sweep facility", "Earn higher interest", "Instant liquidity"]', 1, 0),
            ("lc_3", "q_3", "SBI Mutual Fund SIP", "Smart wealth creation in tiny steps", "Invest fixed sums into mutual funds automatically to beat inflation.", '["Compounding returns", "Start with ₹500", "Rupee cost averaging"]', 1, 1)
        ]
        cursor.executemany("""
            INSERT INTO learning_cards (id, quest_id, product_name, subtitle, explainer, benefits, unlocked, adopted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, learning_cards_init)
        
        # Seed WhatsApp messages log
        historical_notifications = [
            ("n_1", "user_456", "Hi Rahul! Keep going, you've saved ₹500 today towards your Recurring Deposit reward!", "2026-06-16 10:00:00", "whatsapp"),
            ("n_2", "user_abc", "Vikram, you are doing great on your SIP Quest. 15 days left!", "2026-06-15 14:30:00", "whatsapp")
        ]
        cursor.executemany("""
            INSERT INTO notifications (id, user_id, message, timestamp, channel)
            VALUES (?, ?, ?, ?, ?)
        """, historical_notifications)

    conn.commit()
    conn.close()

def get_user(user_id="user_123"):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

def update_user_gamification(user_id, xp_gain=0, streak_val=None, level_val=None, savings_gain=0.0):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current user values
    user = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return None
    
    new_xp = user["xp"] + xp_gain
    new_savings = user["total_savings"] + savings_gain
    
    # Calculate level dynamically based on XP if level_val is not supplied
    # Rule: Level = 1 + floor(XP / 1000)
    calculated_level = 1 + int(new_xp // 1000)
    new_level = level_val if level_val is not None else calculated_level
    
    new_streak = streak_val if streak_val is not None else user["streak"]
    
    cursor.execute("""
        UPDATE users
        SET xp = ?, streak = ?, level = ?, total_savings = ?
        WHERE id = ?
    """, (new_xp, new_streak, new_level, new_savings, user_id))
    
    conn.commit()
    conn.close()
    return {"xp": new_xp, "streak": new_streak, "level": new_level, "total_savings": new_savings}

def get_transactions(user_id="user_123"):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def set_transactions(user_id, txs):
    """
    Overwrites the transactions for a user (used to sync the table with user edits).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete current transactions
    cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
    
    # Insert new transactions
    tx_entries = []
    for tx in txs:
        tx_id = tx.get("id") or f"tx_{uuid.uuid4().hex[:8]}"
        tx_entries.append((
            tx_id,
            user_id,
            float(tx["amount"]),
            tx["category"],
            tx.get("description", ""),
            tx["date"]
        ))
        
    cursor.executemany("""
        INSERT INTO transactions (id, user_id, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, tx_entries)
    
    conn.commit()
    conn.close()
    return get_transactions(user_id)

def add_transaction(user_id, amount, category, description, date):
    conn = get_db_connection()
    cursor = conn.cursor()
    tx_id = f"tx_{uuid.uuid4().hex[:8]}"
    cursor.execute("""
        INSERT INTO transactions (id, user_id, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (tx_id, user_id, amount, category, description, date))
    conn.commit()
    conn.close()
    return tx_id

def delete_transaction(tx_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    conn.commit()
    conn.close()

def save_quest(user_id, quest_data, analysis):
    """
    Saves a quest generated by the Goal Agent. If an active quest already exists,
    it marks it as 'failed' or updates it before creating a new active quest.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Archive existing active quests as failed/abandoned
    cursor.execute("""
        UPDATE quests
        SET status = 'failed'
        WHERE user_id = ? AND status = 'active'
    """, (user_id,))
    
    quest_id = f"q_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO quests (id, user_id, category, target, reduction_percentage, duration, reward, status, current_spend, current_day, created_at, analysis)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        quest_id,
        user_id,
        quest_data["category"],
        float(quest_data["target"]),
        float(quest_data.get("reduction_percentage", 20)),
        int(quest_data["duration"]),
        quest_data["reward"],
        "active",
        0.0,
        0,
        created_at,
        analysis
    ))
    
    conn.commit()
    conn.close()
    return quest_id

def get_active_quest(user_id="user_123"):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM quests WHERE user_id = ? AND status = 'active'", (user_id,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_quest_progress(quest_id, current_spend, current_day, status="active"):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE quests
        SET current_spend = ?, current_day = ?, status = ?
        WHERE id = ?
    """, (current_spend, current_day, status, quest_id))
    
    conn.commit()
    conn.close()

def save_learning_card(quest_id, learning_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete existing to prevent duplicate key
    cursor.execute("DELETE FROM learning_cards WHERE quest_id = ?", (quest_id,))
    
    lc_id = f"lc_{uuid.uuid4().hex[:8]}"
    benefits_json = json.dumps(learning_data["benefits"])
    
    cursor.execute("""
        INSERT INTO learning_cards (id, quest_id, product_name, subtitle, explainer, benefits, unlocked, adopted)
        VALUES (?, ?, ?, ?, ?, ?, 1, 0)
    """, (
        lc_id,
        quest_id,
        learning_data["product_name"],
        learning_data["subtitle"],
        learning_data["explainer"],
        benefits_json
    ))
    
    conn.commit()
    conn.close()
    return lc_id

def get_learning_card(quest_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM learning_cards WHERE quest_id = ?", (quest_id,)).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["benefits"] = json.loads(d["benefits"])
        return d
    return None

def adopt_product(quest_id):
    """
    Mark product associated with a quest as adopted.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get quest to calculate savings / rewards
    quest = cursor.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
    if quest:
        cursor.execute("UPDATE learning_cards SET adopted = 1 WHERE quest_id = ?", (quest_id,))
        # Update quest status to completed (if it wasn't already)
        cursor.execute("UPDATE quests SET status = 'completed' WHERE id = ?", (quest_id,))
        # Add commission revenue / user savings
        savings = float(quest["target"])
        user_id = quest["user_id"]
        
        # Update user totals (award XP: 1000 for adopting, and add savings)
        cursor.execute("""
            UPDATE users
            SET xp = xp + 1000, total_savings = total_savings + ?
            WHERE id = ?
        """, (savings, user_id))
        
    conn.commit()
    conn.close()

def add_notification(user_id, message, channel="whatsapp"):
    conn = get_db_connection()
    cursor = conn.cursor()
    n_id = f"n_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO notifications (id, user_id, message, timestamp, channel)
        VALUES (?, ?, ?, ?, ?)
    """, (n_id, user_id, message, timestamp, channel))
    conn.commit()
    conn.close()
    return n_id

def get_notifications(user_id="user_123"):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT * FROM notifications 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 20
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_bank_metrics():
    """
    Computes summary metrics for the Bank Admin Analytics dashboard.
    """
    conn = get_db_connection()
    
    # 1. High level statistics
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_savings = conn.execute("SELECT SUM(total_savings) FROM users").fetchone()[0] or 0.0
    
    total_quests = conn.execute("SELECT COUNT(*) FROM quests").fetchone()[0]
    completed_quests = conn.execute("SELECT COUNT(*) FROM quests WHERE status = 'completed'").fetchone()[0]
    quest_success_rate = round((completed_quests / total_quests * 100), 1) if total_quests > 0 else 0.0
    
    # Calculate performance-based commission revenue
    # Pricing structure:
    # SIP: ₹500, RD: ₹300, Savings Plus: ₹200, Card ELITE: ₹1200, Life Insurance: ₹1500
    commission_rules = {
        "SBI Mutual Fund SIP": 500.0,
        "SBI Savings Account Plus": 200.0,
        "SBI Recurring Deposit": 300.0,
        "SBI Card ELITE": 1200.0,
        "SBI Life Insurance": 1500.0
    }
    
    adoptions_rows = conn.execute("""
        SELECT product_name, COUNT(*) as count 
        FROM learning_cards 
        WHERE adopted = 1 
        GROUP BY product_name
    """).fetchall()
    
    total_commission = 0.0
    product_adoptions = {}
    for row in adoptions_rows:
        prod = row["product_name"]
        count = row["count"]
        product_adoptions[prod] = count
        price = commission_rules.get(prod, 400.0) # default 400 if product mismatches
        total_commission += (price * count)
        
    # Get details for product adoption funnel
    # Funnel: Recommended (quest created) -> Explainer unlocked (learning_card unlocked) -> Adopted
    funnel_rows = conn.execute("""
        SELECT 
            q.reward as product,
            COUNT(q.id) as recommended,
            SUM(CASE WHEN lc.unlocked = 1 THEN 1 ELSE 0 END) as unlocked,
            SUM(CASE WHEN lc.adopted = 1 THEN 1 ELSE 0 END) as adopted
        FROM quests q
        LEFT JOIN learning_cards lc ON q.id = lc.quest_id
        GROUP BY q.reward
    """).fetchall()
    
    product_funnel = []
    for row in funnel_rows:
        product_funnel.append({
            "product": row["product"],
            "recommended": row["recommended"],
            "unlocked": row["unlocked"] or 0,
            "adopted": row["adopted"] or 0,
            "conversion": round((row["adopted"] or 0) / row["recommended"] * 100, 1) if row["recommended"] > 0 else 0.0
        })
        
    # Category distribution of quests
    category_rows = conn.execute("""
        SELECT category, COUNT(*) as count
        FROM quests
        GROUP BY category
    """).fetchall()
    category_distribution = {row["category"]: row["count"] for row in category_rows}
    
    conn.close()
    
    return {
        "total_users": total_users,
        "total_savings": round(total_savings, 2),
        "quest_success_rate": quest_success_rate,
        "total_commission": round(total_commission, 2),
        "product_funnel": product_funnel,
        "category_distribution": category_distribution
    }

def get_all_customers():
    conn = get_db_connection()
    users_rows = conn.execute("SELECT * FROM users ORDER BY xp DESC").fetchall()
    
    customers = []
    for u_row in users_rows:
        u_dict = dict(u_row)
        u_id = u_dict["id"]
        
        # Get active quest
        active_quest = conn.execute("SELECT * FROM quests WHERE user_id = ? AND status = 'active'", (u_id,)).fetchone()
        u_dict["active_quest"] = dict(active_quest) if active_quest else None
        
        # Get last notification
        last_notif = conn.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (u_id,)).fetchone()
        u_dict["last_notification"] = dict(last_notif) if last_notif else None
        
        customers.append(u_dict)
        
    conn.close()
    return customers

def reset_db():
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception as e:
            print(f"Error removing DB: {e}")
            # Alternate approach: clear tables
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute("DROP TABLE IF EXISTS transactions")
            cursor.execute("DROP TABLE IF EXISTS quests")
            cursor.execute("DROP TABLE IF EXISTS learning_cards")
            cursor.execute("DROP TABLE IF EXISTS notifications")
            conn.commit()
            conn.close()
    init_db()

# Initialize immediately
init_db()
