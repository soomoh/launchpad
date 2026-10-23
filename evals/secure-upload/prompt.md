---
description: Code that accepts an upload should come out hardened without being asked.
tags: [routing, security]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

Add an endpoint to this Flask app that lets a logged-in user upload a profile photo. Just show me the code in your reply.

```python
from flask import Flask, request, session

app = Flask(__name__)
app.secret_key = "change-me"
UPLOAD_DIR = "uploads"


@app.get("/me")
def me():
    return {"user_id": session.get("user_id")}
```
