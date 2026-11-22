# Numeric breakdown: coding-agent-instructions-experiment

Source data: `raw_results.jsonl` (42 rows, one per task x condition pair).

## Pass rate per condition

| Condition | Pass | Total | Pass rate |
|---|---|---|---|
| none | 14 | 14 | 100.0% |
| concise | 13 | 14 | 92.9% |
| long | 13 | 14 | 92.9% |

## Task-level detail

Every task passed in all three conditions except `string_strip_bug`, which failed under both
`concise` and `long` and passed under `none`. See `failure_examples/string_strip_bug_instruction_anchoring.md`
for the full response diff on that task.

## Provider mix during this run

| Provider | Completions used |
|---|---|
| ollama (llama3.1:8b, local) | 41 |
| gemini (gemini-3.6-flash, free tier) | 1 |
| groq | 0 (configured model endpoint returned HTTP 404 on every attempt) |

The single Gemini completion was the first trial of the run (none / off_by_one_range) before the
free-tier rate limit was hit; every later call fell through to the local Ollama model. That
single Gemini completion was in the `none` condition and passed, consistent with the rest of that
condition's clean sweep, so it does not change the headline comparison.

## Scope of the claim

One flipped task out of 14 is the entire measured effect at n=1 trial per cell. That sample size
does not support a general claim that instructions reduce pass rate. It does support, as a real
and fully inspectable instance, that an instruction file can shift a model from writing a fresh
answer toward patching the existing buggy code's structure, on a bug the instructions never named.
The concise and long files produced identical pass rates and the identical single failure; added
length bought nothing measurable here.
