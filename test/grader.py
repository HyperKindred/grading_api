import subprocess
import os
import sys
import tempfile
import json
from pathlib import Path

class CodeGrader:
    """通用代码执行与评分器（支持多文件）"""
    
    def __init__(self, use_docker=False):
        """
        初始化代码执行器
        
        Args:
            use_docker: 是否使用Docker沙箱（当前为False，后续集成）
        """
        self.use_docker = use_docker
        self.project_root = Path(__file__).parent
        
    def run_tests_for_problem(self, problem_id: str) -> str:
        """
        为problems目录中的题目运行测试（保持向后兼容）
        
        Args:
            problem_id: 题目ID，如"two_sum"
            
        Returns:
            测试结果字符串
        """
        problem_dir = self.project_root / "problems" / problem_id
        test_file = problem_dir / "test_cases.py"
        
        if not test_file.exists():
            return f"错误：找不到测试文件 {test_file}"
        
        # 读取学生代码
        student_code_file = problem_dir / "student_code.py"
        if student_code_file.exists():
            with open(student_code_file, 'r', encoding='utf-8') as f:
                student_code = f.read()
        else:
            student_code = "# 默认学生代码"
        
        return self._execute_code_with_tests(student_code, str(test_file), str(problem_dir))
    
    def run_tests_for_dataset_sample(self, sample_data: dict) -> str:
        """
        为数据集样本运行测试（增强版，支持多文件）
        
        Args:
            sample_data: 包含以下字段的字典:
                - student_code: 学生代码字符串（必需）
                - test_cases: 测试用例代码字符串（必需）
                - reference_solution: 参考解决方案代码字符串（可选）
                - additional_files: 其他文件字典 {文件名: 内容}（可选）
                - sample_id: 样本ID（可选，用于日志）
                
        Returns:
            测试结果字符串
        """
        student_code = sample_data.get('student_code', '')
        test_cases = sample_data.get('test_cases', '')
        
        if not student_code:
            return "错误：未提供学生代码"
        if not test_cases:
            return "错误：未提供测试用例"
        
        # 构建文件字典
        files = {
            'student_code.py': student_code,
            'test_cases.py': test_cases
        }
        
        # 添加参考解决方案（如果提供）
        reference_solution = sample_data.get('reference_solution', '')
        if reference_solution:
            files['reference_solution.py'] = reference_solution
        
        # 添加其他文件
        additional_files = sample_data.get('additional_files', {})
        if additional_files:
            files.update(additional_files)
        
        return self._execute_with_multiple_files(files, sample_data.get('sample_id', 'unknown'))
    
    def _execute_with_multiple_files(self, files: dict, sample_id: str = '') -> str:
        """
        执行多个文件的测试
        
        Args:
            files: 文件名到内容的字典
            sample_id: 样本ID（用于日志）
            
        Returns:
            测试结果字符串
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            print(f"  [DEBUG] 临时目录: {temp_dir}")
            
            # 写入所有文件
            for filename, content in files.items():
                file_path = temp_path / filename
                file_path.write_text(content, encoding='utf-8')
                print(f"  [DEBUG] 写入文件: {filename} ({len(content)} 字符)")
            
            # 找到测试文件
            test_file = temp_path / "test_cases.py"
            if not test_file.exists():
                # 尝试找其他测试文件
                test_files = [f for f in temp_path.iterdir() if 'test' in f.name.lower() and f.suffix == '.py']
                if test_files:
                    test_file = test_files[0]
                else:
                    return "错误：未找到测试文件"
            
            print(f"  [DEBUG] 使用测试文件: {test_file}")
            
            # 确保临时目录在Python路径中，以便导入
            env = os.environ.copy()
            env['PYTHONPATH'] = f"{temp_dir}{os.pathsep}{env.get('PYTHONPATH', '')}"
            
            # 执行测试
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=30,  # 增加超时时间
                    cwd=temp_dir,
                    env=env
                )
                
                output = f"测试退出码: {result.returncode}\n"
                output += f"标准输出:\n{result.stdout}\n"
                if result.stderr:
                    output += f"标准错误:\n{result.stderr}\n"
                
                return output.strip()
                
            except subprocess.TimeoutExpired:
                return f"错误：测试运行超时（可能代码有死循环或效率问题）。样本ID: {sample_id}"
            except Exception as e:
                return f"运行测试时发生异常：{str(e)}。样本ID: {sample_id}"
    
    def _execute_code_with_tests(self, student_code: str, test_file_path: str, 
                                 working_dir: str = None) -> str:
        """
        通用代码执行方法（保持向后兼容）
        
        Args:
            student_code: 学生代码字符串
            test_file_path: 测试文件路径
            working_dir: 工作目录（可选）
            
        Returns:
            测试结果字符串
        """
        test_path = Path(test_file_path)
        if not working_dir:
            working_dir = str(test_path.parent)
        
        # 在指定目录创建/覆盖student_code.py
        student_code_file = Path(working_dir) / "student_code.py"
        with open(student_code_file, 'w', encoding='utf-8') as f:
            f.write(student_code)
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file_path, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=working_dir
            )
            
            output = f"测试退出码: {result.returncode}\n"
            output += f"标准输出:\n{result.stdout}\n"
            if result.stderr:
                output += f"标准错误:\n{result.stderr}\n"
            
            return output.strip()
            
        except subprocess.TimeoutExpired:
            return "错误：测试运行超时（可能代码有死循环）。"
        except Exception as e:
            return f"运行测试时发生异常：{str(e)}"
    
    def analyze_test_results(self, test_output: str) -> dict:
        """
        分析测试输出结果，提取结构化信息
        
        Args:
            test_output: 测试输出的字符串
            
        Returns:
            结构化的分析结果
        """
        result = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'success_rate': 0,
            'has_timeout': False,
            'has_errors': False,
            'summary': ''
        }
        
        if not test_output:
            return result
        
        # 分析pytest输出
        lines = test_output.split('\n')
        
        # 统计测试用例数量
        test_count_started = False
        for line in lines:
            line_lower = line.lower()
            
            # 检查超时
            if 'timeout' in line_lower or '超时' in line:
                result['has_timeout'] = True
            
            # 检查语法错误
            if 'syntaxerror' in line_lower or '语法错误' in line_lower:
                result['has_errors'] = True
            
            # 统计收集到的测试数量
            if 'collected' in line_lower and 'item' in line_lower:
                # 例如: "collected 3 items"
                parts = line_lower.split()
                for part in parts:
                    if part.isdigit():
                        result['total_tests'] = int(part)
                        break
            
            # 统计通过/失败/错误（pytest输出格式）
            if '::' in line:
                if 'passed' in line_lower:
                    result['passed'] += 1
                elif 'failed' in line_lower:
                    result['failed'] += 1
                elif 'error' in line_lower:
                    result['errors'] += 1
                    result['has_errors'] = True
        
        # 如果通过解析没找到总数，则使用通过+失败+错误的总和
        if result['total_tests'] == 0:
            result['total_tests'] = result['passed'] + result['failed'] + result['errors']
        
        # 计算通过率
        if result['total_tests'] > 0:
            result['success_rate'] = (result['passed'] / result['total_tests']) * 100
        
        # 生成摘要
        if result['has_timeout']:
            result['summary'] = "测试超时（可能代码有死循环或效率问题）"
        elif result['has_errors']:
            result['summary'] = f"测试出错：{result['passed']}通过，{result['failed']}失败，{result['errors']}错误"
        elif result['total_tests'] == 0:
            result['summary'] = "未找到有效测试结果"
        else:
            result['summary'] = f"测试完成：{result['passed']}/{result['total_tests']}通过 ({result['success_rate']:.1f}%)"
        
        return result


# 保持向后兼容的函数
def run_tests(problem_id: str) -> str:
    """向后兼容的包装函数（用于problems目录）"""
    grader = CodeGrader()
    return grader.run_tests_for_problem(problem_id)


# 测试函数
def test_grader():
    """测试代码执行器"""
    grader = CodeGrader()
    
    print("测试1: 检查problems目录中的demo问题")
    result1 = grader.run_tests_for_problem("demo")
    print(f"结果长度: {len(result1)}")
    print(f"前200字符: {result1[:200]}..." if len(result1) > 200 else result1)
    
    print("\n" + "="*60)
    print("测试2: 多文件测试")
    
    # 测试数据
    student_code = """
def add(a, b):
    return a + b
"""
    
    test_cases = """
def test_add():
    assert add(1, 2) == 3
    
def test_add_negative():
    assert add(-1, -2) == -3
"""
    
    sample_data = {
        'student_code': student_code,
        'test_cases': test_cases,
        'sample_id': 'test_multi_file'
    }
    
    result2 = grader.run_tests_for_dataset_sample(sample_data)
    print(f"多文件测试结果:\n{result2}")
    
    # 分析结果
    analysis = grader.analyze_test_results(result2)
    print(f"\n分析结果: {json.dumps(analysis, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    test_grader()