#!/usr/bin/env python3
"""
测试自动化编译系统的各个模块
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent / 'tools'))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    try:
        from llm_client import LLMClient
        print("✅ LLMClient导入成功")
        
        from project_analyzer import ProjectAnalyzer
        print("✅ ProjectAnalyzer导入成功")
        
        from dependency_manager import DependencyManager
        print("✅ DependencyManager导入成功")
        
        from error_handler import ErrorHandler
        print("✅ ErrorHandler导入成功")
        
        from compiler_engine import CompilerEngine
        print("✅ CompilerEngine导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_config():
    """测试配置文件"""
    print("\n测试配置文件...")
    config_file = Path(__file__).parent / 'config' / 'config.json'
    
    if not config_file.exists():
        print("❌ 配置文件不存在")
        return False
    
    try:
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        if 'openai_api_key' not in config:
            print("⚠️  警告: 配置文件中缺少 openai_api_key")
        
        print(f"✅ 配置文件加载成功")
        print(f"   - API Base: {config.get('openai_api_base', 'N/A')}")
        print(f"   - Model: {config.get('model', 'N/A')}")
        print(f"   - Max Retry: {config.get('max_retry', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return False

def test_project_structure():
    """测试项目结构"""
    print("\n测试项目结构...")
    base_dir = Path(__file__).parent
    
    required_dirs = [
        'src',
        'tools',
        'config'
    ]
    
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'src/compiler_engine.py',
        'src/llm_client.py',
        'tools/project_analyzer.py',
        'tools/dependency_manager.py',
        'tools/error_handler.py',
        'config/config.json'
    ]
    
    all_ok = True
    
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"✅ 目录存在: {dir_name}")
        else:
            print(f"❌ 目录缺失: {dir_name}")
            all_ok = False
    
    for file_name in required_files:
        file_path = base_dir / file_name
        if file_path.exists():
            print(f"✅ 文件存在: {file_name}")
        else:
            print(f"❌ 文件缺失: {file_name}")
            all_ok = False
    
    return all_ok

def test_dependencies():
    """测试依赖包"""
    print("\n测试Python依赖...")
    
    required_packages = ['requests']
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            all_ok = False
    
    return all_ok

def main():
    """主测试函数"""
    print("="*60)
    print("🧪 自动化编译系统测试")
    print("="*60)
    
    results = []
    
    # 运行各项测试
    results.append(("项目结构", test_project_structure()))
    results.append(("依赖包", test_dependencies()))
    results.append(("模块导入", test_imports()))
    results.append(("配置文件", test_config()))
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print(f"总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("✅ 所有测试通过！系统就绪。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查上述错误。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
