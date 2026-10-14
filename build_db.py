"""把 words.json 的单词导入 SQLite：建表 + 插数据（可重复执行，已存在则跳过）。"""
import json
import sqlite3

DB_PATH = "vocab.db"
JSON_PATH = "words.json"


def create_table(conn):
    """建 words 表：单词基本信息 + 复习进度字段。"""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE NOT NULL,
            phonetic TEXT,
            meaning TEXT,
            example TEXT,
            example_cn TEXT,
            level INTEGER DEFAULT 0,        -- 0 不认识 / 1 模糊 / 2 认识
            review_count INTEGER DEFAULT 0  -- 复习过几次
        )
        """
    )


def main():
    with open(JSON_PATH, encoding="utf-8") as f:
        words = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    create_table(conn)

    inserted = 0
    for w in words:
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO words (word, phonetic, meaning, example, example_cn)
            VALUES (?, ?, ?, ?, ?)
            """,
            (w["word"], w["phonetic"], w["meaning"], w["example"], w["example_cn"]),
        )
        inserted += cur.rowcount

    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM words").fetchone()[0]
    print(f"新增 {inserted} 个词，词库共 {total} 个词")
    conn.close()


if __name__ == "__main__":
    main()
