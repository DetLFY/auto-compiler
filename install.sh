#!/bin/bash

echo "🚀 安装自动化编译系统"
echo "========================"

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# 安装依赖
echo ""
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 依赖安装成功"
else
    echo "❌ 依赖安装失败"
    exit 1
fi

# 复制配置文件模板
if [ ! -f "config/config.json" ]; then
    echo ""
    echo "📝 创建配置文件..."
    cat > config/config.json << 'EOF'
{
  "openai_api_key": "your-api-key-here",
  "openai_api_base": "https://api.openai.com/v1",
  "model": "gpt-4-turbo-preview",
  "max_retry": 5,
  "timeout": 300,
  "log_level": "INFO"
}
EOF
    echo "✅ 配置文件已创建: config/config.json"
    echo "⚠️  请编辑 config/config.json 并填入你的API密钥"
else
    echo "✅ 配置文件已存在"
fi

# 设置可执行权限
chmod +x main.py
chmod +x examples.sh
chmod +x test_system.py

echo ""
echo "========================"
echo "✅ 安装完成！"
echo ""
echo "下一步："
echo "1. 编辑 config/config.json 并设置你的API密钥"
echo "2. 运行测试: python3 test_system.py"
echo "3. 开始使用: python3 main.py /path/to/project"
echo ""
