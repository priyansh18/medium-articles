"""Chain-of-thought judge prompt: solve the problem yourself first, then compare."""


def cot_judge_prompt(task_prompt, candidate_answer_text):
    return (
        "You are grading a student's solution to a word problem. First solve the problem "
        "yourself from scratch, showing your own work, and state your own final number on a "
        "line that starts with exactly: MY ANSWER: <number>. Then compare your answer to the "
        "student's final answer below. On the very last line, state your verdict as exactly: "
        "VERDICT: CORRECT or VERDICT: INCORRECT.\n\n"
        f"PROBLEM:\n{task_prompt}\n\n"
        f"STUDENT SOLUTION:\n{candidate_answer_text}\n"
    )
