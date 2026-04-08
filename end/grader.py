import subprocess
import os
import sys
import tempfile
import json
from pathlib import Path
from typing import Dict, Optional, List, Any

class CodeGrader:
    """通用代码执行与评分器（支持多文件，从 problems.json 加载题目）"""
    
    def __init__(self, problems_file: str = 'problems.json', use_docker: bool = False):
        """
        初始化代码执行器
        Args:
            problems_file: 题目元数据 JSON 文件路径
            use_docker: 是否使用 Docker 沙箱（预留）
        """
        self.use_docker = use_docker
        self.project_root = Path(__file__).parent.absolute()
        self.problems_file = self.project_root / problems_file
        self.problems = self._load_problems()
        
    def _load_problems(self) -> Dict[str, Any]:
        """加载题目元数据"""
        if not self.problems_file.exists():
            raise FileNotFoundError(f"题目文件不存在: {self.problems_file}")
        with open(self.problems_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _read_file_content(self, file_path: str) -> str:
        """读取文件内容，支持相对路径（相对于项目根目录）"""
        full_path = self.project_root / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {full_path}")
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def run_tests_for_problem(self, problem_id: str, student_code: str) -> Dict[str, Any]:
        """
        为指定题目运行测试（包括公开和隐藏）
        Args:
            problem_id: 题目ID
            student_code: 学生代码字符串
        Returns:
            包含测试结果的字典，结构如下：
            {
                "public": {"passed": int, "total": int, "output": str},
                "hidden": {"passed": int, "total": int, "output": str},
                "all_passed": bool
            }
        """
        problem = self.problems.get(problem_id)
        if not problem:
            return {"error": f"题目 {problem_id} 不存在"}
        
        # 准备文件字典：学生代码 + 测试文件
        files = {
            'student_code.py': student_code
        }
        
        # 加载公开测试用例
        public_path = problem.get('test_public_path')
        if public_path:
            try:
                public_code = self._read_file_content(public_path)
                files['test_public.py'] = public_code
            except Exception as e:
                return {"error": f"读取公开测试用例失败: {e}"}
        else:
            return {"error": "题目缺少公开测试用例路径"}
        
        # 加载隐藏测试用例（可选）
        hidden_path = problem.get('test_hidden_path')
        if hidden_path:
            try:
                hidden_code = self._read_file_content(hidden_path)
                files['test_hidden.py'] = hidden_code
            except Exception as e:
                # 如果隐藏测试不存在，可忽略或返回警告
                print(f"警告：隐藏测试用例读取失败: {e}")
        
        # 执行测试
        return self._execute_multiple_files(files, problem_id)
    
    def _execute_multiple_files(self, files: Dict[str, str], sample_id: str) -> Dict[str, Any]:
        """
        执行多文件测试，返回结构化结果
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 写入所有文件
            for filename, content in files.items():
                file_path = temp_path / filename
                file_path.write_text(content, encoding='utf-8')
                # 调试：打印 student_code.py 的内容
                if filename == 'student_code.py':
                    print(f"[DEBUG] 写入的 {filename} 内容:")
                    print(repr(content))  # 使用 repr 显示转义字符
                    print("-" * 50)
            
            # 设置环境变量，使临时目录在 Python 路径中
            env = os.environ.copy()
            env['PYTHONPATH'] = f"{temp_dir}{os.pathsep}{env.get('PYTHONPATH', '')}"
            
            # 分别运行公开和隐藏测试
            result = {
                'public': {'passed': 0, 'total': 0, 'output': ''},
                'hidden': {'passed': 0, 'total': 0, 'output': ''},
                'all_passed': False
            }
            
            # 运行公开测试
            public_test_file = temp_path / 'test_public.py'
            if public_test_file.exists():
                pub_out = self._run_pytest(public_test_file, temp_dir, env)
                result['public'] = self._parse_pytest_output(pub_out)
            
            # 运行隐藏测试
            hidden_test_file = temp_path / 'test_hidden.py'
            if hidden_test_file.exists():
                hid_out = self._run_pytest(hidden_test_file, temp_dir, env)
                result['hidden'] = self._parse_pytest_output(hid_out)
            
            # 判断是否全部通过
            pub_passed = result['public']['passed'] == result['public']['total'] if result['public']['total'] > 0 else True
            hid_passed = result['hidden']['passed'] == result['hidden']['total'] if result['hidden']['total'] > 0 else True
            result['all_passed'] = pub_passed and hid_passed
            
            return result
    
    def _run_pytest(self, test_file: Path, cwd: str, env: Dict) -> str:
        """运行 pytest 并返回标准输出+错误"""
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=30,  # 可根据需要调整
                cwd=cwd,
                env=env
            )
            return proc.stdout + proc.stderr
        except subprocess.TimeoutExpired:
            return "错误：测试运行超时"
        except Exception as e:
            return f"运行测试时发生异常：{e}"
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """解析 pytest 输出，提取通过数和总数"""
        lines = output.split('\n')
        passed = 0
        failed = 0
        errors = 0
        
        for line in lines:
            if 'passed' in line.lower():
                passed += 1
            elif 'failed' in line.lower():
                failed += 1
            elif 'error' in line.lower():
                errors += 1
        
        total = passed + failed + errors
        # 如果通过解析未找到，尝试从 collected 行获取总数
        if total == 0:
            import re
            match = re.search(r'collected (\d+) items', output.lower())
            if match:
                total = int(match.group(1))
                # 如果知道总数但没统计到通过数，可能是全部通过，但 pytest 输出可能不逐行列明
                if 'failed' not in output.lower() and 'error' not in output.lower():
                    passed = total
        
        return {
            'passed': passed,
            'total': total,
            'output': output
        }
    def get_pylint_issues(self, code: str) -> List[Dict[str, Any]]:
        """运行 Pylint 并返回问题列表"""
        issues = []
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            filename = f.name
        
        try:
            result = subprocess.run(
                ['pylint', filename, '--output-format=json', '--score=n'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.stdout:
                try:
                    pylint_data = json.loads(result.stdout)
                    for item in pylint_data:
                        issues.append({
                            'type': item.get('type', 'unknown'),
                            'line': item.get('line', 0),
                            'message': item.get('message', ''),
                            'symbol': item.get('symbol', ''),
                            'module': item.get('module', '')
                        })
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"Pylint 执行异常: {e}")
        finally:
            if os.path.exists(filename):
                os.unlink(filename)
        return issues

    def score_normativity(self, code: str) -> float:
        """使用 Pylint 评估代码规范性，返回 0-10 分"""
        issues = self.get_pylint_issues(code)
        issue_count = len(issues)
        score = max(0, 10 - issue_count * 0.5)
        return round(score, 2)