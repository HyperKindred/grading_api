def get_middle_element(lst):
    # 边界条件错误：没有处理空列表和单元素列表
    middle_index = len(lst) // 2
    return lst[middle_index]

# 示例
print(get_middle_element([1, 2, 3, 4, 5]))  # 正常：3
print(get_middle_element([1, 2, 3, 4]))     # 正常：3（Python索引向下取整）
print(get_middle_element([]))               # IndexError
print(get_middle_element([1]))              # 正常：1
