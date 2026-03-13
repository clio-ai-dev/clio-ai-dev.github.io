# Chapter 22: Cost Management and Token Economics

Nobody talks about this.

Every blog post about AI-powered development mentions the productivity gains. Almost none of them mention the bill. And the bill is real. If you're running multiple agents, using background agents for async work, and integrating agents into your CI/CD pipeline, you're spending money. Potentially a lot of money.

This chapter is about understanding, managing, and justifying that spend.

## The Real Cost of Running Multiple Agents

Let's start with honesty. Here's what a serious agentic development setup costs in early 2026:

### Subscription Stacking

Most developers using agents seriously have multiple subscriptions:


| Service | Monthly Cost | What You Get |
|---------|-------------|-------------|
| GitHub Copilot Business | $19/user | Copilot Chat, Copilot Coding Agent, PR summaries |
| Claude Pro | $20/user | Claude Code with extended thinking, higher rate limits |
| Cursor Pro | $20/user | Cursor's agent mode, multi-file editing |
| ChatGPT Pro | $200/user | Codex Cloud, background agents, higher limits |

That's potentially $259/month per developer, before you write a single line of agent-integrated CI/CD (which uses API tokens, not subscriptions).

Most developers don't need all four. But many have two or three, because different tools excel at different tasks. Claude Code for complex reasoning and large refactors. Copilot for inline completions and GitHub integration. Cursor for its multi-file editing UI. The tools aren't interchangeable, so the subscriptions stack.

### API Token Costs

Subscription plans have rate limits. When you hit those limits, or when you need agents in CI/CD pipelines, you pay per token.

As of early 2026, representative API pricing:

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|----------------------|
| Claude Sonnet 4.5 | $3 | $15 |
| Claude Opus 4 | $15 | $75 |
| GPT-4o | $2.50 | $10 |
| GPT-5 | $10 | $40 |
| Claude Haiku 4.5 | $0.80 | $4 |

A single complex coding session with Claude Code can consume 100K-500K tokens. At Sonnet 4.5 rates, that's $0.30-$1.50 per session for input, plus $1.50-$7.50 for output. Run 10 sessions a day and you're looking at $20-$90/day in API costs alone.

For CI/CD agents that trigger on every failed build, the costs scale with your commit frequency. A team of 10 developers pushing 50 commits/day with a 5% failure rate means 2-3 agent invocations per day. Manageable. But a team going through a major refactor with 30% CI failure rates? That's 15 agent invocations per day, each consuming 50K-200K tokens for analysis and remediation.

### The Hidden Cost: Context Window Bloat

Here's something most developers don't realize: your context files cost money every time an agent loads them.

If your `AGENTS.md` is 5,000 tokens, and your agent loads it at the start of every session, and you run 20 sessions a day, that's 100,000 tokens per day just for context loading. At $3/million tokens, that's $0.30/day, or about $9/month. Not a lot on its own.

But add a bloated context file (20,000 tokens), three rule files (5,000 tokens each), and an overly detailed project README (10,000 tokens), and you're loading 45,000 tokens of context per session. Twenty sessions a day, that's 900,000 tokens/day, or $2.70/day, $81/month. Just for context. Before the agent does any actual work.

This is why context engineering isn't just about quality. It's about economy. Every token in your context files is a recurring cost, multiplied by every session, every developer, every day.

## Context Window Efficiency

The most impactful cost reduction isn't switching to a cheaper model. It's making your context files smaller.


### Audit Your Context Files

Pull up your `AGENTS.md` (or `.cursorrules`, or `copilot-instructions.md`). How long is it? If it's over 2,000 tokens (roughly 1,500 words), it's probably too long. Agents don't need your project's entire history. They need:

- Build commands (2-3 lines)
- Architecture overview (10-15 lines)
- Key conventions (10-15 lines)
- What not to do (5-10 lines)

That's about 500-800 tokens. Everything else should be in scoped rules that only load when relevant (e.g., C# rules only load when editing `.cs` files).

### Use Scoped Rules

Instead of one massive context file, break it into scoped rules:

```
.claude/rules/
  csharp.md        # Only loads for .cs files
  testing.md       # Only loads for test files
  api.md           # Only loads for controller files
  infrastructure.md # Only loads for IaC files
```

