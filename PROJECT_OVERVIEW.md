# 自动化编译项目 - 项目总览

## 📋 项目简介

这是一个基于大语言模型（LLM）的智能自动化编译工具，能够自动分析项目、安装依赖、识别并修复编译错误。

**创建时间**: 2025年10月25日

## 📁 项目结构

```
auto-compiler/
├── config/                    # 配置文件目录
│   ├── config.json           # 主配置文件（需要设置API密钥）
│   └── README.md             # 配置说明文档
│
├── src/                       # 核心源代码
│   ├── __init__.py           # 模块初始化
│   ├── compiler_engine.py    # 编译引擎（核心逻辑）
│   └── llm_client.py         # LLM客户端封装
│
├── tools/                     # 工具模块
│   ├── __init__.py           # 模块初始化
│   ├── project_analyzer.py   # 项目分析器
│   ├── dependency_manager.py # 依赖管理器
│   └── error_handler.py      # 错误处理器
│
├── main.py                    # 主程序入口
├── test_system.py            # 系统测试脚本
├── install.sh                # 安装脚本
├── examples.sh               # 使用示例脚本
├── requirements.txt          # Python依赖
├── README.md                 # 项目文档
├── USAGE_EXAMPLES.md         # 详细使用示例
└── .gitignore               # Git忽略文件

```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd auto-compiler
./install.sh
```

或手动安装：

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `config/config.json`：

```json
{
  "openai_api_key": "your-actual-api-key",
  "openai_api_base": "https://api.openai.com/v1",
  "model": "gpt-4-turbo-preview",
  "max_retry": 5
}
```

### 3. 运行测试

```bash
python test_system.py
```

### 4. 开始使用

```bash
python main.py /path/to/your/project
```

## 🔧 核心功能

### 1. 项目分析器 (project_analyzer.py)

**功能**:
- 自动识别项目类型（C/C++, Java, Python, Rust, Go等）
- 检测构建系统（CMake, Make, Maven, Gradle, npm, Cargo等）
- 扫描项目文件结构
- 使用LLM进行深度分析

**支持的构建系统**:
- CMake, Make, Meson, Autotools (C/C++)
- Maven, Gradle (Java)
- npm (JavaScript/TypeScript)
- Cargo (Rust)
- Go Modules (Go)
- pip, Poetry (Python)
- Bazel (多语言)

### 2. 依赖管理器 (dependency_manager.py)

**功能**:
- 自动安装项目依赖
- 支持多种包管理器（npm, pip, cargo, maven等）
- 处理依赖安装错误
- 使用LLM修复依赖问题

### 3. 错误处理器 (error_handler.py)

**功能**:
- 解析编译错误输出
- 提取关键错误信息
- 使用LLM分析错误原因
- 自动生成修复方案
- 应用代码修改

**支持的错误类型**:
- 语法错误
- 依赖缺失
- 配置错误
- 链接错误
- 类型错误

### 4. LLM客户端 (llm_client.py)

**功能**:
- 封装OpenAI API调用
- 支持Function Calling
- 支持流式响应
- 兼容多种OpenAI格式的API服务

### 5. 编译引擎 (compiler_engine.py)

**功能**:
- 协调各个模块
- 管理编译流程
- 记录编译历史
- 迭代修复错误

## 💡 工作流程

1. **分析阶段**: 扫描项目文件，识别构建系统和语言
2. **依赖阶段**: 自动安装所需依赖
3. **编译阶段**: 执行构建命令
4. **修复阶段**: 如果失败，使用LLM分析并修复错误
5. **迭代阶段**: 重复3-4步，直到成功或达到最大重试次数

## 🎯 使用场景

1. **开源项目编译**: 快速编译下载的开源项目
2. **CI/CD集成**: 集成到持续集成流程中
3. **批量编译**: 批量编译多个项目
4. **教学演示**: 用于教学和演示编译过程
5. **错误诊断**: 自动诊断和修复编译问题

## 🔑 关键技术

- **Python 3.x**: 主要开发语言
- **OpenAI API**: LLM能力支持
- **Function Calling**: 工具调用机制
- **正则表达式**: 错误信息解析
- **subprocess**: 执行编译命令
- **pathlib**: 文件路径处理

## ⚙️ 配置选项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| openai_api_key | OpenAI API密钥 | 必需 |
| openai_api_base | API端点URL | https://api.openai.com/v1 |
| model | 使用的模型 | gpt-4-turbo-preview |
| max_retry | 最大重试次数 | 5 |
| timeout | API超时时间（秒） | 300 |
| log_level | 日志级别 | INFO |

## 📊 性能说明

- **小型项目** (< 100个文件): 通常3-5分钟完成
- **中型项目** (100-1000个文件): 通常5-15分钟完成
- **大型项目** (> 1000个文件): 根据复杂度15分钟以上

实际时间取决于：
- 项目复杂度
- 依赖数量
- 网络速度
- LLM响应速度
- 错误数量

## ⚠️ 注意事项

1. **API费用**: 使用LLM API会产生费用
2. **代码安全**: 代码会发送到LLM服务，注意隐私
3. **代码备份**: 系统会修改代码，建议使用版本控制
4. **网络连接**: 需要稳定的网络连接
5. **权限要求**: 需要文件读写和执行权限

## 🐛 常见问题

### Q: 如何使用其他LLM服务？

A: 修改 `config.json` 中的 `openai_api_base`，指向兼容OpenAI API的服务端点。

### Q: 编译失败怎么办？

A: 查看 `auto_compiler.log` 日志文件，了解详细错误信息。可以增加 `--log-level DEBUG` 查看更多细节。

### Q: 如何减少API费用？

A: 降低 `max_retry` 值，或使用更便宜的模型如 `gpt-3.5-turbo`。

### Q: 支持哪些编程语言？

A: 主要支持 C/C++, Java, JavaScript/TypeScript, Python, Rust, Go, Kotlin, Scala 等主流语言。

### Q: 可以离线使用吗？

A: 不可以，需要联网访问LLM API。

## 📚 扩展性

系统采用模块化设计，易于扩展：

1. **添加新的构建系统**: 在 `project_analyzer.py` 中添加识别规则
2. **添加新的包管理器**: 在 `dependency_manager.py` 中添加安装方法
3. **自定义错误处理**: 在 `error_handler.py` 中添加错误模式
4. **自定义LLM交互**: 修改 `llm_client.py` 的工具定义

## 🔄 未来改进

- [ ] 支持本地LLM模型
- [ ] 添加Web界面
- [ ] 支持更多构建系统
- [ ] 优化错误识别算法
- [ ] 添加编译缓存机制
- [ ] 支持并行编译
- [ ] 添加详细的编译报告
- [ ] 支持MCP (Model Context Protocol)

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**让编译更智能，让LLM成为你的编译助手！** 🚀
