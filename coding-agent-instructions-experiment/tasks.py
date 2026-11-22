"""14 small, self-contained Python bug-fix tasks for the repo-instructions experiment.

Each task is a dict: id, description (what the function should do), buggy_code (the function
source with one real bug), test_code (a pytest module testing the CORRECT behavior -- it must
fail against buggy_code and pass against the real fix). Bug families are deliberately varied so
the result isn't an artifact of one bug type.
"""

TASKS = [
    {
        "id": "off_by_one_range",
        "description": "Write a function `sum_first_n(nums, n)` that returns the sum of the first n elements of the list nums.",
        "buggy_code": "def sum_first_n(nums, n):\n    total = 0\n    for i in range(n - 1):\n        total += nums[i]\n    return total\n",
        "test_code": "from solution import sum_first_n\n\ndef test_basic():\n    assert sum_first_n([1, 2, 3, 4, 5], 3) == 6\n\ndef test_zero():\n    assert sum_first_n([1, 2, 3], 0) == 0\n\ndef test_full():\n    assert sum_first_n([1, 2, 3], 3) == 6\n",
    },
    {
        "id": "wrong_comparison",
        "description": "Write a function `is_adult(age)` that returns True if age is 18 or older.",
        "buggy_code": "def is_adult(age):\n    return age > 18\n",
        "test_code": "from solution import is_adult\n\ndef test_exactly_18():\n    assert is_adult(18) is True\n\ndef test_17():\n    assert is_adult(17) is False\n\ndef test_30():\n    assert is_adult(30) is True\n",
    },
    {
        "id": "mutable_default_arg",
        "description": "Write a function `add_item(item, bucket=None)` that appends item to bucket (creating a new list by default each call) and returns bucket.",
        "buggy_code": "def add_item(item, bucket=[]):\n    bucket.append(item)\n    return bucket\n",
        "test_code": "from solution import add_item\n\ndef test_independent_calls():\n    first = add_item('a')\n    second = add_item('b')\n    assert first == ['a']\n    assert second == ['b']\n",
    },
    {
        "id": "string_format_bug",
        "description": "Write a function `format_price(cents)` that formats an integer number of cents as a dollar string like '$12.50' (always two decimal places).",
        "buggy_code": "def format_price(cents):\n    dollars = cents / 100\n    return f\"${dollars}\"\n",
        "test_code": "from solution import format_price\n\ndef test_round_number():\n    assert format_price(1250) == '$12.50'\n\ndef test_small():\n    assert format_price(5) == '$0.05'\n\ndef test_whole():\n    assert format_price(100) == '$1.00'\n",
    },
    {
        "id": "wrong_exception_type",
        "description": "Write a function `safe_divide(a, b)` that returns a/b, and raises a ValueError (not ZeroDivisionError) with message 'b must not be zero' when b is 0.",
        "buggy_code": "def safe_divide(a, b):\n    if b == 0:\n        raise ZeroDivisionError('b must not be zero')\n    return a / b\n",
        "test_code": "import pytest\nfrom solution import safe_divide\n\ndef test_normal():\n    assert safe_divide(10, 2) == 5\n\ndef test_zero_raises_value_error():\n    with pytest.raises(ValueError, match='b must not be zero'):\n        safe_divide(10, 0)\n",
    },
    {
        "id": "sort_stability_key",
        "description": "Write a function `sort_by_length_desc(words)` that returns words sorted by length, longest first (ties keep original relative order).",
        "buggy_code": "def sort_by_length_desc(words):\n    return sorted(words, key=len)\n",
        "test_code": "from solution import sort_by_length_desc\n\ndef test_desc_order():\n    assert sort_by_length_desc(['a', 'ccc', 'bb']) == ['ccc', 'bb', 'a']\n\ndef test_ties_keep_order():\n    assert sort_by_length_desc(['aa', 'bb', 'c']) == ['aa', 'bb', 'c']\n",
    },
    {
        "id": "list_copy_bug",
        "description": "Write a function `double_all(nums)` that returns a NEW list with every element doubled, without modifying the input list.",
        "buggy_code": "def double_all(nums):\n    for i in range(len(nums)):\n        nums[i] = nums[i] * 2\n    return nums\n",
        "test_code": "from solution import double_all\n\ndef test_returns_doubled():\n    assert double_all([1, 2, 3]) == [2, 4, 6]\n\ndef test_input_unchanged():\n    original = [1, 2, 3]\n    double_all(original)\n    assert original == [1, 2, 3]\n",
    },
    {
        "id": "dict_get_default",
        "description": "Write a function `count_votes(votes)` that takes a list of candidate name strings and returns a dict mapping each name to how many times it appears.",
        "buggy_code": "def count_votes(votes):\n    counts = {}\n    for v in votes:\n        counts[v] += 1\n    return counts\n",
        "test_code": "from solution import count_votes\n\ndef test_basic():\n    assert count_votes(['a', 'b', 'a', 'a']) == {'a': 3, 'b': 1}\n\ndef test_empty():\n    assert count_votes([]) == {}\n",
    },
    {
        "id": "recursion_base_case",
        "description": "Write a function `factorial(n)` computing n! recursively, with factorial(0) == 1.",
        "buggy_code": "def factorial(n):\n    if n == 1:\n        return 1\n    return n * factorial(n - 1)\n",
        "test_code": "from solution import factorial\n\ndef test_zero():\n    assert factorial(0) == 1\n\ndef test_five():\n    assert factorial(5) == 120\n",
    },
    {
        "id": "string_strip_bug",
        "description": "Write a function `clean_username(name)` that lowercases a username and strips leading/trailing whitespace only (not internal spaces).",
        "buggy_code": "def clean_username(name):\n    return name.lower().replace(' ', '')\n",
        "test_code": "from solution import clean_username\n\ndef test_strips_edges():\n    assert clean_username('  Bob Smith  ') == 'bob smith'\n\ndef test_already_clean():\n    assert clean_username('alice') == 'alice'\n",
    },
    {
        "id": "float_rounding_bug",
        "description": "Write a function `average(nums)` that returns the average of a list of numbers, rounded to 2 decimal places, and returns 0.0 for an empty list (no error).",
        "buggy_code": "def average(nums):\n    return round(sum(nums) / len(nums), 2)\n",
        "test_code": "from solution import average\n\ndef test_basic():\n    assert average([1, 2, 3]) == 2.0\n\ndef test_rounding():\n    assert average([1, 2, 2]) == 1.67\n\ndef test_empty():\n    assert average([]) == 0.0\n",
    },
    {
        "id": "boolean_logic_bug",
        "description": "Write a function `can_checkout(cart_items, is_logged_in)` that returns True only when the cart has at least one item AND the user is logged in.",
        "buggy_code": "def can_checkout(cart_items, is_logged_in):\n    return len(cart_items) >= 0 and is_logged_in\n",
        "test_code": "from solution import can_checkout\n\ndef test_empty_cart_blocked():\n    assert can_checkout([], True) is False\n\ndef test_not_logged_in_blocked():\n    assert can_checkout(['item'], False) is False\n\ndef test_valid_checkout():\n    assert can_checkout(['item'], True) is True\n",
    },
    {
        "id": "index_slice_bug",
        "description": "Write a function `last_n(items, n)` that returns the last n elements of a list in their original order. If n is 0, return an empty list.",
        "buggy_code": "def last_n(items, n):\n    if n == 0:\n        return []\n    return items[-n:-1]\n",
        "test_code": "from solution import last_n\n\ndef test_basic():\n    assert last_n([1, 2, 3, 4, 5], 2) == [4, 5]\n\ndef test_zero():\n    assert last_n([1, 2, 3], 0) == []\n\ndef test_all():\n    assert last_n([1, 2, 3], 3) == [1, 2, 3]\n",
    },
    {
        "id": "accumulator_scope_bug",
        "description": "Write a function `running_totals(nums)` that returns a list of running (cumulative) sums, e.g. [1,2,3] -> [1,3,6].",
        "buggy_code": "def running_totals(nums):\n    result = []\n    total = 0\n    for n in nums:\n        total = n\n        result.append(total)\n    return result\n",
        "test_code": "from solution import running_totals\n\ndef test_basic():\n    assert running_totals([1, 2, 3]) == [1, 3, 6]\n\ndef test_empty():\n    assert running_totals([]) == []\n",
    },
]
