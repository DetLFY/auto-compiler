#!/usr/bin/env python3
"""
自动化编译引擎
负责项目分析、依赖安装、编译执行和错误修复的核心逻辑
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

from llm_client import LLMClient
from tools.project_analyzer import ProjectAnalyzer
from tools.dependency_manager import DependencyManager
from tools.error_handler import ErrorHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CompilerEngine:
    """自动化编译引擎"""
    
    def __init__(self, project_path: str, config_path: str = "config/config.json"):
        """
        初始化编译引擎
        
        Args:
            project_path: 待编译项目路径
            config_path: 配置文件路径
        """
        self.project_path = Path(project_path).resolve()
        self.config = self._load_config(config_path)
        
        # 初始化LLM客户端
        self.llm_client = LLMClient(
            api_key=self.config.get('openai_api_key'),
            api_base=self.config.get('openai_api_base'),
            model=self.config.get('model', 'gpt-4-turbo-preview')
        )
        
        # 初始化各个工具模块
        self.analyzer = ProjectAnalyzer(self.llm_client)
        self.dep_manager = DependencyManager(self.llm_client)
        self.error_handler = ErrorHandler(self.llm_client)
        
        # 编译状态
        self.max_retry = self.config.get('max_retry', 5)
        self.compile_history = []
        
        logger.info(f"初始化编译引擎，项目路径: {self.project_path}")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"配置文件不存在: {config_path}，使用默认配置")
            return {}
    
    def compile(self) -> bool:
        """
        执行自动化编译流程
        
        Returns:
            bool: 编译是否成功
        """
        logger.info("="*60)
        logger.info("开始自动化编译流程")
        logger.info("="*60)
        
        try:
            # 步骤1: 分析项目结构
            logger.info("\n[步骤1] 分析项目结构...")
            project_info = self.analyzer.analyze_project(self.project_path)
            logger.info(f"项目类型: {project_info.get('project_type')}")
            logger.info(f"编程语言: {', '.join(project_info.get('languages', []))}") 
            logger.info(f"构建系统: {project_info.get('build_system')}")
            
            # 步骤2: 安装依赖
            logger.info("\n[步骤2] 安装项目依赖...")
            deps_installed = self.dep_manager.install_dependencies(
                self.project_path, 
                project_info
            )
            if deps_installed:
                logger.info("依赖安装成功")
            else:
                logger.warning("依赖安装失败或无需安装")
            
            # 步骤3: 尝试编译
            logger.info("\n[步骤3] 开始编译...")
            success, build_command = self._attempt_build(project_info)
            
            if success:
                logger.info("\n" + "="*60)
                logger.info("✅ 编译成功!")
                logger.info("="*60)
                return True
            
            # 步骤4: 迭代修复编译错误
            logger.info("\n[步骤4] 检测到编译错误，开始自动修复...")
            success = self._fix_build_errors(project_info, build_command)
            
            if success:
                logger.info("\n" + "="*60)
                logger.info("✅ 经过自动修复后，编译成功!")
                logger.info("="*60)
                return True
            else:
                logger.error("\n" + "="*60)
                logger.error("❌ 经过多次尝试后，编译仍然失败")
                logger.error("="*60)
                return False
                
        except Exception as e:
            logger.error(f"编译过程中发生异常: {e}", exc_info=True)
            return False
    
    def _attempt_build(self, project_info: Dict) -> Tuple[bool, Optional[str]]:
        """
        尝试执行编译
        
        Returns:
            (是否成功, 编译命令)
        """
        build_system = project_info.get('build_system', 'unknown')
        build_command = project_info.get('build_command')
        
        if not build_command:
            logger.info("未检测到标准构建命令，请求LLM生成...")
            build_command = self._get_build_command_from_llm(project_info)
        
        logger.info(f"执行编译命令: {build_command}")
        
        try:
            result = subprocess.run(
                build_command,
                shell=True,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            # 记录编译历史
            self.compile_history.append({
                'command': build_command,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            })
            
            if result.returncode == 0:
                logger.info("✅ 编译成功!")
                return True, build_command
            else:
                logger.warning(f"❌ 编译失败，返回码: {result.returncode}")
                logger.debug(f"标准输出:\n{result.stdout}")
                logger.debug(f"错误输出:\n{result.stderr}")
                return False, build_command
                
        except subprocess.TimeoutExpired:
            logger.error("编译超时（超过5分钟）")
            return False, build_command
        except Exception as e:
            logger.error(f"执行编译命令时出错: {e}")
            return False, build_command
    
    def _get_build_command_from_llm(self, project_info: Dict) -> str:
        """使用LLM生成构建命令"""
        response = self.llm_client.call_with_tools(
            messages=[{
                "role": "user",
                "content": f"根据以下项目信息生成构建命令:\n{json.dumps(project_info, indent=2, ensure_ascii=False)}"
            }],
            tools=[{
                "type": "function",
                "function": {
                    "name": "generate_build_command",
                    "description": "生成项目的构建命令",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "完整的构建命令"
                            },
                            "explanation": {
                                "type": "string",
                                "description": "命令的解释说明"
                            }
                        },
                        "required": ["command"]
                    }
                }
            }]
        )
        
        # 解析LLM返回的命令
        if response.get('tool_calls'):
            for tool_call in response['tool_calls']:
                if tool_call['function']['name'] == 'generate_build_command':
                    args = json.loads(tool_call['function']['arguments'])
                    return args.get('command', 'make')
        
        return 'make'  # 默认命令
    
    def _fix_build_errors(self, project_info: Dict, build_command: str) -> bool:
        """
        迭代修复编译错误
        
        Returns:
            bool: 是否修复成功
        """
        for attempt in range(self.max_retry):
            logger.info(f"\n--- 修复尝试 {attempt + 1}/{self.max_retry} ---")
            
            # 获取最后一次编译的错误信息
            last_build = self.compile_history[-1] if self.compile_history else None
            if not last_build:
                logger.error("没有编译历史记录")
                return False
            
            # 使用LLM分析并修复错误
            logger.info("分析编译错误...")
            fix_applied = self.error_handler.analyze_and_fix(
                project_path=self.project_path,
                project_info=project_info,
                error_output=last_build['stderr'],
                stdout_output=last_build['stdout']
            )
            
            if not fix_applied:
                logger.warning("LLM未能提供有效的修复方案")
                return False
            
            # 重新尝试编译
            logger.info("应用修复后重新编译...")
            success, _ = self._attempt_build(project_info)
            
            if success:
                logger.info(f"✅ 第 {attempt + 1} 次修复后编译成功!")
                return True
            else:
                logger.warning(f"❌ 第 {attempt + 1} 次修复后仍然失败")
        
        logger.error(f"已达到最大重试次数 {self.max_retry}，放弃修复")
        return False
    
    def get_build_artifacts(self) -> List[Path]:
        """获取编译产物"""
        artifacts = []
        
        # 常见的编译产物目录和文件
        common_output_dirs = ['build', 'dist', 'out', 'target', 'bin']
        common_output_exts = ['.exe', '.so', '.dll', '.a', '.dylib', '.jar', '.war']
        
        for output_dir in common_output_dirs:
            dir_path = self.project_path / output_dir
            if dir_path.exists():
                artifacts.extend(dir_path.rglob('*'))
        
        # 查找根目录下的可执行文件
        for item in self.project_path.iterdir():
            if item.is_file() and (item.suffix in common_output_exts or os.access(item, os.X_OK)):
                artifacts.append(item)
        
        return artifacts
