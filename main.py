#!/usr/bin/env python3
"""
自动化编译系统主入口
Version: 1.1.5
- v1.0: 基础自动化编译功能
- v1.1: 添加README解析功能，优先从README获取构建指令
- v1.1.1: 修复README解析中的命令清理问题，支持子目录检测
- v1.1.2: 改进命令清理逻辑和子目录检测，增强libexpat类项目支持
- v1.1.3: 修复误入测试目录问题，优先使用根目录构建
- v1.1.4: 修复子目录检测逻辑，不将configure.ac误判为实际构建文件
- v1.1.5: 重构prompt策略，根据项目结构生成不同的指令，强制子目录一致性验证
"""

import sys
import argparse
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from compiler_engine import CompilerEngine

VERSION = "1.1.5"


def setup_logging(log_level: str):
    """配置日志"""
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('auto_compiler.log', encoding='utf-8')
        ]
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description=f'自动化编译系统 v{VERSION} - 使用LLM智能处理编译过程',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 编译指定项目
  python main.py /path/to/project
  
  # 使用自定义配置文件
  python main.py /path/to/project --config custom_config.json
  
  # 显示详细日志
  python main.py /path/to/project --log-level DEBUG

新功能 (v1.1):
  - 自动解析项目README文件，提取构建指令
  - 优先使用README中的构建方法，提高编译成功率
  - 修复了构建命令更新机制，避免重复错误
        """
    )
    
    parser.add_argument(
        'project_path',
        type=str,
        help='待编译项目的路径'
    )
    
    parser.add_argument(
        '-c', '--config',
        type=str,
        default='config/config.json',
        help='配置文件路径（默认: config/config.json）'
    )
    
    parser.add_argument(
        '-l', '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别（默认: INFO）'
    )
    
    parser.add_argument(
        '--max-retry',
        type=int,
        default=5,
        help='最大重试次数（默认: 5）'
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # 验证项目路径
    project_path = Path(args.project_path).resolve()
    if not project_path.exists():
        logger.error(f"项目路径不存在: {project_path}")
        sys.exit(1)
    
    if not project_path.is_dir():
        logger.error(f"项目路径不是目录: {project_path}")
        sys.exit(1)
    
    # 输出欢迎信息
    print("="*70)
    print(f"🤖 自动化编译系统 v{VERSION}")
    print("📁 项目路径:", project_path)
    print("⚙️  配置文件:", args.config)
    print("="*70)
    print()
    
    try:
        # 创建编译引擎
        engine = CompilerEngine(
            project_path=str(project_path),
            config_path=args.config
        )
        
        # 执行编译
        success = engine.compile()
        
        # 输出结果
        print()
        print("="*70)
        if success:
            print("✅ 编译成功！")
            
            # 显示编译产物
            artifacts = engine.get_build_artifacts()
            if artifacts:
                print(f"\n📦 编译产物 ({len(artifacts)}个):")
                for artifact in artifacts[:10]:  # 只显示前10个
                    print(f"  - {artifact.relative_to(project_path)}")
                if len(artifacts) > 10:
                    print(f"  ... 以及其他 {len(artifacts) - 10} 个文件")
            
            sys.exit(0)
        else:
            print("❌ 编译失败！")
            print("\n请查看日志文件 auto_compiler.log 获取详细信息")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(130)
    except Exception as e:
        logger.error(f"程序异常: {e}", exc_info=True)
        print(f"\n❌ 程序异常: {e}")
        print("请查看日志文件 auto_compiler.log 获取详细信息")
        sys.exit(1)
    finally:
        print("="*70)


if __name__ == '__main__':
    main()
