"""AI 背单词 —— 命令行复习器。

功能：
  1) 复习：抽词 → 回忆 → 看答案 → 自评（认识/模糊/不认识）
  2) 测验：四选一，选出正确中文释义
  3) AI 讲解：调用智谱 GLM 生成释义/例句/助记

用法：
  python build_db.py   # 先初始化词库
  python app.py        # 再启动
  AI 讲解需要环境变量 ZHIPU_API_KEY（见 .env.example）
"""
import os
import random
import sqlite3

import requests
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "vocab.db"
GLM_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
GLM_MODEL = os.getenv("ZHIPU_MODEL", "glm-4-flash")


# ---------------- 数据库 ----------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_random_word(conn):
    return conn.execute("SELECT * FROM words ORDER BY RANDOM() LIMIT 1").fetchone()


def get_distractors(conn, word_id, n):
    """取 n 个其它词的释义，做选择题干扰项。"""
    return conn.execute(
        "SELECT meaning FROM words WHERE id != ? ORDER BY RANDOM() LIMIT ?",
        (word_id, n),
    ).fetchall()


def update_review(conn, word_id, level):
    conn.execute(
        "UPDATE words SET level = ?, review_count = review_count + 1 WHERE id = ?",
        (level, word_id),
    )
    conn.commit()


# ---------------- AI ----------------
def explain_word(word):
    """调用智谱 GLM，返回对该单词的中文讲解；未配置 key 时返回 None。"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        return None

    prompt = (
        f"请用中文讲解英语单词「{word}」，严格按下面格式输出三行：\n"
        f"释义：<一句话中文释义，标注词性>\n"
        f"例句：<一个英文例句>\n"
        f"助记：<一个记忆技巧或词根词缀拆解>"
    )
    resp = requests.post(
        GLM_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": GLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


# ---------------- 三种模式 ----------------
def review(conn):
    """复习模式：返回 False 表示用户要退出复习。"""
    word = get_random_word(conn)
    print(f"\n单词：{word['word']}   {word['phonetic'] or ''}")
    input("想一下它的意思，按回车看答案...")
    print(f"释义：{word['meaning']}")
    if word["example"]:
        print(f"例句：{word['example']}")
        print(f"      {word['example_cn']}")

    choice = input("\n自评：1=认识  2=模糊  3=不认识  q=退出复习  [默认2]: ").strip()
    if choice == "q":
        return False
    level = {"1": 2, "2": 1, "3": 0}.get(choice, 1)
    update_review(conn, word["id"], level)
    print("已记录。\n")
    return True


def quiz(conn):
    """测验模式：四选一。"""
    word = get_random_word(conn)
    distractors = get_distractors(conn, word["id"], 3)
    if len(distractors) < 3:
        print("词库太少，无法出四选一（至少需要 4 个词）。")
        return

    options = [word["meaning"]] + [d["meaning"] for d in distractors]
    random.shuffle(options)
    answer_idx = options.index(word["meaning"])

    print(f"\n单词：{word['word']}")
    for i, opt in enumerate(options):
        print(f"  {chr(65 + i)}. {opt}")
    choice = input("选一个字母：").strip().upper()

    if choice == chr(65 + answer_idx):
        print("✅ 正确！")
    else:
        print(f"❌ 错了，正确答案是 {chr(65 + answer_idx)}. {word['meaning']}")


def ai_explain(conn):
    """AI 讲解模式。"""
    word = input("\n输入要讲解的单词（留空则随机抽一个）：").strip()
    if not word:
        word = get_random_word(conn)["word"]
    print(f"正在让 AI 讲解「{word}」...\n")
    result = explain_word(word)
    if result is None:
        print("未检测到 ZHIPU_API_KEY。")
        print("获取 key：https://open.bigmodel.cn 注册后创建 API Key。")
        print("然后设置（Windows）：set ZHIPU_API_KEY=你的key  再重启本程序。")
        return
    print(result)


# ---------------- 主菜单 ----------------
def main():
    if not os.path.exists(DB_PATH):
        print("找不到 vocab.db，请先运行：python build_db.py")
        return

    conn = get_conn()
    while True:
        print("\n====== AI 背单词 ======")
        print("1. 复习")
        print("2. 测验")
        print("3. AI 讲解")
        print("0. 退出")
        choice = input("选择：").strip()

        if choice == "1":
            while review(conn):
                pass
        elif choice == "2":
            quiz(conn)
        elif choice == "3":
            ai_explain(conn)
        elif choice == "0":
            break
        else:
            print("无效输入")
    conn.close()
    print("再见！")


if __name__ == "__main__":
    main()
