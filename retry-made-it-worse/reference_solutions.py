"""Ground-truth reference implementations used only to compute expected test
outputs (never shown to the model). Correctness of each is what the grading
in run_experiment.py relies on; each was sanity-checked by hand against known
values before being used as the oracle (see run log notes in the article's
reproducibility repo)."""

def rotate_list(lst, k):
    if not lst:
        return []
    n = len(lst)
    k = k % n
    return lst[-k:] + lst[:-k] if k else list(lst)

def merge_intervals(intervals):
    if not intervals:
        return []
    s = sorted(intervals, key=lambda x: x[0])
    out = [list(s[0])]
    for start, end in s[1:]:
        if start <= out[-1][1]:
            out[-1][1] = max(out[-1][1], end)
        else:
            out.append([start, end])
    return [tuple(x) for x in out]

def longest_substring_without_repeat(s):
    seen = {}
    start = 0
    best = 0
    for i, c in enumerate(s):
        if c in seen and seen[c] >= start:
            start = seen[c] + 1
        seen[c] = i
        best = max(best, i - start + 1)
    return best

def next_greater_permutation(digits):
    d = list(digits)
    n = len(d)
    i = n - 2
    while i >= 0 and d[i] >= d[i + 1]:
        i -= 1
    if i == -1:
        return sorted(d)
    j = n - 1
    while d[j] <= d[i]:
        j -= 1
    d[i], d[j] = d[j], d[i]
    d[i + 1:] = list(reversed(d[i + 1:]))
    return d

def int_to_roman(n):
    vals = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'),
            (90, 'XC'), (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'),
            (5, 'V'), (4, 'IV'), (1, 'I')]
    out = []
    for v, sym in vals:
        while n >= v:
            out.append(sym)
            n -= v
    return ''.join(out)

def run_length_encode(s):
    if not s:
        return ""
    out = []
    cur = s[0]
    cnt = 1
    for c in s[1:]:
        if c == cur:
            cnt += 1
        else:
            out.append(f"{cnt}{cur}")
            cur = c
            cnt = 1
    out.append(f"{cnt}{cur}")
    return ''.join(out)

def leftmost_insert_position(sorted_list, target):
    lo, hi = 0, len(sorted_list)
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_list[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def spiral_order(matrix):
    if not matrix or not matrix[0]:
        return []
    res = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            res.append(matrix[top][c])
        top += 1
        for r in range(top, bottom + 1):
            res.append(matrix[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                res.append(matrix[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                res.append(matrix[r][left])
            left += 1
    return res

def group_anagrams(words):
    groups = {}
    for w in words:
        key = ''.join(sorted(w))
        groups.setdefault(key, []).append(w)
    return [groups[k] for k in sorted(groups)]

def valid_parenthesis_with_star(s):
    lo = hi = 0
    for c in s:
        if c == '(':
            lo += 1
            hi += 1
        elif c == ')':
            lo -= 1
            hi -= 1
        else:
            lo -= 1
            hi += 1
        if hi < 0:
            return False
        lo = max(lo, 0)
    return lo == 0

def majority_element(nums):
    if not nums:
        raise ValueError("empty list")
    count = 0
    candidate = None
    for n in nums:
        if count == 0:
            candidate = n
            count = 1
        elif n == candidate:
            count += 1
        else:
            count -= 1
    return candidate

def decode_ways(s):
    if not s or s[0] == '0':
        return 0
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = 0
        if s[i - 1] != '0':
            dp[i] += dp[i - 1]
        two = int(s[i - 2:i])
        if 10 <= two <= 26:
            dp[i] += dp[i - 2]
    return dp[n]

REFS = {
    "rotate_list": rotate_list,
    "merge_intervals": merge_intervals,
    "longest_substring_without_repeat": longest_substring_without_repeat,
    "next_greater_permutation": next_greater_permutation,
    "int_to_roman": int_to_roman,
    "run_length_encode": run_length_encode,
    "leftmost_insert_position": leftmost_insert_position,
    "spiral_order": spiral_order,
    "group_anagrams": group_anagrams,
    "valid_parenthesis_with_star": valid_parenthesis_with_star,
    "majority_element": majority_element,
    "decode_ways": decode_ways,
}
