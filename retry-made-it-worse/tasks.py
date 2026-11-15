"""12 Python function-writing tasks for the retry experiment. The first set
(easy list/string utilities) produced a ceiling effect against llama3.1:8b --
11 of 12 passed the baseline attempt with zero failures, leaving no signal to
study retry dynamics on. This set replaces most of them with classic
algorithmic interview problems chosen specifically because small local models
tend to get a known edge case wrong (tie-breaking, off-by-one, double-zero
traps, single-column matrices, etc), while keeping `rotate_list` and
`merge_intervals` (expanded with harder cases) since they already produced a
genuine, informative baseline failure. Prompts give a signature and spec only
-- never the edge-case behaviour itself."""

TASKS = [
    {
        "id": "rotate_list",
        "func": "rotate_list",
        "prompt": (
            "Write a Python function `rotate_list(lst, k)` that returns a new list "
            "which is `lst` rotated to the right by `k` positions. `k` can be larger "
            "than the length of `lst`, zero, or negative (rotate left). If `lst` is "
            "empty, return an empty list. Return only the function, no example usage."
        ),
        "test_inputs": [
            ([1, 2, 3, 4, 5], 2),
            ([1, 2, 3, 4, 5], 7),
            ([1, 2, 3, 4, 5], -1),
            ([1, 2, 3], 0),
            ([1], 5),
            ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 13),
        ],
    },
    {
        "id": "merge_intervals",
        "func": "merge_intervals",
        "prompt": (
            "Write a Python function `merge_intervals(intervals)` that takes a list "
            "of (start, end) tuples/lists and returns a new list of merged, "
            "non-overlapping intervals as tuples, sorted by start. Two intervals "
            "that touch (e.g. end of one equals start of the next) should also be "
            "merged. Return only the function, no example usage, no explanation."
        ),
        "test_inputs": [
            ([(1, 3), (2, 6), (8, 10), (15, 18)],),
            ([(1, 4), (4, 5)],),
            ([(1, 4), (0, 4)],),
            ([(1, 10), (2, 3), (4, 5), (6, 7)],),
            ([(5, 5)],),
            ([],),
        ],
    },
    {
        "id": "longest_substring_without_repeat",
        "func": "longest_substring_without_repeat",
        "prompt": (
            "Write a Python function `longest_substring_without_repeat(s)` that "
            "returns the length of the longest substring of `s` that contains no "
            "repeated characters. Return only the function, no example usage, no "
            "explanation."
        ),
        "test_inputs": [
            ("abcabcbb",),
            ("bbbbb",),
            ("pwwkew",),
            ("",),
            ("dvdf",),
            ("abba",),
        ],
    },
    {
        "id": "next_greater_permutation",
        "func": "next_greater_permutation",
        "prompt": (
            "Write a Python function `next_greater_permutation(digits)` that takes "
            "a list of digits representing a number and returns a new list that is "
            "the next permutation of those digits in lexicographic order (the "
            "smallest arrangement that is strictly greater than the input). If the "
            "input is already the highest possible permutation, return the digits "
            "sorted in ascending order instead (wrap around to the smallest). "
            "Return only the function, no example usage, no explanation."
        ),
        "test_inputs": [
            ([1, 2, 3],),
            ([3, 2, 1],),
            ([1, 1, 5],),
            ([2, 3, 1],),
            ([1],),
        ],
    },
    {
        "id": "int_to_roman",
        "func": "int_to_roman",
        "prompt": (
            "Write a Python function `int_to_roman(n)` that converts an integer "
            "`n` (between 1 and 3999) into its standard Roman numeral string "
            "representation, using the subtractive notation (e.g. 4 is 'IV', not "
            "'IIII'). Return only the function, no example usage, no explanation."
        ),
        "test_inputs": [
            (3749,),
            (58,),
            (1994,),
            (4,),
            (9,),
            (3999,),
        ],
    },
    {
        "id": "run_length_encode",
        "func": "run_length_encode",
        "prompt": (
            "Write a Python function `run_length_encode(s)` that compresses the "
            "string `s` by replacing each run of consecutive identical characters "
            "with the run's length followed by the character (e.g. consecutive runs "
            "of the same character get combined, but non-consecutive occurrences of "
            "the same character do not get merged together). If `s` is empty, "
            "return an empty string. Return only the function, no example usage."
        ),
        "test_inputs": [
            ("aaabbc",),
            ("abcd",),
            ("",),
            ("aaaa",),
            ("aabbaa",),
        ],
    },
    {
        "id": "leftmost_insert_position",
        "func": "leftmost_insert_position",
        "prompt": (
            "Write a Python function `leftmost_insert_position(sorted_list, "
            "target)` that returns the leftmost index at which `target` could be "
            "inserted into `sorted_list` (which is sorted in ascending order) while "
            "keeping it sorted. If `target` already appears in the list, return the "
            "index of its first (leftmost) occurrence, not after it. Return only "
            "the function, no example usage, no explanation."
        ),
        "test_inputs": [
            ([1, 3, 3, 5, 7], 3),
            ([1, 2, 4, 4, 4, 8], 4),
            ([1, 2, 3], 5),
            ([1, 2, 3], 0),
            ([], 5),
        ],
    },
    {
        "id": "spiral_order",
        "func": "spiral_order",
        "prompt": (
            "Write a Python function `spiral_order(matrix)` that takes a 2D list "
            "`matrix` (a list of rows, not necessarily square) and returns a flat "
            "list of all its elements visited in clockwise spiral order, starting "
            "from the top-left element. Return only the function, no example usage, "
            "no explanation."
        ),
        "test_inputs": [
            ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],),
            ([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],),
            ([[1]],),
            ([[1, 2], [3, 4]],),
            ([[1], [2], [3]],),
        ],
    },
    {
        "id": "group_anagrams",
        "func": "group_anagrams",
        "prompt": (
            "Write a Python function `group_anagrams(words)` that groups the "
            "strings in `words` into lists of anagrams of each other, and returns a "
            "list of those groups. The groups must be returned in a DETERMINISTIC "
            "order: sort the groups by their sorted-letters key (e.g. the group for "
            "'eat' has key 'aet'), and keep the words within each group in the order "
            "they first appeared in `words`. Return only the function, no example "
            "usage, no explanation."
        ),
        "test_inputs": [
            (["eat", "tea", "tan", "ate", "nat", "bat"],),
            ([""],),
            (["a"],),
            (["ab", "ba", "abc"],),
        ],
    },
    {
        "id": "valid_parenthesis_with_star",
        "func": "valid_parenthesis_with_star",
        "prompt": (
            "Write a Python function `valid_parenthesis_with_star(s)` that returns "
            "True if the string `s`, which contains only the characters '(', ')' "
            "and '*', can be interpreted as a valid, balanced parenthesis sequence. "
            "Each '*' can be treated as '(', as ')', or as an empty string, your "
            "choice, independently for each '*'. Return only the function, no "
            "example usage, no explanation."
        ),
        "test_inputs": [
            ("()",),
            ("(*)",),
            ("(*))",),
            ("((*)",),
            (")(",),
            ("(((*)",),
        ],
    },
    {
        "id": "majority_element",
        "func": "majority_element",
        "prompt": (
            "Write a Python function `majority_element(nums)` that returns the "
            "value that appears more than n/2 times in the list `nums` (you may "
            "assume such a value always exists when `nums` is non-empty). If "
            "`nums` is empty, raise a ValueError. Write an approach that uses O(1) "
            "extra space, not a counting dictionary. Return only the function, no "
            "example usage, no explanation."
        ),
        "test_inputs": [
            ([3, 2, 3],),
            ([2, 2, 1, 1, 1, 2, 2],),
            ([1],),
            ([6, 5, 5],),
        ],
    },
    {
        "id": "decode_ways",
        "func": "decode_ways",
        "prompt": (
            "Write a Python function `decode_ways(s)` where `s` is a string of "
            "digits. Each letter A-Z was encoded as a number 1-26 (A=1, ..., Z=26) "
            "and the resulting numbers were concatenated into `s` with no "
            "separators. Return the total number of distinct ways `s` could have "
            "been decoded back into letters. Return only the function, no example "
            "usage, no explanation."
        ),
        "test_inputs": [
            ("12",),
            ("226",),
            ("06",),
            ("27",),
            ("11106",),
            ("100",),
        ],
    },
]
