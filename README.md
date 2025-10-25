# 🤖 自动化编译系统

基于大语言模型（LLM）的智能自动化编译工具，能够自动分析项目结构、安装依赖、识别编译错误并自动修复。

## ✨ 核心特性

- **🔍 智能项目分析**: 自动识别项目类型、编程语言和构建系统
- **📦 自动依赖管理**: 智能下载和安装编译所需的依赖
- **🐛 错误自动修复**: 使用LLM分析编译错误并自动生成修复方案
- **🔄 迭代修复**: 支持多次尝试修复，直到编译成功
- **🌐 广泛支持**: 支持多种编程语言和构建系统
- **🎯 零配置**: 给定项目路径即可自动化完成全流程

## 🎬 快速开始

### 1. 安装依赖

```bash
cd auto-compiler
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `config/config.json` 文件，填入你的OpenAI API密钥：

```json
{
  "openai_api_key": "your-api-key-here",
  "openai_api_base": "https://api.openai.com/v1",
  "model": "gpt-4-turbo-preview",
  "max_retry": 5
}
```

> 💡 支持任何兼容OpenAI格式的API服务，如Azure OpenAI、OpenRouter等

### 3. 运行编译

#### 方式A: 直接运行（需要root权限）

```bash
# 以root用户运行
sudo python main.py /path/to/your/project

# 或切换到root
sudo su
python main.py /path/to/your/project
```

#### 方式B: Docker运行（推荐⭐）

```bash
docker run -it --rm \
  -v $(pwd)/auto-compiler:/app \
  -v /path/to/project:/project \
  -e OPENAI_API_KEY="your-api-key" \
  ubuntu:22.04 \
  bash -c "cd /app && pip3 install -r requirements.txt && python3 main.py /project"
```

> 💡 Docker方式最安全方便，详见 [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

## 📖 使用方法

### 基本用法

```bash
# 编译指定项目
python main.py /path/to/project

# 使用自定义配置文件
python main.py /path/to/project --config custom_config.json

# 显示详细日志
python main.py /path/to/project --log-level DEBUG

# 设置最大重试次数
python main.py /path/to/project --max-retry 10
```

### 命令行参数

- `project_path`: （必需）待编译项目的路径
- `-c, --config`: 配置文件路径（默认: config/config.json）
- `-l, --log-level`: 日志级别，可选 DEBUG/INFO/WARNING/ERROR（默认: INFO）
- `--max-retry`: 最大重试次数（默认: 5）

## 🏗️ 支持的构建系统

| 构建系统 | 语言 | 支持状态 |
|---------|------|---------|
| CMake | C/C++ | ✅ |
| Make | C/C++ | ✅ |
| Maven | Java | ✅ |
| Gradle | Java/Kotlin | ✅ |
| npm | JavaScript/TypeScript | ✅ |
| Cargo | Rust | ✅ |
| Go Modules | Go | ✅ |
| setuptools/pip | Python | ✅ |
| Poetry | Python | ✅ |
| Meson | C/C++ | ✅ |
| Bazel | 多语言 | ✅ |
| Autotools | C/C++ | ✅ |

## 🔧 工作原理

### 编译流程

```
┌─────────────────────┐
│   1. 项目分析       │  ← 识别项目类型和构建系统
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   2. 依赖安装       │  ← 自动下载和安装依赖
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   3. 尝试编译       │  ← 执行构建命令
└──────────┬──────────┘
           ↓
      [成功?]
       /   \
     是      否
      ↓       ↓
    完成   ┌─────────────────────┐
           │  4. 错误分析与修复  │  ← LLM分析错误并生成修复
           └──────────┬──────────┘
                      ↓
                  重新编译
                      ↓
                 [成功或达到重试上限]
```

### 核心模块

#### 1. 项目分析器 (`tools/project_analyzer.py`)

- 扫描项目文件结构
- 识别构建配置文件
- 检测编程语言
- 生成项目元信息

#### 2. 依赖管理器 (`tools/dependency_manager.py`)

- 根据构建系统自动安装依赖
- 支持 npm, pip, cargo, maven, gradle 等
- 处理依赖安装错误

#### 3. 错误处理器 (`tools/error_handler.py`)

- 解析编译错误输出
- 使用LLM分析错误原因
- 生成具体的修复方案
- 应用代码修改

#### 4. LLM客户端 (`src/llm_client.py`)

- 封装OpenAI API调用
- 支持工具调用（Function Calling）
- 支持流式响应

#### 5. 编译引擎 (`src/compiler_engine.py`)

- 协调各个模块
- 管理编译流程
- 记录编译历史

## 📝 配置说明

### config.json 配置项

```json
{
  "openai_api_key": "your-api-key",      // OpenAI API密钥
  "openai_api_base": "https://...",      // API端点
  "model": "gpt-4-turbo-preview",        // 使用的模型
  "max_retry": 5,                        // 最大重试次数
  "timeout": 300,                        // API超时时间（秒）
  "log_level": "INFO"                    // 日志级别
}
```

### 环境变量支持

也可以通过环境变量配置：

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://api.openai.com/v1"
export OPENAI_MODEL="gpt-4-turbo-preview"
```

