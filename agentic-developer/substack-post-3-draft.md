# Post #3 Draft — The Agentic Developer

**Subject line:** Amnesia.
**Subtitle:** Your AI coding agent forgets what it's doing after 20 minutes. Here's why — and what to do about it.

---

You're 45 minutes into a Claude Code session. Everything's going great. You've added three endpoints, fixed a failing test, wired up the AppHost config.

Then you ask Claude to update the integration test for the endpoint it built 15 minutes ago.

And it rewrites the file from scratch. Different naming conventions. Different assertion library. Like the last 40 minutes never happened.

You didn't change anything. You didn't confuse it. **Your session just forgot itself.**

This is the thing nobody warns you about with AI coding agents. The context window — that 200K token buffer that sounds enormous — has a cliff. And once you fall off it, the agent doesn't throw an error. It doesn't warn you. It just starts confidently producing garbage that *looks* like competent code.

I call it **The Amnesia Point.**

## What's actually happening

Every time you interact with Claude Code, the conversation grows. Your prompts, its responses, file reads, build output, test results — all of it stacks into a single context window.

At around 65-70% capacity, Claude Code does something called **auto-compaction**. It summarizes the conversation to free up space. Sounds reasonable. But here's what it actually means:

→ Architectural decisions you discussed at minute 5? Summarized into a sentence. Or gone.

→ That naming convention you established through three rounds of feedback? Compressed into something generic.

→ The specific Shouldly assertion pattern you corrected twice? Lost. Back to `Assert.IsType` from the training data.

Stanford researchers found that language model performance degrades **15-47%** as context fills up — even before compaction happens. The model literally pays less attention to information in the middle of a long conversation. They called it "Lost in the Middle." I call it the reason your 90-minute sessions produce worse code than your 20-minute ones.

And here's the part that should scare you: **you can't tell when it happens.** The agent doesn't stutter. It doesn't say "I'm not sure anymore." It writes code with the same confidence at minute 60 as it did at minute 5. The confidence is identical. The quality isn't.

## The three symptoms

Before I give you the fix, let me describe what Amnesia Point looks like in practice. If any of these sound familiar, you've already hit it:

**1. The Convention Reset.** Your project uses Shouldly, `MethodName_Scenario_ExpectedResult`, and FluentAssertions for HTTP tests. At minute 40, the agent starts writing plain xUnit assertions and `ReturnsX_WhenY` test names. It didn't forget your project — it forgot what you *told it* about your project.

**2. The Ghost Refactor.** You asked Claude to add a DELETE endpoint. Instead, it also restructured three files you didn't mention, added a package you don't want, and moved a helper method to a new class. The guardrails you set 30 minutes ago got compacted away.

**3. The Confident Loop.** Claude fixes a test. You run it. It fails. Claude "fixes" it again — with the exact same code. This loop can go 4-5 rounds before you realize the agent lost the context of *why* the test was failing in the first place.

If you've ever thought "Claude got dumber during the session" — no. It got *amnesia*.

## How to beat it

You don't need a new tool. You need three habits.

### Habit 1: Check your context before it checks out

Run `/context` in your Claude Code session right now. Seriously — stop reading and do it.

Since v2.1.74, this command doesn't just show a progress bar. It tells you **what's eating your context** and gives specific suggestions. If your CLAUDE.md is 15K tokens, it'll tell you. If your bash history is bloated, it'll flag it.

Here's the rule: **if you're above 50%, start a new session.** Not 80%. Not 70%. Fifty.

"But I'll lose all the context from this session."

You will. That's the point. A fresh session with a good CLAUDE.md will produce better code than a long session where the agent is quietly forgetting your standards.

### Habit 2: Write a session handoff note

Before you `/clear` or start a new session, ask Claude to write its own handoff:

```
Write a handoff note for the next session. Include:
- What we built and where
- What decisions we made and why
- What's left to do
- Any patterns or conventions established

Save it to HANDOFF.md
```

Then in your next session, start with: "Read HANDOFF.md before doing anything."

This is the human equivalent of writing a note to yourself before going to sleep. Your future session doesn't have your current session's memory — but it can read a file.

### Habit 3: Keep your CLAUDE.md ruthlessly specific

Your CLAUDE.md is your insurance against amnesia. It loads automatically every session. It's the one thing that survives compaction.

But most developers write CLAUDE.md files that are either too vague or too long. Both are problems.

**Too vague:**
```markdown
# CLAUDE.md
Use the project's conventions. Run tests before committing.
```

Useless. Which conventions? What test command?

**Too long:**
```markdown
# CLAUDE.md
[2,000 words describing every architectural decision since 2019]
```

This eats 8K+ tokens on load. You just gave yourself a smaller context window before you even started working.

**What works — the 200-word CLAUDE.md:**

```markdown
# CLAUDE.md

## Stack
- .NET 10, Aspire 9.2, Minimal APIs
- xUnit + Shouldly for testing
- EF Core with PostgreSQL

## Conventions
- Test names: MethodName_Scenario_ExpectedResult
- One endpoint per static method in *Endpoints.cs files
- No AutoMapper. Manual mapping only.
- Integration tests use WebApplicationFactory

## Guardrails
- Never modify files I didn't mention
- Never add NuGet packages without asking
- Never restructure existing code as part of a feature task

## Verification
- After any code change: run `dotnet build`
- After any test change: run `dotnet test`
- If either fails, fix it before reporting done
```

This is ~150 tokens. It loads instantly. And it contains every decision the agent needs to respect your codebase — even in a fresh session, even after compaction.

## The 30-minute challenge

Here's what I want you to do today:

**Minutes 1-5:** Open your current Claude Code project. Run `/context`. Screenshot what you see. If you're above 50% and still working — that's your Amnesia Point in action.

**Minutes 5-15:** Write a CLAUDE.md under 200 words. Use the template above. Focus on conventions, guardrails, and verification. Nothing else.

**Minutes 15-25:** Start a fresh session. Give it a single task you'd normally do at the end of a long session. Compare the output quality to what you were getting before.

**Minutes 25-30:** Write your first HANDOFF.md. Even if it's rough. The habit matters more than the format.

One session rotation. One CLAUDE.md. One handoff note. That's it.

The developers shipping clean code with AI agents aren't smarter. They're not using a secret model. They just learned to work *with* the context window instead of pretending it's infinite.

---

I put together a free visual guide with 32 illustrated concepts on agentic development — including context management, session architecture, and the CLAUDE.md patterns that actually work. Get it here 👇

[link to visual guide]

---

*What's the worst "amnesia moment" you've had in a coding session? Hit reply — I read every one.*
