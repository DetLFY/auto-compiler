# Docker 使用指南

本文档说明如何在Docker容器中使用自动化编译系统，这是推荐的使用方式。

## 🐳 为什么使用Docker

1. **完整权限**: 容器内以root运行，可以自动安装任何依赖
2. **环境隔离**: 不影响宿主机系统
3. **可重复性**: 确保编译环境一致
4. **安全性**: 限制在容器内，不会影响宿主机

## 📦 快速开始

### 方式1: 使用官方镜像（推荐）

```bash
# 拉取镜像
docker pull ubuntu:22.04

# 运行容器并挂载项目
docker run -it --rm \
  -v /path/to/auto-compiler:/auto-compiler \
  -v /path/to/project:/project \
  -e OPENAI_API_KEY="your-api-key" \
  ubuntu:22.04 \
  bash

# 在容器内
cd /auto-compiler
pip install -r requirements.txt
python main.py /project
```

### 方式2: 创建Dockerfile

创建 `Dockerfile`:

```dockerfile
FROM ubuntu:22.04

# 安装Python和基础工具
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制auto-compiler
COPY . /auto-compiler
WORKDIR /auto-compiler

# 安装Python依赖
RUN pip3 install -r requirements.txt

# 设置入口点
ENTRYPOINT ["python3", "main.py"]
```

构建并使用:

```bash
# 构建镜像
docker build -t auto-compiler .

# 运行
docker run -it --rm \
  -v /path/to/project:/project \
  -e OPENAI_API_KEY="your-api-key" \
  auto-compiler /project
```

## 🔧 完整示例

### 示例1: 编译C++项目

```bash
# 启动容器
docker run -it --rm \
  -v $(pwd)/auto-compiler:/app \
  -v $(pwd)/my-cpp-project:/project \
  -e OPENAI_API_KEY="sk-xxxxx" \
  ubuntu:22.04 bash

# 在容器内
cd /app
pip3 install -r requirements.txt

# 编译项目（会自动安装cmake、make、gcc等）
python3 main.py /project
```

### 示例2: 使用docker-compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  auto-compiler:
    image: ubuntu:22.04
    volumes:
      - ./auto-compiler:/auto-compiler
      - ./projects:/projects
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    working_dir: /auto-compiler
    command: >
      bash -c "
        apt-get update &&
        apt-get install -y python3 python3-pip &&
        pip3 install -r requirements.txt &&
        python3 main.py /projects/my-project
      "
```

使用:

```bash
# 设置API密钥
export OPENAI_API_KEY="your-api-key"

# 运行
docker-compose up
```

## 🎯 推荐配置

### 基础镜像选择

| 镜像 | 适用场景 | 特点 |
|------|---------|------|
| ubuntu:22.04 | 通用C/C++项目 | 包管理器apt，支持最多 |
| debian:bullseye | 稳定性要求高 | 更稳定，包更保守 |
| centos:8 | RHEL系项目 | 使用yum/dnf |
| alpine:latest | 资源受限 | 体积小，但兼容性差 |

### 资源限制

```bash
docker run -it --rm \
  --memory="4g" \
  --cpus="2" \
  -v $(pwd):/workspace \
  ubuntu:22.04 bash
```

### 网络配置

```bash
# 如果需要访问宿主机服务
docker run -it --rm \
  --network host \
  -v $(pwd):/workspace \
  ubuntu:22.04 bash
```

## 📝 最佳实践

### 1. 使用配置文件挂载

```bash
docker run -it --rm \
  -v $(pwd)/auto-compiler:/app \
  -v $(pwd)/config.json:/app/config/config.json:ro \
  -v $(pwd)/project:/project \
  ubuntu:22.04 bash
```

### 2. 持久化日志

```bash
docker run -it --rm \
  -v $(pwd)/auto-compiler:/app \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/project:/project \
  ubuntu:22.04 bash

# 在容器内日志会保存到 /app/logs
```

### 3. 多项目批量编译

```bash
#!/bin/bash
# batch-compile.sh

PROJECTS=(
  "/projects/project1"
  "/projects/project2"
  "/projects/project3"
)

for project in "${PROJECTS[@]}"; do
  echo "编译: $project"
  docker run --rm \
    -v $(pwd)/auto-compiler:/app \
    -v $project:$project \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    ubuntu:22.04 \
    bash -c "
      cd /app &&
      pip3 install -q -r requirements.txt &&
      python3 main.py $project
    "
done
```

## 🔐 安全建议

### 1. 最小权限原则

虽然在容器内以root运行，但仍应限制容器权限：

```bash
docker run -it --rm \
  --security-opt=no-new-privileges \
  --cap-drop=ALL \
  --cap-add=CHOWN,SETUID,SETGID \
  -v $(pwd):/workspace \
  ubuntu:22.04 bash
```

### 2. 只读挂载

将auto-compiler目录设为只读：

```bash
docker run -it --rm \
  -v $(pwd)/auto-compiler:/app:ro \
  -v $(pwd)/project:/project \
  ubuntu:22.04 bash
```

### 3. 环境变量隔离

使用env文件：

```bash
# .env
OPENAI_API_KEY=sk-xxxxx
OPENAI_API_BASE=https://api.openai.com/v1

# 使用
docker run -it --rm \
  --env-file .env \
  -v $(pwd):/workspace \
  ubuntu:22.04 bash
```

## 🚀 CI/CD集成

### GitHub Actions

```yaml
name: Auto Compile

on: [push]

jobs:
  compile:
    runs-on: ubuntu-latest
    container:
      image: ubuntu:22.04
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup auto-compiler
      run: |
        apt-get update
        apt-get install -y python3 python3-pip
        cd auto-compiler
        pip3 install -r requirements.txt
    
    - name: Compile project
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        cd auto-compiler
        python3 main.py ../project
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: build-output
        path: project/build/
```

### GitLab CI

```yaml
compile:
  image: ubuntu:22.04
  
  before_script:
    - apt-get update
    - apt-get install -y python3 python3-pip
    - cd auto-compiler
    - pip3 install -r requirements.txt
  
  script:
    - python3 main.py ../project
  
  artifacts:
    paths:
      - project/build/
```

## 📊 性能优化

### 1. 缓存层

创建带缓存的Dockerfile:

```dockerfile
FROM ubuntu:22.04

# 缓存apt包列表
RUN apt-get update

# 缓存常用工具
RUN apt-get install -y \
    python3 python3-pip \
    build-essential cmake \
    git curl wget

# 缓存Python包
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# 复制代码
COPY . /auto-compiler
WORKDIR /auto-compiler
```

### 2. 使用本地缓存

```bash
# 使用宿主机的pip缓存
docker run -it --rm \
  -v $(pwd):/workspace \
  -v ~/.cache/pip:/root/.cache/pip \
  ubuntu:22.04 bash
```

## 🐛 故障排查

### 问题1: 容器内网络不通

```bash
# 测试网络
docker run --rm ubuntu:22.04 \
  bash -c "apt-get update && apt-get install -y curl && curl -I https://api.openai.com"

# 使用宿主机网络
docker run --network host ...
```

### 问题2: 权限问题

```bash
# 确保以root运行
docker run --user root ...

# 检查挂载目录权限
ls -la /path/to/mount
```

### 问题3: 资源不足

```bash
# 增加内存和CPU
docker run \
  --memory="8g" \
  --cpus="4" \
  ...
```

## 📚 相关资源

- [Docker官方文档](https://docs.docker.com/)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [Dockerfile最佳实践](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

---

**推荐**: 在Docker容器中使用本系统可以获得最佳体验，无需担心权限和环境问题！🐳
