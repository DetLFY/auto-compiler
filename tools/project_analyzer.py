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
            'files': []
        }
        
        # 1. 检测构建系统
        build_info = self._detect_build_system(project_path)
        project_info.update(build_info)
        
        # 2. 扫描文件识别编程语言
        languages = self._detect_languages(project_path)
        project_info['languages'] = languages
        
        # 3. 获取项目文件列表（用于LLM分析）
        project_files = self._get_project_structure(project_path)
        project_info['files'] = project_files
        
        # 4. 使用LLM进行深度分析
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
