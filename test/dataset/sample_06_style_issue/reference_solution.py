def calculate_average(numbers: list[float]) -> float:
    '''计算数字列表的平均值
    
    Args:
        numbers: 数字列表
        
    Returns:
        平均值，如果列表为空则返回0.0
    '''
    if not numbers:
        return 0.0
    
    total = sum(numbers)
    count = len(numbers)
    return total / count

def find_prime_numbers(limit: int) -> list[int]:
    '''查找小于等于给定限制的所有质数
    
    Args:
        limit: 质数的上限
        
    Returns:
        质数列表
    '''
    if limit < 2:
        return []
    
    primes = []
    for num in range(2, limit + 1):
        # 优化：只需要检查到平方根
        is_prime = True
        for divisor in range(2, int(num ** 0.5) + 1):
            if num % divisor == 0:
                is_prime = False
                break
        
        if is_prime:
            primes.append(num)
    
    return primes

# 可选：使用更高效的筛法
def find_prime_numbers_sieve(limit: int) -> list[int]:
    '''使用埃拉托斯特尼筛法查找质数'''
    if limit < 2:
        return []
    
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    
    return [i for i, prime in enumerate(is_prime) if prime]
