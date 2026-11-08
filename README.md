# Medium Articles — Reproducibility Packages

One repository for every reproducibility package behind a Medium article by
[Priyansh Singhal](https://medium.com/@singhalpriyansh58) — one subfolder per article,
instead of a new standalone repo each time.

## Articles

| Article | Published | Repo folder |
|---|---|---|
| [I Reproduced OpenAI's Agent Safety-Alert Evasion on a Free Model](https://medium.com/@singhalpriyansh58/i-reproduced-openais-agent-safety-alert-evasion-on-a-free-model-5979288406b1) | 2026-10-28 | [`agent-safety-alert-suppression-toy/`](./agent-safety-alert-suppression-toy) |
| [My LLM Router Spent 8x More and Matched the Cheap Model Exactly](https://medium.com/@singhalpriyansh58/my-llm-router-spent-8x-more-and-matched-the-cheap-model-exactly-0153690cfbd1) | 2026-10-21 | [`confidence-router-benchmark/`](./confidence-router-benchmark) |
| [I Split One Agent Into Three. The Plan Never Reached the Executor.](https://medium.com/@singhalpriyansh58/i-split-one-agent-into-three-the-plan-never-reached-the-executor-00a7d17b70ca) | 2026-10-14 | [`agent-handoff-loss-benchmark/`](./agent-handoff-loss-benchmark) |
| My Agent Had the Right Tool in a 50-Tool Menu. It Used the Wrong One. | *draft, not yet published* | [`tool-count-confusion/`](./tool-count-confusion) |
| My LLM Judge Caught 1 of 41 Wrong Answers. One Line Fixed the Rest. | *draft, not yet published* | [`llm-judge-rubber-stamp/`](./llm-judge-rubber-stamp) |

Each folder is self-contained: its own `README.md`, `methodology.md`, raw results, analysis,
and license, exactly as it would be as a standalone repo — nothing shared or cross-referenced
between folders.

## Why one repo

Before 2026-11-02, every article with a reproducible experiment got its own standalone GitHub
repo (`agent-safety-alert-suppression-toy`, `confidence-router-benchmark`,
`agent-handoff-loss-benchmark`, `tool-count-confusion` above). That stops here — new articles'
packages land as new subfolders in this one repo, and this README's table gets a new row each
time. The four original repos above are kept online, untouched (their already-published
articles link directly to them), but nothing new will be created there.
