def calculate_average(numbers):
    if len(numbers) == 0:
        return 0  # 或者抛出异常，根据需求决定
    total = sum(numbers)
    count = len(numbers)
    return total / count
