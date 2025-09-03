def subset_sum(nums, target, i=0, memo=None):
    if memo is None:
        memo = {}

    # key memoización
    key = (i, target)
    if key in memo:
        return memo[key]

    # casos base
    if target == 0:
        return True
    if i >= len(nums) or target < 0:
        return False

    #  incluir nums[i]
    include = subset_sum(nums, target - nums[i], i + 1, memo)
    #  excluir nums[i]
    exclude = subset_sum(nums, target, i + 1, memo)

    memo[key] = include or exclude
    return memo[key]


nums = [3, 34, 4, 12, 5, 2]
target = 9
print(subset_sum(nums, target))

