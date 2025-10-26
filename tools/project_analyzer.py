"""
项目分析工具
负责识别项目类型、编程语言、构建系统等
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ProjectAnalyzer:
    """项目分析器"""
    
    def __init__(self, llm_client):
        """初始化项目分析器"""
        self.llm_client = llm_client
        
        # 常见的构建文件映射
        self.build_file_patterns = {
            'CMakeLists.txt': {'type': 'cmake', 'language': 'C/C++'},
            'Makefile': {'type': 'make', 'language': 'C/C++'},
            'pom.xml': {'type': 'maven', 'language': 'Java'},
            'build.gradle': {'type': 'gradle', 'language': 'Java/Kotlin'},
            'package.json': {'type': 'npm', 'language': 'JavaScript/TypeScript'},
            'Cargo.toml': {'type': 'cargo', 'language': 'Rust'},
            'go.mod': {'type': 'go', 'language': 'Go'},
            'setup.py': {'type': 'setuptools', 'language': 'Python'},
            'pyproject.toml': {'type': 'poetry', 'language': 'Python'},
            'build.sbt': {'type': 'sbt', 'language': 'Scala'},
            'meson.build': {'type': 'meson', 'language': 'C/C++'},
            'configure.ac': {'type': 'autotools', 'language': 'C/C++'},
            'BUILD': {'type': 'bazel', 'language': 'Multiple'},
            'BUILD.bazel': {'type': 'bazel', 'language': 'Multiple'}
        }
        
        # 编程语言文件扩展名
        self.language_extensions = {
            '.c': 'C',
            '.h': 'C',
            '.cpp': 'C++',
            '.hpp': 'C++',
            '.cc': 'C++',
            '.cxx': 'C++',
            '.java': 'Java',
            '.kt': 'Kotlin',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.py': 'Python',
            '.rs': 'Rust',
            '.go': 'Go',
            '.scala': 'Scala',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.cs': 'C#',
            '.swift': 'Swift',
            '.m': 'Objective-C',
            '.mm': 'Objective-C++',
        }
    
    def analyze_project(self, project_path: Path) -> Dict:
        """
        分析项目结构
        
        Args:
            project_path: 项目路径
            
        Returns:
            Dict: 项目信息
        """
        logger.info(f"开始分析项目: {project_path}")
        
        project_info = {
            'path': str(project_path),
            'name': project_path.name,
            'build_system': None,
            'project_type': None,
            'languages': [],
            'build_command': None,
            'dependencies': [],
            'files': [],
            'readme_instructions': None
        }
        
        # 1. 尝试从README获取构建指令（v1.1新功能）
        readme_info = self._parse_readme(project_path)
        if readme_info:
            logger.info("从README文件中提取到构建指令")
            project_info.update(readme_info)
            project_info['readme_instructions'] = True
        
        # 2. 检测构建系统（如果README没有提供完整信息）
        if not project_info['build_system'] or not project_info['build_command']:
            build_info = self._detect_build_system(project_path)
            # 只更新未从README获取的字段
            for key, value in build_info.items():
                if not project_info.get(key):
                    project_info[key] = value
        
        # 3. 扫描文件识别编程语言
        languages = self._detect_languages(project_path)
        if not project_info['languages']:
            project_info['languages'] = languages
        
        # 4. 获取项目文件列表（用于LLM分析）
        project_files = self._get_project_structure(project_path)
        project_info['files'] = project_files
        
        # 5. 使用LLM进行深度分析（仅在没有README指令时）
        if not project_info.get('readme_instructions'):
            enhanced_info = self._llm_analysis(project_info)
            project_info.update(enhanced_info)
        
        logger.info(f"项目分析完成: {json.dumps(project_info, indent=2, ensure_ascii=False)}")
        return project_info
    
    def _detect_build_system(self, project_path: Path) -> Dict:
        """检测构建系统"""
        result = {
            'build_system': None,
            'project_type': None,
            'build_command': None
        }
        
        for build_file, info in self.build_file_patterns.items():
            file_path = project_path / build_file
            if file_path.exists():
                result['build_system'] = info['type']
                result['project_type'] = info['language']
                result['build_command'] = self._get_default_build_command(info['type'])
                logger.info(f"检测到构建系统: {info['type']}")
                return result
        
        # 检查configure脚本
        if (project_path / 'configure').exists():
            result['build_system'] = 'autotools'
            result['project_type'] = 'C/C++'
            result['build_command'] = './configure && make'
            return result
        
        logger.warning("未检测到已知的构建系统")
        return result
    
    def _check_build_subdirectories(self, project_path: Path) -> str:
        """
        检查项目是否有子目录包含构建文件
        
        Args:
            project_path: 项目路径
            
        Returns:
            str: 子目录信息描述
        """
        subdirs_with_build = []
        main_subdir = None
        
        # 首先检查根目录是否有构建文件
        root_has_cmake = (project_path / 'CMakeLists.txt').exists()
        # 只检查实际的configure脚本，不检查configure.ac（可能是autoscan生成的）
        root_has_configure = (project_path / 'configure').exists()
        root_has_makefile = (project_path / 'Makefile').exists()
        # 检查buildconf.sh（autotools项目的准备脚本）
        root_has_buildconf = (project_path / 'buildconf.sh').exists()
        
        # 如果根目录有实际的构建文件（configure脚本或buildconf.sh），优先使用根目录
        if root_has_cmake or root_has_configure or root_has_buildconf or root_has_makefile:
            logger.info("根目录已包含构建文件，不需要进入子目录")
            return "- 根目录包含构建文件，直接在根目录构建即可"
        
        # 只有当根目录没有构建文件时，才检查子目录
        for item in project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # 跳过常见的测试/示例目录
                if item.name.lower() in ['test', 'tests', 'testing', 'fuzzing', 'examples', 'samples', 'docs', 'doc']:
                    continue
                    
                # 检查是否包含常见的构建文件
                has_cmake = (item / 'CMakeLists.txt').exists()
                has_configure = (item / 'configure').exists() or (item / 'configure.ac').exists()
                has_buildconf = (item / 'buildconf.sh').exists()
                has_makefile = (item / 'Makefile').exists() or (item / 'Makefile.am').exists()
                
                if has_cmake or has_configure or has_makefile or has_buildconf:
                    build_types = []
                    if has_cmake:
                        build_types.append('CMake')
                    if has_configure or has_buildconf:
                        build_types.append('Autotools')
                    if has_makefile:
                        build_types.append('Make')
                    
                    info = f"  - {item.name}/ ({', '.join(build_types)})"
                    subdirs_with_build.append(info)
                    
                    # 记录主要的子目录（通常是项目名的子目录）
                    if not main_subdir or item.name.lower() in [project_path.name.lower(), 'src', 'source']:
                        main_subdir = item.name
        
        if subdirs_with_build:
            result = "- 包含构建文件的子目录:\n" + "\n".join(subdirs_with_build)
            if main_subdir:
                result += f"\n- 主要构建目录可能是: {main_subdir}/"
                result += f"\n- 建议在构建命令前添加: cd {main_subdir} &&"
            return result
        else:
            return "- 根目录和子目录都没有发现构建文件"

    
    def _parse_readme(self, project_path: Path) -> Optional[Dict]:
        """
        解析README文件获取构建指令 (v1.1新功能)
        
        Args:
            project_path: 项目路径
            
        Returns:
            Dict: 从README提取的构建信息，如果没有找到README返回None
        """
        # 查找README文件（支持多种格式）
        readme_patterns = [
            'README.md', 'README.MD', 'Readme.md',
            'README.txt', 'README.rst', 'README',
            'readme.md', 'readme.txt'
        ]
        
        readme_path = None
        for pattern in readme_patterns:
            potential_path = project_path / pattern
            if potential_path.exists():
                readme_path = potential_path
                logger.info(f"找到README文件: {pattern}")
                break
        
        if not readme_path:
            logger.info("未找到README文件")
            return None
        
        try:
            # 读取README内容
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                readme_content = f.read()
            
            # 限制内容长度，避免token过多
            if len(readme_content) > 10000:
                readme_content = readme_content[:10000] + "\n... (内容过长，已截断)"
            
            # 检查项目是否有子目录包含实际构建文件
            # 例如 libexpat/expat/ 或 project/src/
            subdirs_info = self._check_build_subdirectories(project_path)
            
            # 判断是否需要进入子目录
            needs_subdir = "建议在构建命令前添加: cd" in subdirs_info
            subdir_name = None
            if needs_subdir:
                # 从 subdirs_info 中提取子目录名
                import re
                match = re.search(r'cd (\w+) &&', subdirs_info)
                if match:
                    subdir_name = match.group(1)
            
            # 构建针对性的 prompt
            if needs_subdir and subdir_name:
                # 情况1：必须进入子目录
                prompt = f"""请分析以下README文件内容，提取项目的构建和安装指令。