Each rule file is small (200-500 tokens). Only the relevant rules load per session. A test-writing session loads `testing.md` but not `infrastructure.md`. An API implementation session loads `api.md` and `csharp.md` but not `testing.md`.

The savings compound. Instead of loading 2,000 tokens of context every session, you load 400-800 tokens of relevant context. Over hundreds of sessions per month, this adds up.

### Trim Your Prompt Engineering

Verbose prompts cost money. "I would like you to please create a comprehensive service class that handles all aspects of..." is burning tokens on filler. "Create `OrderService` with these methods: ..." is cheaper and more effective.

This isn't about being terse. It's about being precise. Every word in a prompt should carry information. If removing a word doesn't change the output, remove it.

## Model Selection Strategy

Not every task needs the most expensive model. This is the single biggest lever most developers ignore.

### The Three-Tier Approach


**Tier 1: Cheap and fast (Haiku, GPT-4o-mini)**
- Code formatting and linting fixes
- Simple boilerplate generation
- Documentation generation
- Test scaffolding
- Commit message generation
- Context file maintenance

Cost: $0.80-$1.50 per million input tokens. Use this for 60-70% of your agent interactions.

**Tier 2: Capable and balanced (Sonnet, GPT-4o)**
- Feature implementation from specs
- Bug diagnosis and fixing
- Code review assistance
- Refactoring
- CI failure analysis

Cost: $2.50-$3 per million input tokens. Use this for 25-35% of your interactions.

**Tier 3: Maximum capability (Opus, GPT-5, o3)**
- Complex architectural decisions
- Large-scale refactoring across many files
- Debugging subtle, multi-component issues
- Performance optimization
- Security review

Cost: $10-$15 per million input tokens. Use this for 5-10% of your interactions, the problems that actually need it.

### Automatic Model Routing

Some tools support automatic model selection based on task complexity. If yours doesn't, build the habit manually. Before launching an agent, ask: "Does this task need the expensive model?" If the answer is "probably not," use Tier 1 or Tier 2.

The difference in monthly cost between "always use Opus" and "use Opus only when needed" can be 5-10x. For a team of 10, that's the difference between a $500/month AI budget and a $5,000/month AI budget.

## Cost Tracking and Budgeting for Teams

If you're a team lead or engineering manager, you need visibility into AI spending. Without tracking, costs creep up invisibly until someone notices the credit card bill.

### What to Track

- **Per-developer spending:** Who's using the most tokens? Are they getting proportional value?
- **Per-task-type spending:** How much does CI/CD automation cost vs. feature development vs. code review?
- **Model usage distribution:** Are developers defaulting to expensive models for simple tasks?
- **Context file sizes:** Are they growing over time? (They usually are.)
- **Cost per PR:** Divide total AI spend by PRs merged. This gives you a rough cost-per-unit-of-output.

### Setting Budgets

A reasonable starting budget for a team adopting agentic development:

- **Subscriptions:** $40-$60/developer/month (two tool subscriptions)
- **API tokens:** $20-$50/developer/month (for CLI agents and CI/CD)
- **Total:** $60-$110/developer/month

That's $720-$1,320/developer/year. For context, a developer's fully loaded cost is typically $150,000-$250,000/year. If AI tools provide even a 10% productivity improvement, the ROI is clear: $15,000-$25,000 of additional output for $720-$1,320 of tooling cost.

The math is overwhelmingly in favor of the tools. The question isn't whether to spend, it's whether you're spending efficiently.

## ROI Calculation: Justifying the Spend

If you need to justify AI tooling spend to management (or to yourself), here's a framework.


### The Conservative Calculation

