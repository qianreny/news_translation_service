# 多语言翻译Flask服务

基于GPT-4o的多语言翻译服务，专门用于将简体中文新闻内容翻译成多种目标语言。

## 功能特性

- 🌍 支持5种目标语言翻译
- 📝 独立的翻译提示词模板
- 🔄 单个和批量翻译接口
- 🎯 可扩展的语言配置
- 📊 详细的翻译结果返回
- 🛡️ 完善的错误处理

## 支持的目标语言

| 语言代码 | 语言名称 | 语言代码(ISO) |
|---------|---------|---------------|
| `traditional_tw` | 繁体中文（台湾） | zh-TW |
| `traditional_hk` | 繁体中文（香港） | zh-HK |
| `vietnamese` | 越南语 | vi |
| `japanese` | 日语 | ja |
| `english` | 英语 | en |

## 项目结构

```
tranate_flask/
├── app.py                 # 主应用文件
├── config.py             # 配置管理
├── test_translation.py   # 测试脚本
├── requirements.txt      # 依赖包列表
├── .env.example         # 环境变量模板
└── README.md            # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
HOST=0.0.0.0
PORT=5000
```

### 3. 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

## API接口文档

### 1. 健康检查

**GET** `/health`

检查服务状态和支持的语言列表。

**响应示例：**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "supported_languages": ["traditional_tw", "traditional_hk", "vietnamese", "japanese", "english"]
}
```

### 2. 获取支持的语言

**GET** `/languages`

获取所有支持的目标语言详细信息。

**响应示例：**
```json
{
  "supported_languages": {
    "traditional_tw": {
      "name": "繁体中文（台湾）",
      "code": "zh-TW"
    },
    "english": {
      "name": "英语",
      "code": "en"
    }
  },
  "total_count": 5
}
```

### 3. 单语言翻译

**POST** `/translate`

将简体中文内容翻译成指定的目标语言。

**请求参数：**
```json
{
  "news_id": "新闻ID",
  "title": "新闻标题",
  "description": "新闻描述",
  "content": "新闻正文",
  "target_language": "目标语言代码"
}
```

**响应示例：**
```json
{
  "news_id": "news_001",
  "target_language": "traditional_tw",
  "language_name": "繁体中文（台湾）",
  "language_code": "zh-TW",
  "translated_title": "翻译后的标题",
  "translated_description": "翻译后的描述",
  "translated_content": "翻译后的正文",
  "original_title": "原始标题",
  "original_description": "原始描述",
  "original_content": "原始正文",
  "timestamp": "2024-01-01T12:00:00",
  "status": "success"
}
```

### 4. 批量翻译

**POST** `/translate/batch`

将简体中文内容批量翻译成多种目标语言。

**请求参数：**
```json
{
  "news_id": "新闻ID",
  "title": "新闻标题",
  "description": "新闻描述",
  "content": "新闻正文",
  "target_languages": ["traditional_tw", "english", "japanese"]
}
```

**响应示例：**
```json
{
  "news_id": "news_001",
  "total_translations": 3,
  "results": [
    {
      "target_language": "traditional_tw",
      "language_name": "繁体中文（台湾）",
      "translated_title": "翻译后的标题",
      "status": "success"
    }
  ],
  "timestamp": "2024-01-01T12:00:00",
  "status": "success"
}
```

## 测试

运行测试脚本：

```bash
python test_translation.py
```

测试脚本会自动测试所有API接口的功能。

## 扩展语言支持

要添加新的目标语言，需要在 `config.py` 的 `LanguageConfig` 类中添加新的语言配置：

1. 在 `get_target_languages()` 方法中添加新语言
2. 创建对应的提示词模板方法
3. 确保提示词包含 `{title}`、`{description}`、`{content}` 占位符

**示例：添加韩语支持**

```python
'korean': {
    'name': '韩语',
    'code': 'ko',
    'prompt_template': LanguageConfig._get_korean_prompt()
}
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥 | 必需 |
| `OPENAI_MODEL` | 使用的模型 | gpt-4o |
| `OPENAI_TEMPERATURE` | 温度参数 | 0.3 |
| `OPENAI_MAX_TOKENS` | 最大token数 | 4000 |
| `FLASK_DEBUG` | 调试模式 | True |
| `HOST` | 服务器地址 | 0.0.0.0 |
| `PORT` | 服务器端口 | 5000 |

### 翻译提示词模板

每种目标语言都有独立的提示词模板，包含：
- 翻译要求和规范
- 语言特色用词说明
- 输出格式要求
- 质量控制标准

## 错误处理

服务包含完善的错误处理机制：

- **400 Bad Request**: 请求参数错误
- **500 Internal Server Error**: 服务器内部错误
- 详细的错误信息返回
- 翻译失败时的降级处理

## 生产部署

### 使用Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 注意事项

1. **API密钥安全**: 确保OpenAI API密钥的安全，不要提交到版本控制
2. **请求限制**: 注意OpenAI API的调用限制和费用
3. **内容长度**: 超长内容可能需要分段处理
4. **并发控制**: 生产环境建议配置适当的并发限制

## 许可证

MIT License