README内容：
{readme_content}

【重要】项目结构信息：
{subdirs_info}

**关键信息**：
- 项目根目录: {project_path.name}（根目录没有构建文件）
- 实际构建目录: {subdir_name}/（构建文件在这个子目录中）
- **必须先 cd {subdir_name} 再执行构建命令**

请提取以下信息：
1. 构建系统类型（如cmake, autotools, make等）
2. 具体的构建命令（完整的命令序列）
3. 需要安装的依赖项
4. 编程语言

【关键要求 - 必须遵守】：
1. **命令必须以 "cd {subdir_name} &&" 开头**（因为构建文件在子目录）
2. README中如果提到 "./buildconf.sh" 或 "./configure" 或 "cmake"，这些都是在 {subdir_name}/ 目录下执行
3. 不要包含任何中文、注释、说明文字
4. 去掉所有sudo前缀（以root用户运行）
5. 使用 'mkdir -p build' 而不是 'mkdir build'
6. 命令之间用 && 连接

正确示例：
- "cd {subdir_name} && ./buildconf.sh && ./configure && make"  ← Autotools
- "cd {subdir_name} && mkdir -p build && cd build && cmake .. && make"  ← CMake
- "cd {subdir_name} && cmake -B build && cmake --build build"  ← CMake简化版

