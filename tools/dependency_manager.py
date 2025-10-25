"""
依赖管理工具
负责自动安装项目依赖
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DependencyManager:
    """依赖管理器"""
    
    def __init__(self, llm_client):
        """初始化依赖管理器"""
        self.llm_client = llm_client
    
    def install_dependencies(self, project_path: Path, project_info: Dict) -> bool:
        """
        安装项目依赖
        
        Args:
            project_path: 项目路径
            project_info: 项目信息
            
        Returns:
            bool: 是否成功安装
        """
        build_system = project_info.get('build_system')
        
        if not build_system:
            logger.warning("未知构建系统，跳过依赖安装")
            return False
        
        logger.info(f"为构建系统 {build_system} 安装依赖...")
        
        # 根据构建系统选择安装方法
        install_methods = {
            'npm': self._install_npm_deps,
            'maven': self._install_maven_deps,
            'gradle': self._install_gradle_deps,
            'cargo': self._install_cargo_deps,
            'go': self._install_go_deps,
            'setuptools': self._install_python_deps,
            'poetry': self._install_poetry_deps,
            'pip': self._install_python_deps,
        }
        
        install_method = install_methods.get(build_system)
        if install_method:
            return install_method(project_path, project_info)
        else:
            logger.info(f"构建系统 {build_system} 通常在构建时自动处理依赖")
            return True
    
    def _install_npm_deps(self, project_path: Path, project_info: Dict) -> bool:
        """安装npm依赖"""
        package_json = project_path / 'package.json'
        if not package_json.exists():
            logger.warning("未找到package.json文件")
            return False
        
        logger.info("执行: npm install")
        try:
            result = subprocess.run(
                ['npm', 'install'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✅ npm依赖安装成功")
                return True
            else:
                logger.error(f"npm安装失败: {result.stderr}")
                return self._fix_dependency_error(project_path, project_info, 
                                                  'npm', result.stderr)
        except Exception as e:
            logger.error(f"npm安装异常: {e}")
            return False
    
    def _install_maven_deps(self, project_path: Path, project_info: Dict) -> bool:
        """安装Maven依赖"""
        pom_xml = project_path / 'pom.xml'
        if not pom_xml.exists():
            logger.warning("未找到pom.xml文件")
            return False
        
        logger.info("执行: mvn dependency:resolve")
        try:
            result = subprocess.run(
                ['mvn', 'dependency:resolve'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                logger.info("✅ Maven依赖安装成功")
                return True
            else:
                logger.error(f"Maven依赖解析失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Maven安装异常: {e}")
            return False
    
    def _install_gradle_deps(self, project_path: Path, project_info: Dict) -> bool:
        """安装Gradle依赖"""
        build_gradle = project_path / 'build.gradle'
        if not build_gradle.exists():
            logger.warning("未找到build.gradle文件")
            return False
        
        # 检查gradlew是否存在
        gradlew = project_path / 'gradlew'
        gradle_cmd = './gradlew' if gradlew.exists() else 'gradle'
        
        logger.info(f"执行: {gradle_cmd} dependencies")
        try:
            result = subprocess.run(
                [gradle_cmd, 'dependencies'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600,
                shell=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Gradle依赖安装成功")
                return True
            else:
                logger.error(f"Gradle依赖解析失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Gradle安装异常: {e}")
            return False
    
    def _install_cargo_deps(self, project_path: Path, project_info: Dict) -> bool:
        """安装Cargo依赖"""
        cargo_toml = project_path / 'Cargo.toml'
        if not cargo_toml.exists():
            logger.warning("未找到Cargo.toml文件")
            return False
        
        logger.info("执行: cargo fetch")
        try:
            result = subprocess.run(
                ['cargo', 'fetch'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                logger.info("✅ Cargo依赖安装成功")
                return True
            else:
                logger.error(f"Cargo依赖获取失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Cargo安装异常: {e}")
            return False
    
    def _install_go_deps(self, project_path: Path, project_info: Dict) -> bool:
        """安装Go依赖"""
        go_mod = project_path / 'go.mod'
        if not go_mod.exists():
            logger.warning("未找到go.mod文件")
            return False
        
        logger.info("执行: go mod download")
        try:
            result = subprocess.run(
                ['go', 'mod', 'download'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                logger.info("✅ Go依赖安装成功")
                return True
            else:
                logger.error(f"Go依赖下载失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Go安装异常: {e}")
            return False
    
    def _install_python_deps(self, project_path: Path, project_info: Dict) -> bool:
        """安装Python依赖"""
        requirements = project_path / 'requirements.txt'
        setup_py = project_path / 'setup.py'
        
        if requirements.exists():
            logger.info("执行: pip install -r requirements.txt")
            try:
                result = subprocess.run(
                    ['pip', 'install', '-r', 'requirements.txt'],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                if result.returncode == 0:
                    logger.info("✅ Python依赖安装成功")
                    return True
                else:
                    logger.error(f"pip安装失败: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"pip安装异常: {e}")
                return False
        
        elif setup_py.exists():
            logger.info("执行: pip install -e .")
            try:
                result = subprocess.run(
                    ['pip', 'install', '-e', '.'],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                if result.returncode == 0:
                    logger.info("✅ Python依赖安装成功")
                    return True
                else:
                    logger.error(f"pip安装失败: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"pip安装异常: {e}")
                return False
        
        else:
            logger.warning("未找到requirements.txt或setup.py文件")
            return False
    
    def _install_poetry_deps(self, project_path: Path, project_info: Dict) -> bool:
        """安装Poetry依赖"""
        pyproject_toml = project_path / 'pyproject.toml'
        if not pyproject_toml.exists():
            logger.warning("未找到pyproject.toml文件")
            return False
        
        logger.info("执行: poetry install")
        try:
            result = subprocess.run(
                ['poetry', 'install'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                logger.info("✅ Poetry依赖安装成功")
                return True
            else:
                logger.error(f"Poetry安装失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Poetry安装异常: {e}")
            return False
    
    def _fix_dependency_error(self, project_path: Path, project_info: Dict,
                             dep_system: str, error_output: str) -> bool:
        """使用LLM修复依赖安装错误"""
        logger.info("尝试使用LLM修复依赖安装错误...")
        
        try:
            prompt = f"""依赖安装失败，错误信息如下：

