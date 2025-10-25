# 使用示例

本文档提供自动化编译系统的详细使用示例。

## 场景1: 编译C/C++项目

### 示例: CMake项目

```bash
# 项目结构
my-cpp-project/
├── CMakeLists.txt
├── src/
│   ├── main.cpp
│   └── utils.cpp
└── include/
    └── utils.h

# 运行编译
python main.py /path/to/my-cpp-project
```

### 示例: Makefile项目

```bash
# 项目结构
my-c-project/
├── Makefile
├── main.c
└── lib.c

# 运行编译
python main.py /path/to/my-c-project
```

## 场景2: 编译Java项目

### 示例: Maven项目

```bash
# 项目结构
my-java-project/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── com/example/Main.java

# 运行编译
python main.py /path/to/my-java-project
```

### 示例: Gradle项目

```bash
# 项目结构
my-kotlin-project/
├── build.gradle
├── settings.gradle
└── src/
    └── main/
        └── kotlin/
            └── Main.kt

# 运行编译
python main.py /path/to/my-kotlin-project
```

## 场景3: 编译JavaScript/TypeScript项目

### 示例: npm项目

```bash
# 项目结构
my-node-project/
├── package.json
├── tsconfig.json
└── src/
    └── index.ts

# 运行编译
python main.py /path/to/my-node-project
```

## 场景4: 编译Rust项目

### 示例: Cargo项目

```bash
# 项目结构
my-rust-project/
├── Cargo.toml
└── src/
    └── main.rs

# 运行编译
python main.py /path/to/my-rust-project
```

## 场景5: 编译Go项目

### 示例: Go Modules项目

```bash
# 项目结构
my-go-project/
├── go.mod
├── go.sum
└── main.go

# 运行编译
python main.py /path/to/my-go-project
```

## 场景6: 编译Python项目

### 示例: setuptools项目

```bash
# 项目结构
my-python-project/
├── setup.py
├── requirements.txt
└── src/
    └── mypackage/
        └── __init__.py

# 运行编译/打包
python main.py /path/to/my-python-project
```

## 高级使用

### 使用调试模式

```bash
# 查看详细的执行过程
python main.py /path/to/project --log-level DEBUG
```

### 自定义重试次数

```bash
# 对于复杂项目，增加重试次数
python main.py /path/to/project --max-retry 10
```

### 使用自定义配置

```bash
# 使用不同的配置文件
python main.py /path/to/project --config my-config.json
```

### 批量编译

```bash
#!/bin/bash
# batch_compile.sh

projects=(
    "/path/to/project1"
    "/path/to/project2"
    "/path/to/project3"
)

for project in "${projects[@]}"; do
    echo "编译: $project"
    python main.py "$project"
    
    if [ $? -eq 0 ]; then
        echo "✅ $project 编译成功"
    else
        echo "❌ $project 编译失败"
    fi
    echo "---"
done
```

## CI/CD集成

### GitHub Actions

```yaml
name: Auto Compile

on: [push, pull_request]

jobs:
  compile:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install Auto Compiler
      run: |
        git clone https://github.com/your/auto-compiler.git
        cd auto-compiler
        pip install -r requirements.txt
    
    - name: Configure
      run: |
        echo '${{ secrets.CONFIG_JSON }}' > auto-compiler/config/config.json
    
    - name: Compile
      run: |
        cd auto-compiler
        python main.py ../
```

### GitLab CI

```yaml
compile:
  image: python:3.9
  
  before_script:
    - git clone https://github.com/your/auto-compiler.git
    - cd auto-compiler
    - pip install -r requirements.txt
    - echo "$CONFIG_JSON" > config/config.json
    - cd ..
  
  script:
    - python auto-compiler/main.py ./
  
  artifacts:
    paths:
      - build/
      - dist/
```

## 故障排查示例

### 查看日志

```bash
# 实时查看日志
tail -f auto_compiler.log

# 搜索错误
grep "ERROR" auto_compiler.log

# 查看最后的错误
grep "ERROR" auto_compiler.log | tail -n 20
```

### 手动干预

如果自动编译失败，可以查看日志了解问题，然后手动修复后重新运行：

```bash
# 1. 查看日志
cat auto_compiler.log

# 2. 根据日志手动修复问题
# 例如: 安装缺失的依赖
sudo apt-get install build-essential

# 3. 重新运行
python main.py /path/to/project
```

## 环境变量配置

可以通过环境变量配置API密钥：

```bash
# 设置环境变量
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxx"
export OPENAI_API_BASE="https://api.openai.com/v1"
export OPENAI_MODEL="gpt-4-turbo-preview"

# 运行（将使用环境变量中的配置）
python main.py /path/to/project
```

## 性能优化

### 减少API调用

```json
{
  "max_retry": 3,
  "timeout": 120
}
```

### 使用更快的模型

```json
{
  "model": "gpt-3.5-turbo"
}
```

## 最佳实践

1. **版本控制**: 在编译前确保代码已提交到git，以便出错时回滚
2. **备份**: 首次使用时建议先在测试项目上运行
3. **日志查看**: 遇到问题时及时查看日志文件
4. **API配额**: 注意API使用量，避免超出配额
5. **网络稳定**: 确保网络连接稳定

## 更多帮助

```bash
# 查看帮助信息
python main.py --help

# 查看版本信息
python main.py --version  # 如果实现了version参数
```
