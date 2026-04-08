def calculate_average(numbers):
    # 逻辑错误：没有检查空列表，会导致除以零错误
    total = sum(numbers)
    count = len(numbers)
    return total / count  # 如果numbers为空，这里会报错：ZeroDivisionError
