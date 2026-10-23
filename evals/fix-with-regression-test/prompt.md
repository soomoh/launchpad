---
description: A bug fix should come with the regression test that would have caught it, and not hide "no value" as zero.
tags: [routing, engineering]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

This should return the average of a list of numbers, but it crashes on an empty list. Fix it — reply with the code.

```python
def average(xs):
    return sum(xs) / len(xs)
```
