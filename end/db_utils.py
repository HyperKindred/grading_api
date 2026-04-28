import json
from db_config import get_db_connection

def save_or_update_submission(problem_id, student_id, code, scores_dict, feedback):
    """保存或更新提交记录，如果已存在则更新，并设置 schange = 1"""
    scores_json = json.dumps(scores_dict)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # 检查是否存在
        cursor.execute(
            "SELECT id FROM submissions WHERE problem_id = %s AND student_id = %s",
            (problem_id, student_id)
        )
        existing = cursor.fetchone()
        if existing:
            cursor.execute(
                """UPDATE submissions 
                   SET code = %s, scores_json = %s, feedback = %s, schange = 1, updated_at = NOW()
                   WHERE problem_id = %s AND student_id = %s""",
                (code, scores_json, feedback, problem_id, student_id)
            )
        else:
            cursor.execute(
                """INSERT INTO submissions (problem_id, student_id, code, scores_json, feedback, schange)
                   VALUES (%s, %s, %s, %s, %s, 1)""",
                (problem_id, student_id, code, scores_json, feedback)
            )
        conn.commit()

def get_student_submission(problem_id, student_id):
    """获取某学生某题的提交记录（用于前端加载已有分数等）"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT code, scores_json, feedback, created_at, updated_at, tchange FROM submissions "
            "WHERE problem_id = %s AND student_id = %s",
            (problem_id, student_id)
        )
        row = cursor.fetchone()
        if row:
            return {
                'code': row['code'],
                'scores': json.loads(row['scores_json']),
                'feedback': row['feedback'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'tchange': row['tchange']
            }
        return None

def mark_tchange_read(problem_id, student_id):
    """学生查看反馈后，清除 tchange 标记"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE submissions SET tchange = 0 WHERE problem_id = %s AND student_id = %s",
            (problem_id, student_id)
        )
        conn.commit()