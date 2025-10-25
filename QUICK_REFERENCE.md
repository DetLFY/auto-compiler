# 快速参考指南

## 🚀 一分钟上手

```bash
# 1. 进入项目目录
cd auto-compiler

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置API密钥（编辑config/config.json）
{
  "openai_api_key": "your-api-key-here",
  "openai_api_base": "https://api.openai.com/v1",
  "model": "gpt-4-turbo-preview"
}

# 4. 运行（建议以root用户运行，或在Docker容器中）
python main.py /path/to/your/project
```

**重要**: 系统会自动安装缺失的构建工具（cmake、make等），建议在root用户或Docker容器中运行。

## 📋 常用命令

```bash
# 基本编译
python main.py /path/to/project

# 调试模式
python main.py /path/to/project --log-level DEBUG

# 增加重试次数
python main.py /path/to/project --max-retry 10

# 使用自定义配置
python main.py /path/to/project --config my-config.json

# 查看帮助
python main.py --help

# 运行测试
python test_system.py

# 查看日志
tail -f auto_compiler.log
```

## 🔧 配置速查

### 最小配置
```json
{
  "openai_api_key": "sk-...",
  "model": "gpt-4-turbo-preview"
}
```

### 完整配置
```json
{
  "openai_api_key": "sk-...",
  "openai_api_base": "https://api.openai.com/v1",
  "model": "gpt-4-turbo-preview",
  "max_retry": 5,
  "timeout": 300,
  "log_level": "INFO"
}
```

### 环境变量
```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_API_BASE="https://api.openai.com/v1"
export OPENAI_MODEL="gpt-4-turbo-preview"
```

## 🎯 支持的项目类型

| 类型 | 识别文件 | 构建命令 |
|------|---------|---------|
| C/C++ (CMake) | CMakeLists.txt | `mkdir build && cd build && cmake .. && make` |
| C/C++ (Make) | Makefile | `make` |
| Java (Maven) | pom.xml | `mvn clean package` |
| Java (Gradle) | build.gradle | `./gradlew build` |
| JavaScript | package.json | `npm install && npm run build` |
| Rust | Cargo.toml | `cargo build --release` |
| Go | go.mod | `go build` |
| Python | setup.py | `python setup.py build` |

## ⚡ 常见问题速查

### Q: 程序卡住不动？
**A**: 可能是包管理器被锁定。检查是否有其他apt/yum进程在运行。

### Q: apt锁定错误？
**A**: 
```bash
# 查看占用进程
lsof /var/lib/dpkg/lock-frontend
# 等待完成或终止进程后重试
```

### Q: 权限不足？
**A**: 建议以root用户运行或在Docker容器中运行。系统需要权限安装包。

### Q: API调用失败？
**A**: 检查网络和API密钥。确保config.json配置正确。

### Q: 编译失败？
**A**: 查看日志 `auto_compiler.log`。使用 `--log-level DEBUG` 获取详细信息。

### Q: 自动安装失败？
**A**: 检查网络连接和包管理器状态。可能需要先更新包列表（apt-get update）。

## 📊 日志级别说明

| 级别 | 用途 | 输出内容 |
|------|------|---------|
| DEBUG | 详细调试 | 所有执行细节、API调用、文件操作 |
| INFO | 正常使用 | 主要流程步骤、成功/失败信息 |
| WARNING | 警告信息 | 需要注意的问题、跳过的操作 |
| ERROR | 错误信息 | 严重错误、失败原因 |

## 🔒 安全提示

✅ **会做的**:
- 自动安装系统依赖（apt-get install、yum install等）
- 安装Python/Node.js包依赖
- 修改项目代码和配置
- 执行构建命令
- 读写日志文件

❌ **不会做的**:
- 使用sudo命令（假设当前用户已有足够权限）
- 修改项目外的系统文件
- 访问项目外的文件

⚠️ **权限要求**:
- 建议以root用户运行，或
- 在Docker容器中运行，或
- 确保当前用户有权限执行包管理器命令

## 📁 文件结构速查

```
auto-compiler/
├── config/config.json          ← 在这里配置API
├── src/compiler_engine.py      ← 核心编译逻辑
├── tools/                      ← 工具模块
│   ├── project_analyzer.py     ← 项目分析
│   ├── dependency_manager.py   ← 依赖管理
│   └── error_handler.py        ← 错误处理
├── main.py                     ← 运行这个！
├── auto_compiler.log           ← 查看这个了解详情
└── README.md                   ← 完整文档
```

## 🆘 紧急救援

```bash
# 1. 检查系统状态
python test_system.py

# 2. 查看最近错误
tail -n 50 auto_compiler.log | grep ERROR

# 3. 清理并重试
rm -f auto_compiler.log
python main.py /path/to/project --log-level DEBUG

# 4. 手动干预
cd /path/to/project
# 手动执行失败的命令
# 然后重新运行auto-compiler
```

## 📚 文档索引

- **README.md** - 完整项目文档
- **USAGE_EXAMPLES.md** - 详细使用示例
- **SECURITY_IMPROVEMENTS.md** - 安全性改进说明
- **PROJECT_OVERVIEW.md** - 项目架构文档
- **config/README.md** - 配置说明

## 💡 最佳实践

1. ✅ 使用前提交代码到git
2. ✅ 先在小项目上测试
3. ✅ 遇到问题查看日志
4. ✅ 手动安装系统依赖
5. ✅ 监控API使用量

## 🎓 学习路径

1. **新手**: 阅读 README.md → 运行 test_system.py → 尝试简单项目
2. **进阶**: 阅读 USAGE_EXAMPLES.md → 理解不同场景 → 自定义配置
3. **高级**: 阅读 PROJECT_OVERVIEW.md → 理解架构 → 扩展功能

## 📞 获取帮助

- 查看日志文件: `auto_compiler.log`
- 运行测试: `python test_system.py`
- 查看详细文档: `README.md`
- 理解安全机制: `SECURITY_IMPROVEMENTS.md`

---

**记住**: 这个工具会修改代码，使用前请备份！🔒
