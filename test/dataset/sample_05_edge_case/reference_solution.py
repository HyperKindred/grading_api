def get_middle_element(lst):
    # 正确处理边界条件
    if not lst:  # 空列表
        return None
    
    middle_index = len(lst) // 2
    return lst[middle_index]

# 更完善的版本
def get_middle_element_robust(lst):
    if not lst:
        return None
    
    # 如果列表有偶数个元素，返回中间两个元素的平均值
    if len(lst) % 2 == 0:
        mid1 = lst[len(lst) // 2 - 1]
        mid2 = lst[len(lst) // 2]
        return (mid1 + mid2) / 2
    else:
        return lst[len(lst) // 2]

# 示例
print(get_middle_element([1, 2, 3, 4, 5]))  # 3
print(get_middle_element([]))               # None