错误示例（不要这样）：
- "mkdir -p build && cd build && cmake .. && make"  ← 缺少 cd {subdir_name}
- "./buildconf.sh && ./configure && make"  ← 缺少 cd {subdir_name}
- "cd tests && ..."  ← 错误的子目录
"""
            else:
                # 情况2：根目录构建
                prompt = f"""请分析以下README文件内容，提取项目的构建和安装指令。

README内容：
{readme_content}

项目结构信息：
- 项目根目录: {project_path.name}
{subdirs_info}

请提取以下信息：
1. 构建系统类型（如cmake, make, maven等）
2. 具体的构建命令（完整的命令序列）
3. 需要安装的依赖项
4. 编程语言

【关键要求】：
1. build_command必须是可以直接在shell中执行的命令序列
2. 不要包含任何中文注释、说明文字、或者标题
3. **在根目录直接构建，不要添加cd命令**
4. **不要选择测试、示例、fuzzing等子目录的构建命令**
5. 如果README提供了多种构建方式，优先选择：CMake > autotools(configure) > make
6. 使用 'mkdir -p build' 而不是 'mkdir build' 以避免目录已存在错误
7. 去掉所有sudo前缀（因为以root用户运行）
8. 命令之间用 && 连接

正确示例：
- "mkdir -p build && cd build && cmake .. && make"  ← 根目录CMake
- "cmake -B build && cmake --build build"  ← 根目录CMake简化版
- "./configure && make && make install"  ← 根目录autotools

