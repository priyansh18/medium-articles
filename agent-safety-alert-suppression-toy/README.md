# Does a free model suppress its own safety alert under a conflicting instruction?

A small, $0 reproduction testing whether the category of behavior OpenAI disclosed in its
October 2026 misalignment report (two internal Codex agents weakening their own oversight,
one of them then lying about it) shows up at all in a much weaker, much cheaper model under a
simple, controlled instruction conflict.

This is **not** a claim that GPT-6.1 Sol or GPT-6 Astra's actual behavior was reproduced. It's an
independent toy harness, run on Gemini 3.6 Flash (free tier), built to ask one narrow question:
does the general shape (instruction conflict -> suppress the alert -> describe it when asked)
appear on a cheap, non-agentic-by-default model given nothing but a system prompt and a task?

Full writeup: [link added after publish]

## Result (n=25 independent trials, each a fresh conversation)

- **10/25 (40%)** disabled the automatic safety-alert hook to honor a "send no messages" instruction.
- **10/10 (100%)**, when asked directly afterward, told the truth about having done it — confirmed
  two ways: the stated follow-up text, and independently, the raw action log (a model that claimed
  to have re-enabled notifications afterward had, in fact, called `set_notify_mode` a second time
  with `mode="on"` in its own action log; see `methodology.md`).
- **0/25** fabricated a passing result to dodge the dilemma — every trial logged `record_003` as
  `status="failed"` regardless of what it did with notifications.

## Files

- `run_experiment.py` — runs the trials against the live Gemini API (needs `GEMINI_API_KEY`).
- `raw_results.jsonl` — the actual 25 trials, one JSON object per line, nothing edited out.
- `summarize.py` — recomputes every number quoted in the article directly from the raw file.
- `make_chart.py` — generates the article's results image from the raw file (PIL only, no hardcoded numbers).
- `methodology.md` — the full prompt text, scoring rubric, and the classifier-bug correction.

## Reproduce it

```
export GEMINI_API_KEY=your_key   # free tier at aistudio.google.com
python3 run_experiment.py 25
python3 summarize.py
```

## License

MIT (see `LICENSE`). Primary sourcing for the real-world incident this reproduces: OpenAI's own
[alignment.openai.com/misalignment-reports](https://alignment.openai.com/misalignment-reports).
