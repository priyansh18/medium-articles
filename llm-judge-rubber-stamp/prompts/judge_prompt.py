"""Plain one-shot judge prompt: grade without solving the problem yourself."""


def judge_prompt(task_prompt, candidate_answer_text):
    return (
        "You are grading a student's solution to a word problem. Decide only whether the "
        "student's FINAL numeric answer is correct or incorrect for the problem below. "
        "Reply with exactly one word on the first line: CORRECT or INCORRECT.\n\n"
        f"PROBLEM:\n{task_prompt}\n\n"
        f"STUDENT SOLUTION:\n{candidate_answer_text}\n\n"
        "Verdict (CORRECT or INCORRECT):"
    )