错误示例（不要这样）：
- "cd fuzzing && cmake ..."  ← 不要进入测试目录
- "cd src && make"  ← 不要进入子目录（根目录构建）
- "从Git克隆构建：\\n./buildconf.sh"  ← 包含中文
"""
            
            response = self.llm_client.call_with_tools(
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "extract_readme_instructions",
                        "description": "从README中提取构建指令",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "build_system": {
                                    "type": "string",
                                    "description": "构建系统类型（如cmake, autotools, make等）"
                                },
                                "build_command": {
                                    "type": "string",
                                    "description": "可直接执行的构建命令序列，不含任何中文、注释或说明文字，只包含shell命令"
                                },
                                "dependencies": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "依赖项列表（简化的包名，如cmake, gcc等）"
                                },
                                "languages": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "编程语言列表"
                                },
                                "project_type": {
                                    "type": "string",
                                    "description": "项目类型"
                                }
                            },
                            "required": ["build_command"]
                        }
                    }
                }]
            )
            
            # 解析LLM响应
            if response.get('tool_calls'):
                for tool_call in response['tool_calls']:
                    if tool_call['function']['name'] == 'extract_readme_instructions':
                        args = json.loads(tool_call['function']['arguments'])
                        result = {}
                        
                        if args.get('build_command'):
                            # 清理构建命令
                            build_cmd = args['build_command']
                            # 移除sudo前缀
                            build_cmd = build_cmd.replace('sudo ', '').replace('sudo\n', '')
                            
                            # 改进的命令清理逻辑
                            lines = build_cmd.split('\n')
                            cleaned_lines = []
                            for line in lines:
                                line = line.strip()
                                # 跳过空行
                                if not line:
                                    continue
                                # 跳过包含中文的行
                                if any(ord(c) > 127 for c in line):
                                    continue
                                # 跳过纯说明性的行（不以命令开头的冒号行）
                                # 但保留合法的shell命令（如 cd, cmake, make等）
                                if ':' in line and not any(cmd in line.lower() for cmd in [
                                    'cd ', 'cmake', 'make', 'configure', 'autoreconf', 
                                    './buildconf', './build', 'gcc', 'g++', 'python', 
                                    'npm', 'cargo', 'go ', 'mvn', 'gradle'
                                ]):
                                    logger.debug(f"跳过说明性行: {line}")
                                    continue
                                
                                cleaned_lines.append(line)
                            
                            if cleaned_lines:
                                # 用 && 连接命令
                                build_cmd = ' && '.join(cleaned_lines)
                                
                                # 验证命令与项目结构的一致性
                                if needs_subdir and subdir_name:
                                    # 如果需要子目录，确保命令包含 cd subdir_name
                                    if f'cd {subdir_name}' not in build_cmd:
                                        logger.warning(f"命令缺少必需的 'cd {subdir_name}'，自动添加")
                                        build_cmd = f'cd {subdir_name} && {build_cmd}'
                                else:
                                    # 如果不需要子目录，确保命令不要cd到非构建目录
                                    import re
                                    cd_match = re.search(r'cd (\w+)', build_cmd)
                                    if cd_match:
                                        target_dir = cd_match.group(1)
                                        # 检查是否是测试/示例目录
                                        if target_dir.lower() in ['test', 'tests', 'testing', 'fuzzing', 'examples', 'samples', 'docs', 'doc']:
                                            logger.warning(f"命令包含不应该的 'cd {target_dir}'，移除")
                                            build_cmd = re.sub(rf'cd {target_dir} && ', '', build_cmd)
                                
                                result['build_command'] = build_cmd
                                logger.info(f"清理后的构建命令: {build_cmd}")
                            else:
                                logger.warning("清理后没有有效的构建命令，将回退到自动检测")
                                return None
                        
                        if args.get('build_system'):
                            result['build_system'] = args['build_system']
                        
                        if args.get('dependencies'):
                            result['dependencies'] = args['dependencies']
                        
                        if args.get('languages'):
                            result['languages'] = args['languages']
                        
                        if args.get('project_type'):
                            result['project_type'] = args['project_type']
                        
                        logger.info(f"从README提取到构建信息: {json.dumps(result, ensure_ascii=False)}")
                        return result
            
            logger.warning("LLM未能从README中提取有效的构建指令")
            return None
            
        except Exception as e:
            logger.error(f"解析README文件失败: {e}")
            return None

    
    def _get_default_build_command(self, build_system: str) -> str:
        """获取默认构建命令"""
        commands = {
            'cmake': 'mkdir -p build && cd build && cmake .. && make',
            'make': 'make',
            'maven': 'mvn clean package',
            'gradle': './gradlew build',
            'npm': 'npm install && npm run build',
            'cargo': 'cargo build --release',
            'go': 'go build',
            'setuptools': 'python setup.py build',
            'poetry': 'poetry build',
            'sbt': 'sbt compile',
            'meson': 'meson setup build && meson compile -C build',
            'autotools': './configure && make',
            'bazel': 'bazel build //...'
        }
        return commands.get(build_system, 'make')
    
    def _detect_languages(self, project_path: Path) -> List[str]:
        """检测项目使用的编程语言"""
        languages = set()
        
        # 遍历项目文件
        for root, dirs, files in os.walk(project_path):
            # 跳过常见的隐藏目录和构建目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                      ['node_modules', 'build', 'dist', 'target', '__pycache__', 'venv']]
            
            for file in files:
                ext = Path(file).suffix
                if ext in self.language_extensions:
                    languages.add(self.language_extensions[ext])
        
        return sorted(list(languages))
    
    def _get_project_structure(self, project_path: Path, max_files: int = 100) -> List[str]:
        """获取项目文件结构"""
        files = []
        count = 0
        
        for root, dirs, filenames in os.walk(project_path):
            # 跳过隐藏目录和构建目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                      ['node_modules', 'build', 'dist', 'target', '__pycache__', 'venv']]
            
            for filename in filenames:
                if count >= max_files:
                    break
                
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(project_path)
                files.append(str(rel_path))
                count += 1
        
        return files
    
    def _llm_analysis(self, project_info: Dict) -> Dict:
        """使用LLM进行深度项目分析"""
        try:
            prompt = f"""分析以下项目信息，提供详细的构建建议：