## 🎯 使用场景

### 场景1: 编译开源项目

```bash
# 克隆一个开源项目
git clone https://github.com/example/project.git

# 自动编译
python main.py project/
```

### 场景2: CI/CD集成

```yaml
# .github/workflows/build.yml
- name: Auto Compile
  run: |
    python auto-compiler/main.py ./ --config ci-config.json
```

### 场景3: 批量编译

```bash
# 批量编译多个项目
for project in projects/*; do
  python main.py "$project"
done
```

## 🔬 高级特性

### 自定义工具函数

LLM使用Function Calling与工具交互，你可以扩展工具定义来增强能力：

```python
# 在相应的工具文件中添加新的工具定义
tools = [{
    "type": "function",
    "function": {
        "name": "your_custom_tool",
        "description": "工具描述",
        "parameters": {
            # 参数定义
        }
    }
}]
```

### 错误修复策略

系统使用以下策略修复编译错误：

1. **代码修改**: 修改源代码文件
2. **依赖安装**: 安装缺失的依赖包
3. **配置调整**: 修改构建配置文件
4. **环境设置**: 设置必要的环境变量

## 📊 日志文件

编译过程会生成详细的日志文件 `auto_compiler.log`，包含：

- 项目分析结果
- 依赖安装过程
- 编译命令执行
- 错误分析过程
- LLM交互记录
- 修复方案应用

## ⚠️ 注意事项

1. **API费用**: 使用LLM API会产生费用，建议设置合理的重试次数
2. **代码备份**: 系统会修改源代码，建议先备份或使用版本控制
3. **网络连接**: 需要稳定的网络连接访问LLM API
4. **权限要求**: 
   - 需要文件读写权限和执行构建工具的权限
   - **建议在root用户或具有足够权限的用户下运行**
   - 系统会自动安装缺失的构建工具和依赖（如cmake、make等）
5. **隐私安全**: 项目代码会发送给LLM服务，请注意隐私和安全
6. **自动安装**: 系统会自动执行包管理器命令（apt、yum等）安装依赖，不使用sudo前缀
7. **适合容器**: 特别适合在Docker等容器环境中使用，可以自动配置完整的编译环境

## 🐛 故障排查

### 问题: 无法连接API

```bash
# 检查网络连接
curl https://api.openai.com/v1/models

# 检查API密钥
export OPENAI_API_KEY="your-key"
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

### 问题: 编译失败

```bash
# 使用DEBUG日志级别查看详细信息
python main.py /path/to/project --log-level DEBUG

# 查看日志文件
tail -f auto_compiler.log
```

### 问题: 依赖安装失败

```bash
# 手动安装依赖后再运行
cd /path/to/project
npm install  # 或其他包管理器
cd -
python main.py /path/to/project
```

### 问题: sudo命令或包管理器锁定

系统会自动移除命令中的sudo前缀并执行。如遇到apt锁定错误：

```bash
# 等待其他进程完成
lsof /var/lib/dpkg/lock-frontend

# 或强制解锁（谨慎使用）
rm /var/lib/dpkg/lock-frontend
rm /var/lib/dpkg/lock

# 然后重新运行
python main.py /path/to/project
```

**注意**: 
- 系统会自动执行 `apt-get install`、`yum install` 等命令
- 不会添加 sudo 前缀
- 建议在root用户或Docker容器中运行
- 详见 `SECURITY_IMPROVEMENTS.md`

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置

```bash
git clone <repository-url>
cd auto-compiler
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果有开发依赖
```

### 代码风格

- 遵循PEP 8规范
- 使用type hints
- 添加详细的docstring

## 📜 许可证

GPL-3.0 License

## 🔗 相关资源

- [OpenAI API文档](https://platform.openai.com/docs)
- [Function Calling指南](https://platform.openai.com/docs/guides/function-calling)

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交Issue
- 发送邮件

---

**让编译变得简单，让LLM成为你的编译助手！** 🚀
