# AI 背单词 📚

一个命令行背单词复习器：SQLite 存词库 + 三种复习模式 + 智谱 GLM 生成 AI 讲解。

## 功能

- **复习**：随机抽词 → 回忆 → 看答案 → 自评（认识/模糊/不认识），复习进度写回数据库
- **测验**：四选一选择题，从词库随机抽干扰项
- **AI 讲解**：调用智谱 GLM，一键生成释义 / 例句 / 助记

## 快速开始

```bash
pip install -r requirements.txt

# 1. 初始化词库（把 words.json 的 30 个词导入 SQLite）
python build_db.py

# 2. 启动
python app.py
```

## AI 讲解（可选）

1. 到 [智谱开放平台](https://open.bigmodel.cn) 注册并创建 API Key
2. 设置环境变量：
   - Windows CMD：`set ZHIPU_API_KEY=你的key`
   - 或复制 `.env.example` 为 `.env` 并填入 key（需要 `python-dotenv`，或自行 `os.getenv` 读取）
3. 重启 `app.py`，选 `3. AI 讲解`

不设置 key 也能正常使用「复习」和「测验」功能。

## 项目结构

```
ai-vocab/
├── words.json      # 词库数据源（30 个四级词）
├── build_db.py     # 初始化词库：json → SQLite
├── app.py          # 命令行复习器主程序
├── requirements.txt
├── .env.example    # 环境变量示例
└── vocab.db        # SQLite 数据库（首次运行生成，已 gitignore）
```

## 数据模型

`words` 表：

| 字段 | 说明 |
|---|---|
| word / phonetic / meaning / example / example_cn | 单词基本信息 |
| level | 掌握程度：0 不认识 / 1 模糊 / 2 认识 |
| review_count | 复习次数 |

## 技术栈

- Python 3 + sqlite3（标准库）
- requests（调用智谱 GLM API）
