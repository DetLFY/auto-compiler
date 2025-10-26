# 更新日志

## v1.1.5 (2025-10-26)

### 🎯 核心重构
- 🔄 **重构 README 解析策略**（解决 libexpat CMake 误判问题）：
  - 根据项目结构**动态生成不同的 prompt**
  - 需要子目录时：强制要求命令以 `cd subdir &&` 开头
  - 根目录构建时：明确禁止添加任何 cd 命令
  
### 🛠️ 改进的验证机制
- ✅ **命令与结构一致性验证**：
  ```python
  # 如果检测到需要子目录
  if needs_subdir and 'cd subdir' not in build_cmd:
      # 自动添加 cd 命令
      build_cmd = f'cd {subdir_name} && {build_cmd}'
  
  # 如果不需要子目录，但命令包含 cd
  if not needs_subdir and 'cd test' in build_cmd:
      # 移除错误的 cd 命令
      build_cmd = remove_cd(build_cmd)
  ```

### 📋 问题分析
**libexpat v1.1.4 失败原因**：
```bash
# README 内容（包含多种构建方式）：
CMake 方式：cd expat && cmake ...
Autotools 方式：cd expat && ./buildconf.sh ...

# v1.1.4 的问题：
1. LLM 看到 "cmake" 关键字
2. Prompt 要求"优先使用根目录"（矛盾指令）
3. 生成：mkdir -p build && cd build && cmake .. && make
4. 但根目录没有 CMakeLists.txt → 失败

# v1.1.5 的解决：
1. 检测到 expat/ 子目录有构建文件
2. 使用"子目录 prompt"（强制要求 cd expat）
3. 生成：cd expat && mkdir -p build && cd build && cmake .. && make
4. 或者：cd expat && ./buildconf.sh && ./configure && make
```

### 🔍 Prompt 策略对比
**v1.1.4（单一 prompt，矛盾指令）**：
- ❌ "优先使用项目根目录的构建方式"
- ❌ "只有当项目结构信息明确建议cd到子目录时，才添加cd命令"
- 结果：LLM 困惑，选择错误

**v1.1.5（双 prompt 策略）**：
- ✅ **子目录 prompt**：
  - "命令必须以 cd {subdir_name} && 开头"
  - "README 中的命令都是在 {subdir_name}/ 下执行"
  - 清晰明确，无歧义
  
- ✅ **根目录 prompt**：
  - "在根目录直接构建，不要添加cd命令"
  - "不要进入测试/示例目录"
  - 简单直接

### 📊 泛化性增强
适用于多种项目结构：
1. **根目录构建**（cJSON）：直接生成根目录命令
2. **子目录构建**（libexpat）：强制添加 cd 命令
3. **多README项目**：分别解析不同层级的 README
4. **混合结构**：正确识别主构建目录

---

## v1.1.4 (2025-10-26)

### 🔧 关键修复
- 🐛 **修复子目录检测误判问题**（libexpat编译失败）：
  - 不再将 `configure.ac` 误判为实际的构建文件
  - 只检查实际的 `configure` 脚本（已生成的可执行文件）
  - 增加对 `buildconf.sh` 的检测（autotools项目的准备脚本）

### 问题分析
**libexpat项目的循环失败**：
```bash
# 问题根源：
根目录有 configure.ac（autoscan自动生成的）
→ v1.1.3误判为"根目录有构建文件"
→ 不检查expat/子目录
→ 在根目录执行 ./buildconf.sh（文件不存在）
→ LLM尝试autoreconf修复（在错误目录）
→ 循环20次失败

# 实际情况：
expat/buildconf.sh ← 实际的构建脚本在这里
expat/configure.ac ← 实际的配置文件在这里
```

### 修复逻辑
```python
# 旧逻辑（v1.1.3）：
root_has_configure = (project_path / 'configure').exists() or (project_path / 'configure.ac').exists()

# 新逻辑（v1.1.4）：
root_has_configure = (project_path / 'configure').exists()  # 只检查实际脚本
root_has_buildconf = (project_path / 'buildconf.sh').exists()  # 检查准备脚本
```

### 检测优先级
1. ✅ **实际的构建文件**：`configure`（可执行）、`buildconf.sh`、`CMakeLists.txt`、`Makefile`
2. ❌ **不作为判断依据**：`configure.ac`、`Makefile.am`（这些是源文件，不是实际构建文件）

---

## v1.1.3 (2025-10-26)

### 关键修复
- 🐛 **修复误入测试/fuzzing目录问题**：
  - 优先检查根目录是否有构建文件，如果有则直接使用根目录
  - 跳过test、tests、fuzzing、examples等非主要构建目录
  - 改进prompt，明确要求不要选择测试目录的构建命令
  
### 改进逻辑
- 📂 **智能构建目录选择**：
  ```
  1. 检查根目录是否有CMakeLists.txt/configure/Makefile
  2. 如果有 → 使用根目录，不检查子目录
  3. 如果没有 → 检查子目录，但跳过test/fuzzing/examples等
  ```

