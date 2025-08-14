import sqlite3


def get_db_connection():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn


def add_notification(username, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            seen INTEGER DEFAULT 0
        )
    """
    )
    cursor.execute(
        "INSERT INTO notifications (username, message) VALUES (?, ?)",
        (username, message),
    )
    conn.commit()
    conn.close()


def get_notifications(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, message FROM notifications WHERE username = ? AND seen = 0",
        (username,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def mark_notifications_seen(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET seen = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()


def create_private_message_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS private_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            seen INTEGER DEFAULT 0
        )
    """
    )
    conn.commit()
    conn.close()


def send_private_message(sender, receiver, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO private_messages (sender, receiver, message) VALUES (?, ?, ?)",
        (sender, receiver, message),
    )
    conn.commit()
    conn.close()


def get_private_messages(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT sender, message, timestamp FROM private_messages
        WHERE receiver = ? ORDER BY timestamp DESC
    """,
        (username,),

ALTER TABLE private_messages ADD COLUMN file_name TEXT;
ALTER TABLE private_messages ADD COLUMN file_data BLOB;
ALTER TABLE private_messages ADD COLUMN thread_id INTEGER;
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_unseen_message_count(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM private_messages WHERE receiver = ? AND seen = 0",
        (username,),
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count


def mark_messages_seen(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE private_messages SET seen = 1 WHERE receiver = ?", (username,)
    )
    conn.commit()
    conn.close()


def get_message_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM private_messages")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT thread_id) FROM private_messages")
    threads = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM private_messages WHERE file_name IS NOT NULL")
    attachments = cursor.fetchone()[0]

    cursor.execute("""
        SELECT users.role, COUNT(*) FROM private_messages
        JOIN users ON private_messages.sender = users.username
        GROUP BY users.role
    """)
    by_role = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()
    return {"total": total, "threads": threads, "attachments": attachments, "by_role": by_role}