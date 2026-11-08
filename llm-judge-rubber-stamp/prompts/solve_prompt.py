"""Prompt template used to make the candidate model solve each word problem."""


def solve_prompt(task_prompt):
    return (
        f"{task_prompt}\n\n"
        "Think briefly, then give your final numeric answer on the last line as exactly: "
        "FINAL ANSWER: <number>"
    )
