def reverse_two_digit(n: int) -> int:
    # 提取十位和个位
    tens = n // 10
    ones = n % 10
    # 反转后组成新数：原个位变为十位，原十位变为个位
    reversed_num = ones * 10 + tens
    return reversed_num