# Repo conventions

- Return exactly the fixed function body. No explanations, no markdown fences, no extra functions.
- Match the existing function signature exactly; do not rename it.
- Common pitfalls in this repo: off-by-one in range()/slices, mutable default arguments
  (`def f(x=[])`), and raising the wrong exception type when the spec names one explicitly.
- Re-read the description's exact wording (inclusive bounds, exact return type, exact exception
  type/message) before writing the fix.
- Prefer the simplest correct fix over a rewrite.