### 修复的问题
**cJSON项目问题**:
```bash
# v1.1.2: 错误地进入fuzzing目录
"cd fuzzing && mkdir -p build && cd build && cmake .. && make"
# 结果：没有实际的库文件产出

# v1.1.3: 正确使用根目录
"mkdir -p build && cd build && cmake .. && make"
# 结果：在根目录build/下生成libcjson.a等产物
```

### 跳过的目录
自动跳过以下类型的子目录：
- `test`, `tests`, `testing` - 测试目录
- `fuzzing` - 模糊测试目录
- `examples`, `samples` - 示例代码目录
- `docs`, `doc` - 文档目录

---

## v1.1.2 (2025-10-26)

### 关键改进
- 🔧 **改进命令清理逻辑**：
  - 修复了过于激进的冒号过滤问题，现在只过滤纯说明性的行
  - 保留合法的shell命令（即使包含冒号）
  - 白名单包括：cd, cmake, make, configure, autoreconf, gcc, python等常用命令
  
- 📂 **增强子目录检测**：
  - 新增主要构建目录智能识别（优先识别项目同名子目录）
  - 明确提示LLM需要添加cd命令
  - 检测buildconf.sh等autotools特有文件
  - 改进prompt，强调cd命令的重要性

### 修复的问题
**问题1**: 命令清理把合法命令也过滤了
```bash
# 之前：过滤掉所有包含冒号的行
# 现在：只过滤说明性行，保留命令行
```

**问题2**: libexpat类项目找不到构建文件
```bash
# 结构: libexpat/expat/configure.ac
# 之前：./configure  ← 错误：找不到configure
# 现在：cd expat && ./buildconf.sh && ./configure  ← 正确
```

### 示例
**libexpat项目**:
- ✅ 检测到 expat/ 子目录包含 Autotools
- ✅ 提示: "建议在构建命令前添加: cd expat &&"
- ✅ LLM生成: "cd expat && ./buildconf.sh && ./configure && make"

---

## v1.1.1 (2025-10-26)

### 关键Bug修复
- 🐛 **修复README解析导致的命令执行错误**：
  - 修复了LLM从README提取的构建命令包含中文注释和说明文字的问题
  - 添加了命令清理逻辑，自动过滤非可执行内容（中文、注释、标题等）
  - 改进了prompt，明确要求LLM只返回可执行的shell命令
  - 添加了子目录检测功能，支持libexpat类型的多层目录结构
  
### 改进
- 🔧 **增强命令清理**：
  - 自动移除包含中文字符的行
  - 自动移除包含冒号的说明性文本
  - 自动移除空行和无效命令
  - 用 `&&` 连接清理后的命令序列
  
- 📊 **改进子目录支持**：
  - 新增 `_check_build_subdirectories()` 方法检测子目录中的构建文件
  - 将子目录信息提供给LLM，帮助生成正确的cd命令
  - 支持 libexpat/expat/ 这种嵌套结构

### 示例
**之前的问题**:
```bash
# LLM返回包含中文的命令
"从Git克隆构建：\n./buildconf.sh\n./configure\n..."
# 导致执行失败：/bin/sh: 1: 从Git克隆构建：: not found
```

**现在的解决方案**:
```bash
# 自动清理为纯命令
"./buildconf.sh && ./configure && make"
# 或包含cd的命令
"cd expat && ./buildconf.sh && ./configure && make"
```

---

## v1.1 (2025-10-26)

### 新增功能
- ✨ **README解析功能**：系统现在能够自动解析项目的README文件，智能提取构建指令
  - 支持多种README格式：README.md, README.txt, README.rst等
  - 使用LLM从README中提取构建系统类型、构建命令、依赖项和编程语言
  - 优先使用README中的指令，提高编译成功率
  
### 改进
- 🐛 **修复无限循环问题**：修复了构建命令未更新导致的重复错误
  - 构建命令现在会在成功修复后持久化更新
  - `_attempt_build()` 方法现在会就地更新 `project_info` 字典
  - 错误处理器可以返回新的构建命令建议
  
- 🔧 **构建命令自动修正**：
  - 自动将 `mkdir build` 转换为 `mkdir -p build`，避免目录已存在错误
  - 修复常见的目录创建问题
  
- 📝 **增强日志记录**：
  - 更详细的编译历史记录
  - 改进的错误信息提示
  - 显示README解析状态

### 技术细节
- `ProjectAnalyzer.analyze_project()` 现在首先尝试解析README
- `ProjectAnalyzer._parse_readme()` 新方法用于提取README中的构建指令
- `ErrorHandler.analyze_and_fix()` 返回值改为字典，可包含新的构建命令
- `CompilerEngine._attempt_build()` 现在会更新并返回使用的构建命令
- `CompilerEngine._fix_build_errors()` 能够接收并应用LLM建议的新构建命令

---

## v1.0

### 首次发布
- 🎉 基础自动化编译功能
- 🔍 项目结构自动分析
- 📦 自动依赖安装
- 🛠️ 编译错误自动修复
- 🤖 LLM驱动的智能决策
- 🐧 支持多种构建系统（CMake, Make, Maven, Gradle, npm, Cargo等）
- 🔐 Root用户环境支持（无需sudo）
- 📊 详细的日志和错误报告
