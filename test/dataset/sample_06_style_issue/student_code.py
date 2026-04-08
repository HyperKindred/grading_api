def calc(lst):
    # 代码风格问题：函数名不清晰，变量名随意
    s = 0
    c = 0
    for x in lst:
        s = s + x
        c = c + 1
    if c == 0:
        return 0
    a = s / c
    return a

def FindPrimeNumbers(n):
    # 更多风格问题：不一致的命名，魔法数字，冗余注释
    primes = []
    for num in range(2, n+1):
        is_prime = True
        for i in range(2, num):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes
