class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        n = len(nums)
        for i in range(n):
            for j in range(i + 1, n):  # 典型的O(n²)暴力解法
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []  # 虽然正确，但效率低