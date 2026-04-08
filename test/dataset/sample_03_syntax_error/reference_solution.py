def find_maximum(numbers):
    # 正确的语法
    if len(numbers) == 0:
        return None
    
    max_num = numbers[0]
    for num in numbers[1:]:
        if num > max_num:
            max_num = num
    
    return max_num
