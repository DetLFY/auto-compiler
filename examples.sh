#!/bin/bash

# 示例: 编译C项目
echo "示例1: 编译C项目"
python main.py examples/c-project/

# 示例: 编译Python项目
echo "示例2: 编译Python项目"
python main.py examples/python-project/

# 示例: 使用调试模式
echo "示例3: 调试模式"
python main.py examples/rust-project/ --log-level DEBUG

# 示例: 自定义重试次数
echo "示例4: 自定义重试次数"
python main.py examples/java-project/ --max-retry 10