项目名称: {project_info['name']}
检测到的构建系统: {project_info['build_system']}
编程语言: {', '.join(project_info['languages'])}
文件列表（前50个）: {', '.join(project_info['files'][:50])}

请提供：
1. 确认或修正构建系统类型
2. 推荐的构建命令（如果当前命令不合适）
3. 可能需要的依赖项
4. 构建注意事项
"""
            
            response = self.llm_client.call_with_tools(
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "provide_build_analysis",
                        "description": "提供项目构建分析结果",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "build_system": {
                                    "type": "string",
                                    "description": "确认的构建系统"
                                },
                                "build_command": {
                                    "type": "string",
                                    "description": "推荐的构建命令"
                                },
                                "dependencies": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "依赖项列表"
                                },
                                "notes": {
                                    "type": "string",
                                    "description": "构建注意事项"
                                }
                            }
                        }
                    }
                }]
            )
            
            # 解析LLM返回的分析结果
            if response.get('tool_calls'):
                for tool_call in response['tool_calls']:
                    if tool_call['function']['name'] == 'provide_build_analysis':
                        args = json.loads(tool_call['function']['arguments'])
                        result = {}
                        if args.get('build_system'):
                            result['build_system'] = args['build_system']
                        if args.get('build_command'):
                            result['build_command'] = args['build_command']
                        if args.get('dependencies'):
                            result['dependencies'] = args['dependencies']
                        if args.get('notes'):
                            result['llm_notes'] = args['notes']
                        return result
            
        except Exception as e:
            logger.warning(f"LLM分析失败: {e}")
        
        return {}
