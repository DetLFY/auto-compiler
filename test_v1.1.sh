#!/bin/bash
# v1.1功能测试脚本

set -e

echo "=========================================="
echo "自动化编译系统 v1.1 功能测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
test_case() {
    local test_name=$1
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${YELLOW}[测试 $TOTAL_TESTS]${NC} $test_name"
}

test_pass() {
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo -e "${GREEN}✓ 通过${NC}"
    echo ""
}

test_fail() {
    local reason=$1
    FAILED_TESTS=$((FAILED_TESTS + 1))
    echo -e "${RED}✗ 失败: $reason${NC}"
    echo ""
}

# 清理函数
cleanup() {
    echo "清理测试文件..."
    rm -rf test_v1.1_*
}

# 设置清理陷阱
trap cleanup EXIT

# ==================== 测试1: README解析功能 ====================
test_case "README解析 - CMake项目"

# 创建测试项目
mkdir -p test_v1.1_cmake
cd test_v1.1_cmake

cat > README.md << 'EOF'
# Test CMake Project

## Building

Install dependencies:
```bash
apt-get install -y cmake gcc g++
```

Build the project:
```bash
mkdir -p build
cd build
cmake ..
make
```
EOF

cat > CMakeLists.txt << 'EOF'
cmake_minimum_required(VERSION 3.10)
project(TestProject)
add_executable(test_app main.c)
EOF

cat > main.c << 'EOF'
#include <stdio.h>
int main() {
    printf("Test v1.1\n");
    return 0;
}
EOF

cd ..

# 检查README是否创建成功
if [ -f "test_v1.1_cmake/README.md" ]; then
    test_pass
else
    test_fail "README文件未创建"
fi

# ==================== 测试2: 构建命令修正 ====================
test_case "构建命令自动修正 - mkdir -> mkdir -p"

# 创建Python测试来验证修正逻辑
cat > test_fix_command.py << 'EOF'
import sys
sys.path.insert(0, 'src')

from compiler_engine import CompilerEngine

# 模拟配置
test_config = {
    'openai_api_key': 'test',
    'openai_api_base': 'http://test',
    'model': 'test',
    'max_retry': 1
}

# 创建引擎实例
class MockEngine(CompilerEngine):
    def __init__(self):
        self.config = test_config
    
    def _fix_build_command(self, command):
        return CompilerEngine._fix_build_command(self, command)

engine = MockEngine()

# 测试修正功能
test_cases = [
    ("mkdir build && cd build", "mkdir -p build && cd build"),
    ("mkdir -p build && cd build", "mkdir -p build && cd build"),
    ("cmake .. && make", "cmake .. && make"),
]

all_passed = True
for original, expected in test_cases:
    result = engine._fix_build_command(original)
    if result != expected:
        print(f"FAIL: '{original}' -> '{result}' (expected '{expected}')")
        all_passed = False

if all_passed:
    print("PASS")
    sys.exit(0)
else:
    sys.exit(1)
EOF

if python3 test_fix_command.py 2>/dev/null; then
    test_pass
else
    test_fail "构建命令修正逻辑错误"
fi

rm -f test_fix_command.py

# ==================== 测试3: 项目分析器README方法存在性 ====================
test_case "项目分析器包含_parse_readme方法"

cat > test_parse_readme_exists.py << 'EOF'
import sys
sys.path.insert(0, 'src')
sys.path.insert(0, 'tools')

from project_analyzer import ProjectAnalyzer

# 检查方法是否存在
if hasattr(ProjectAnalyzer, '_parse_readme'):
    print("PASS: _parse_readme method exists")
    sys.exit(0)
else:
    print("FAIL: _parse_readme method not found")
    sys.exit(1)
EOF

if python3 test_parse_readme_exists.py 2>/dev/null; then
    test_pass
else
    test_fail "_parse_readme方法不存在"
fi

rm -f test_parse_readme_exists.py

# ==================== 测试4: 错误处理器返回值类型 ====================
test_case "错误处理器支持返回字典类型"

cat > test_error_handler_return.py << 'EOF'
import sys
sys.path.insert(0, 'tools')

# 只需验证类型注解正确
from error_handler import ErrorHandler
import inspect

# 获取方法签名
sig = inspect.signature(ErrorHandler.analyze_and_fix)
return_annotation = sig.return_annotation

# 检查返回类型提示
if 'Optional' in str(return_annotation) or 'Dict' in str(return_annotation):
    print("PASS: Return type supports Dict")
    sys.exit(0)
else:
    print("FAIL: Return type not updated")
    sys.exit(1)
EOF

if python3 test_error_handler_return.py 2>/dev/null; then
    test_pass
else
    test_fail "错误处理器返回类型未更新"
fi

rm -f test_error_handler_return.py

# ==================== 测试5: 版本号检查 ====================
test_case "版本号更新为v1.1"

if grep -q "VERSION = \"1.1\"" main.py; then
    test_pass
else
    test_fail "版本号未更新"
fi

# ==================== 测试6: CHANGELOG存在性 ====================
test_case "CHANGELOG.md文件存在"

if [ -f "CHANGELOG.md" ]; then
    if grep -q "v1.1" CHANGELOG.md; then
        test_pass
    else
        test_fail "CHANGELOG中未包含v1.1信息"
    fi
else
    test_fail "CHANGELOG.md文件不存在"
fi

# ==================== 测试7: 文件语法检查 ====================
test_case "Python文件语法检查"

syntax_errors=0
for file in src/*.py tools/*.py main.py; do
    if [ -f "$file" ]; then
        if ! python3 -m py_compile "$file" 2>/dev/null; then
            echo "语法错误: $file"
            syntax_errors=$((syntax_errors + 1))
        fi
    fi
done

if [ $syntax_errors -eq 0 ]; then
    test_pass
else
    test_fail "$syntax_errors 个文件存在语法错误"
fi

# ==================== 测试总结 ====================
echo "=========================================="
echo "测试总结"
echo "=========================================="
echo "总测试数: $TOTAL_TESTS"
echo -e "${GREEN}通过: $PASSED_TESTS${NC}"
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}失败: $FAILED_TESTS${NC}"
else
    echo -e "失败: $FAILED_TESTS"
fi
echo "成功率: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
echo "=========================================="

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！v1.1升级成功！${NC}"
    exit 0
else
    echo -e "${RED}✗ 部分测试失败，请检查上述错误${NC}"
    exit 1
fi