依赖系统: {dep_system}
项目路径: {project_path}
错误输出:
{error_output}

请分析错误原因并提供修复方案。

【关键约束】：
1. 不要使用 sudo 命令（当前用户已有足够权限）
2. 可以直接使用包管理器安装：
   - Ubuntu/Debian: apt-get install -y <package>
   - CentOS/RHEL: yum install -y <package>
   - macOS: brew install <package>
3. 可以安装Python包: pip install <package>
4. 可以安装Node.js包: npm install <package>
5. manual_steps保持为空，所有命令放入fix_commands

示例：
- ✅ 正确: fix_commands: ["apt-get install -y python3-dev"]
- ✅ 正确: fix_commands: ["pip install numpy"]
- ❌ 错误: fix_commands: ["sudo apt-get install python3-dev"]
"""
            
            response = self.llm_client.call_with_tools(
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "fix_dependency_error",
                        "description": "提供依赖安装错误的修复方案",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "fix_commands": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "修复命令列表（不包含sudo）"
                                },
                                "manual_steps": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "需要手动执行的步骤"
                                },
                                "explanation": {
                                    "type": "string",
                                    "description": "错误原因和修复说明"
                                }
                            },
                            "required": ["explanation"]
                        }
                    }
                }]
            )
            
            # 执行修复命令
            if response.get('tool_calls'):
                for tool_call in response['tool_calls']:
                    if tool_call['function']['name'] == 'fix_dependency_error':
                        args = json.loads(tool_call['function']['arguments'])
                        commands = args.get('fix_commands', [])
                        manual_steps = args.get('manual_steps', [])
                        
                        logger.info(f"LLM建议的修复方案: {args.get('explanation')}")
                        
                        # 显示需要手动执行的步骤（如果有）
                        if manual_steps:
                            logger.warning("以下步骤需要手动执行:")
                            for step in manual_steps:
                                logger.warning(f"  - {step}")
                        
                        # 执行自动修复命令
                        for cmd in commands:
                            # 如果命令包含sudo，自动移除
                            if 'sudo' in cmd.lower():
                                logger.warning(f"命令包含sudo，已自动移除: {cmd}")
                                cmd = cmd.replace('sudo ', '').replace('sudo\t', '')
                                logger.info(f"修正后的命令: {cmd}")
                            
                            logger.info(f"执行修复命令: {cmd}")
                            result = subprocess.run(
                                cmd,
                                shell=True,
                                cwd=project_path,
                                capture_output=True,
                                text=True,
                                timeout=600
                            )
                            
                            if result.returncode != 0:
                                logger.error(f"修复命令执行失败: {result.stderr}")
                                # 继续执行其他命令
                            else:
                                logger.info(f"✅ 命令执行成功")
                        
                        return True
            
        except Exception as e:
            logger.error(f"LLM修复依赖错误失败: {e}")
        
        return False
