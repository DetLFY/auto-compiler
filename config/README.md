# 配置文件示例

## 基础配置

最简单的配置：

```json
{
  "openai_api_key": "sk-xxxxxxxxxxxxxx",
  "model": "gpt-4-turbo-preview"
}
```

## 使用Azure OpenAI

```json
{
  "openai_api_key": "your-azure-api-key",
  "openai_api_base": "https://your-resource.openai.azure.com/openai/deployments/your-deployment",
  "model": "gpt-4",
  "max_retry": 5,
  "timeout": 300
}
```

## 使用其他兼容服务

```json
{
  "openai_api_key": "your-api-key",
  "openai_api_base": "https://api.groq.com/openai/v1",
  "model": "llama-3-70b",
  "max_retry": 3,
  "timeout": 120
}
```

## 完整配置

```json
{
  "openai_api_key": "your-api-key",
  "openai_api_base": "https://api.openai.com/v1",
  "model": "gpt-4-turbo-preview",
  "max_retry": 5,
  "timeout": 300,
  "log_level": "INFO"
}
```

## 配置项说明

- `openai_api_key`: （必需）API密钥
- `openai_api_base`: API基础URL，默认为OpenAI官方
- `model`: 使用的模型名称
- `max_retry`: 编译失败后的最大重试次数
- `timeout`: API请求超时时间（秒）
- `log_level`: 日志级别（DEBUG/INFO/WARNING/ERROR）
