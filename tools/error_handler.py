"""
错误处理工具
负责分析编译错误并自动修复
"""

import os
import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ErrorHandler:
    """编译错误处理器"""
    
    def __init__(self, llm_client):
        """初始化错误处理器"""
        self.llm_client = llm_client
    
    def analyze_and_fix(self, project_path: Path, project_info: Dict,
                       error_output: str, stdout_output: str = "") -> bool:
        """
        分析编译错误并尝试修复
        
        Args:
            project_path: 项目路径
            project_info: 项目信息
            error_output: 错误输出
            stdout_output: 标准输出
            
        Returns:
            bool: 是否成功应用修复
        """
        logger.info("分析编译错误...")
        
        # 1. 提取关键错误信息
        error_summary = self._extract_error_info(error_output, stdout_output)
        logger.info(f"提取到 {len(error_summary['errors'])} 个错误")
        
        # 2. 使用LLM分析错误并生成修复方案
        fix_plan = self._get_fix_plan_from_llm(
            project_path, project_info, error_summary, error_output
        )
        
        if not fix_plan:
            logger.error("LLM未能生成有效的修复方案")
            return False
        
        # 3. 应用修复方案
        logger.info("应用修复方案...")
        success = self._apply_fixes(project_path, fix_plan)
        
        return success
    
    def _extract_error_info(self, error_output: str, stdout_output: str) -> Dict:
        """提取错误信息"""
        errors = []
        
        # 合并输出
        full_output = stdout_output + "\n" + error_output
        
        # 常见的错误模式
        patterns = [
            # GCC/Clang错误格式: file.c:10:5: error: ...
            r'([^:\s]+):(\d+):(\d+):\s*(error|fatal error):\s*(.+)',
            # MSVC错误格式: file.c(10): error C2065: ...
            r'([^:\s]+)\((\d+)\):\s*error\s+[A-Z]\d+:\s*(.+)',
            # Java错误格式: file.java:10: error: ...
            r'([^:\s]+):(\d+):\s*error:\s*(.+)',
            # Python错误
            r'File "([^"]+)", line (\d+).*\n.*\n\s*(.+Error:.+)',
            # Make错误
            r'make(?:\[\d+\])?: \*\*\* \[(.+)\] Error \d+',
            # Cargo错误
            r'error(?:\[E\d+\])?: (.+)',
            # npm/node错误
            r'ERROR in (.+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, full_output, re.MULTILINE)
            for match in matches:
                error_info = {
                    'pattern': pattern,
                    'match': match.groups(),
                    'full_match': match.group(0)
                }
                errors.append(error_info)
        
        # 如果没有匹配到具体错误，返回原始输出的摘要
        if not errors:
            lines = error_output.strip().split('\n')
            errors.append({
                'pattern': 'generic',
                'match': [],
                'full_match': '\n'.join(lines[-20:]) if len(lines) > 20 else error_output
            })
        
        return {
            'errors': errors,
            'error_count': len(errors),
            'full_output': full_output
        }
    
    def _get_fix_plan_from_llm(self, project_path: Path, project_info: Dict,
                               error_summary: Dict, error_output: str) -> Optional[Dict]:
        """使用LLM生成修复方案"""
        try:
            # 构建详细的错误信息
            error_details = "\n".join([
                f"错误 {i+1}: {err['full_match']}"
                for i, err in enumerate(error_summary['errors'][:10])  # 限制前10个错误
            ])
            
            # 读取相关源文件内容（如果错误中提到了具体文件）
            source_files_content = self._read_related_source_files(
                project_path, error_summary
            )
            
            prompt = f"""分析以下编译错误并提供修复方案：

项目信息:
- 项目类型: {project_info.get('project_type')}
- 构建系统: {project_info.get('build_system')}
- 编程语言: {', '.join(project_info.get('languages', []))}

编译错误:
{error_details}

相关源文件:
{source_files_content}

请分析错误原因并提供具体的修复方案。修复方案应该包括：
1. 需要修改的文件路径
2. 具体的修改内容
3. 如果需要安装依赖或工具，提供安装命令

【关键约束】：
1. 绝对禁止使用 sudo 命令（当前用户已有足够权限）
2. 如果缺少系统工具（如cmake、make等），直接使用包管理器安装：
   - Ubuntu/Debian: apt-get install -y <package>
   - CentOS/RHEL: yum install -y <package>
   - macOS: brew install <package>
3. 如果缺少Python包: pip install <package>
4. 如果缺少Node.js包: npm install <package>
5. 所有命令不要使用sudo前缀
6. 安装命令放入commands字段，会自动执行
7. manual_steps字段保持为空

示例：
- ❌ 错误: commands: ["sudo apt-get install cmake"]
- ✅ 正确: commands: ["apt-get install -y cmake"]
- ✅ 正确: commands: ["apt-get install -y cmake make gcc"]
- ✅ 正确: commands: ["pip install numpy", "apt-get install -y python3-dev"]

请确保修复方案是具体的、可自动执行的。
"""
            
            response = self.llm_client.call_with_tools(
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "provide_fix_plan",
                        "description": "提供编译错误的修复方案",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "error_analysis": {
                                    "type": "string",
                                    "description": "错误原因分析"
                                },
                                "file_changes": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "file_path": {
                                                "type": "string",
                                                "description": "需要修改的文件路径（相对于项目根目录）"
                                            },
                                            "changes": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "line_number": {
                                                            "type": "integer",
                                                            "description": "修改的行号（0表示在文件末尾添加）"
                                                        },
                                                        "old_content": {
                                                            "type": "string",
                                                            "description": "原始内容（用于匹配）"
                                                        },
                                                        "new_content": {
                                                            "type": "string",
                                                            "description": "新内容"
                                                        },
                                                        "action": {
                                                            "type": "string",
                                                            "enum": ["replace", "insert", "delete"],
                                                            "description": "操作类型"
                                                        }
                                                    },
                                                    "required": ["new_content", "action"]
                                                }
                                            }
                                        },
                                        "required": ["file_path", "changes"]
                                    },
                                    "description": "需要修改的文件列表"
                                },
                                "commands": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "需要执行的命令（不含sudo，如：apt-get install -y cmake, pip install xxx, npm install xxx）"
                                },
                                "manual_steps": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "【保持为空】所有操作都应该通过commands自动执行"
                                }
                            },
                            "required": ["error_analysis", "file_changes"]
                        }
                    }
                }],
                temperature=0.3  # 降低温度以获得更确定的修复方案
            )
            
            # 解析修复方案
            if response.get('tool_calls'):
                for tool_call in response['tool_calls']:
                    if tool_call['function']['name'] == 'provide_fix_plan':
                        fix_plan = json.loads(tool_call['function']['arguments'])
                        logger.info(f"LLM错误分析: {fix_plan.get('error_analysis')}")
                        return fix_plan
            
        except Exception as e:
            logger.error(f"获取LLM修复方案失败: {e}", exc_info=True)
        
        return None
    
    def _read_related_source_files(self, project_path: Path, 
                                   error_summary: Dict, max_lines: int = 50) -> str:
        """读取错误相关的源文件内容"""
        files_content = []
        processed_files = set()
        
        # 从错误信息中提取文件路径
        for error in error_summary['errors'][:5]:  # 只处理前5个错误
            match = error['match']
            if match and len(match) > 0:
                file_path = match[0]
                
                # 清理文件路径
                file_path = file_path.strip()
                if file_path in processed_files:
                    continue
                
                full_path = project_path / file_path
                if full_path.exists() and full_path.is_file():
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            
                        # 如果错误中有行号，读取相关行的上下文
                        if len(match) > 1 and match[1].isdigit():
                            line_num = int(match[1])
                            start = max(0, line_num - 10)
                            end = min(len(lines), line_num + 10)
                            content = ''.join(lines[start:end])
                        else:
                            # 否则读取文件开头
                            content = ''.join(lines[:max_lines])
                        
                        files_content.append(f"\n文件: {file_path}\n{content}")
                        processed_files.add(file_path)
                        
                    except Exception as e:
                        logger.warning(f"无法读取文件 {file_path}: {e}")
        
        if not files_content:
            return "（未能提取到相关源文件）"
        
        return '\n'.join(files_content)
    
    def _apply_fixes(self, project_path: Path, fix_plan: Dict) -> bool:
        """应用修复方案"""
        try:
            # 0. 检查并显示manual_steps（如果有）
            manual_steps = fix_plan.get('manual_steps', [])
            if manual_steps:
                logger.warning("="*60)
                logger.warning("⚠️  以下步骤需要手动执行:")
                logger.warning("="*60)
                for i, step in enumerate(manual_steps, 1):
                    logger.warning(f"{i}. {step}")
                logger.warning("="*60)
            
            # 1. 执行命令（包括安装依赖和工具）
            commands = fix_plan.get('commands', [])
            for cmd in commands:
                # 检查是否包含sudo，如果有则移除
                if 'sudo' in cmd.lower():
                    logger.warning(f"⚠️  命令包含sudo，已自动移除: {cmd}")
                    cmd = cmd.replace('sudo ', '').replace('sudo\t', '')
                    logger.info(f"   修正后的命令: {cmd}")
                
                logger.info(f"执行命令: {cmd}")
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=600  # 安装工具可能需要更长时间
                )
                
                if result.returncode != 0:
                    logger.warning(f"命令执行失败: {result.stderr}")
                    logger.warning(f"标准输出: {result.stdout}")
                    # 继续执行其他命令，不立即返回False
                else:
                    logger.info(f"✅ 命令执行成功")
                    if result.stdout:
                        logger.debug(f"输出: {result.stdout[:500]}")
            
            # 2. 应用文件修改
            file_changes = fix_plan.get('file_changes', [])
            if not file_changes and not commands:
                logger.warning("⚠️  没有文件修改也没有命令，可能无法解决问题")
                
            for file_change in file_changes:
                file_path = project_path / file_change['file_path']
                changes = file_change['changes']
                
                if not file_path.exists():
                    logger.warning(f"文件不存在: {file_path}")
                    # 如果是新文件，创建它
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.touch()
                
                # 应用修改
                self._apply_file_changes(file_path, changes)
                logger.info(f"✅ 已修改文件: {file_change['file_path']}")
            
            return True
            
        except Exception as e:
            logger.error(f"应用修复方案失败: {e}", exc_info=True)
            return False
    
    def _apply_file_changes(self, file_path: Path, changes: List[Dict]):
        """应用文件修改"""
        # 读取原文件内容
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        else:
            lines = []
        
        # 按行号倒序排序，从后往前修改避免行号偏移
        sorted_changes = sorted(
            changes,
            key=lambda x: x.get('line_number', 0),
            reverse=True
        )
        
        for change in sorted_changes:
            action = change['action']
            new_content = change['new_content']
            
            if not new_content.endswith('\n') and action in ['insert', 'replace']:
                new_content += '\n'
            
            if action == 'replace':
                old_content = change.get('old_content', '')
                # 在文件中查找并替换
                for i, line in enumerate(lines):
                    if old_content in line:
                        lines[i] = line.replace(old_content, new_content)
                        break
            
            elif action == 'insert':
                line_num = change.get('line_number', 0)
                if line_num == 0 or line_num > len(lines):
                    lines.append(new_content)
                else:
                    lines.insert(line_num - 1, new_content)
            
            elif action == 'delete':
                line_num = change.get('line_number', 0)
                if 0 < line_num <= len(lines):
                    del lines[line_num - 1]
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
