# Prompt Templates

Quick templates for fast, effective communication with Claw.

---

## 🔧 Quick Commands

| Abbrev | Meaning | Example |
|--------|---------|---------|
| `/w` | Write to memory | `/w Ryan prefers video over text summaries` |
| `/r` | Read memory | `/r what does Ryan like?` |
| `/s` | Search web | `/s best VSCode extensions for AI coding` |
| `/t` | Task (spawn sub-agent) | `/t research量子计算最新进展` |
| `/c` | Code task | `/c write a Python script to parse JSON` |

---

## 📝 Ideal Prompt Structure

**Best format:**
```
[What you want] + [Context] + [Constraints]

Example: "Write a haiku about a lobster" → too simple
Example: "Write a haiku about a lobster feeling existential, keep it under 30 chars" → better
```

**For tasks, use:**
```
DO: [specific action]
CONTEXT: [why, background]
CONSTRAINTS: [limits, style, format]
```

---

## 🎯 Prompt Quality Guide

| Weak Prompt | Strong Prompt |
|-------------|---------------|
| "Help me" | "Write a Python function that reads a CSV and returns rows where column_3 > 100" |
| "Find stuff about X" | "Find the latest (2025) research papers on transformer efficiency, summarize 3 key findings" |
| "Make it better" | "Refactor this function to use list comprehension instead of for-loop, keep it under 5 lines" |

---

## ⚡ Test These

Try sending me:

1. **Code:** `Write a 3-line Python function that checks if a number is prime`
2. **Research:** `What's the best open-source alternative to Notion? Summarize in 2 sentences`
3. **Memory:** `Remember: my favorite color is forest green`
4. **Action:** `Create a cron job that runs every Monday at 9am`
5. **Creative:** `Write a limerick about an AI lobster`

---

## 🚫 Don't

- Ask "can you help me?" → just tell me what to do
- Be vague → "make it faster" → "reduce this function from 20 to 5 lines"
- Stack multiple unrelated requests → break into separate messages

---

**Test my responses and let me know what needs tuning!**
