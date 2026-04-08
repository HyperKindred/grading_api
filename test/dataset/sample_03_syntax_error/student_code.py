def find_maximum(numbers):
    # 语法错误：if语句缺少冒号
    if len(numbers) == 0
        return None
    
    max_num = numbers[0]
    for num in numbers[1:]:
        if num > max_num:
            max_num = num
    
    return max_num