Assume a modest 15% productivity improvement (well below the 26% GitHub measured, but accounting for the METR study's finding that naive usage can slow you down).

```
Developer cost:           $200,000/year (fully loaded)
15% productivity gain:    $30,000/year equivalent output
AI tooling cost:          $1,200/year ($100/month)
Net ROI:                  $28,800/year per developer
ROI percentage:           2,400%
```

Even if you cut the productivity gain to 5% (extremely conservative), the ROI is still 733%. The tooling cost is simply too small relative to developer compensation for the math to not work out.

### The Honest Calculation

The conservative calculation assumes productivity gains are uniform. They're not. Some tasks see 50%+ improvement (boilerplate, testing, documentation). Others see 0% or negative improvement (novel architecture, deep debugging, creative design).

A more honest calculation:

```
Tasks that benefit from agents:        60% of developer time
Average improvement on those tasks:    25%
Effective overall improvement:         15%
Tasks that don't benefit:              30% of developer time
Tasks where agents slow you down:      10% of developer time
Average slowdown:                      -10%
Net effective improvement:             14%
```

Even this more nuanced calculation produces massive ROI. The tools pay for themselves many times over, as long as you're using them on the right tasks and not forcing them where they don't help.

## Tips for Reducing Costs Without Reducing Quality

### 1. Cache Your Context

If your agent tool supports it, cache compiled context between sessions. Some tools (Claude Code with its session memory, Cursor with its indexed codebase) do this automatically. The first session loads everything; subsequent sessions reuse the cache.

### 2. Batch Small Tasks

Instead of 10 separate agent sessions for 10 small fixes, batch them: "Fix all 10 items in this list: [list]." One session with one context load instead of ten sessions with ten context loads.

### 3. Write Better Specs

The tightest spec produces the fewest iterations. Every round of "that's not what I meant, try again" costs tokens. Invest 5 minutes in a clear spec and save $5 in wasted iterations.

### 4. Use Checkpoints

For long-running tasks, use agents that support checkpointing. If the agent goes off-track at step 7 of 10, you can roll back to step 6 instead of starting over. Some tools support this natively; others require you to commit intermediate results to Git.

### 5. Kill Bad Sessions Early

If an agent is clearly going in the wrong direction, stop it. Don't let it burn tokens trying to fix a fundamentally wrong approach. Reset, refine the spec, restart. The sunk cost fallacy applies to token spend too.

### 6. Monitor and Alert

Set up spending alerts with your API provider. Anthropic, OpenAI, and others support budget limits and email notifications. A runaway agent (stuck in a retry loop, for example) can burn through a month's budget in hours.

### 7. Compress Context Aggressively

Review your context files monthly. Remove outdated conventions. Consolidate redundant rules. Shorten verbose explanations. Every token you trim saves money on every future session.

### 8. Use the Right Tool for the Job

Don't use Claude Opus to generate a `.gitignore` file. Don't use a CI/CD agent for a one-time script. Match the tool to the task. This sounds obvious, but developers consistently default to their most powerful (and expensive) tool for everything.

## The Team Economics

For engineering teams, the economics of agentic development extend beyond tool costs. Consider the second-order effects:

**Reduced context-switching cost:** When an agent handles CI failures, developers stay focused on their primary tasks. Context-switching costs are estimated at 15-20 minutes per interruption. Eliminating 2-3 CI-related interruptions per day saves 30-60 minutes per developer.

**Reduced onboarding time:** New developers with agent support can explore and understand codebases faster. The "ask the agent about the codebase" workflow (Chapter 18's codebase questions category) replaces hours of reading code or asking senior developers for explanations.

**Reduced technical debt accumulation:** Background agents can chip away at tech debt overnight (Chapter 19). Tasks that never make it to the top of a human's priority list can be assigned to agents during off-hours.

**Increased deployment frequency:** Agent-integrated CI/CD (Chapter 21) reduces the time from "something broke" to "it's fixed." Faster recovery means more confidence in deploying, which means more frequent deployments, which means faster feedback loops.

These second-order effects are harder to measure but often more valuable than the direct productivity gains. A team that deploys twice as often, onboards developers in half the time, and accumulates less tech debt is a fundamentally more effective team, regardless of what the line-item AI budget looks like.

## The Bottom Line

AI tooling costs money. The costs are real, visible, and growing as you adopt more tools and more sophisticated workflows. Ignoring costs leads to waste. Obsessing over costs leads to under-utilization.

The right approach is informed management: know what you're spending, know what you're getting, and continuously optimize the ratio. Track costs per developer, per task type, and per model. Use cheap models for cheap tasks. Write tight specs and tight context files. Monitor for waste.

And when someone asks "is this worth the money?", the answer is almost certainly yes. A $100/month tool that makes a $200,000/year developer 15% more effective pays for itself in the first two days of every month. The remaining 28 days are pure upside.

The real question isn't whether to spend. It's whether you're spending wisely. This chapter gave you the framework to answer that question. Now go audit your context files. You're probably burning tokens on instructions nobody reads.
