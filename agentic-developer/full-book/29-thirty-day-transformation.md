# Chapter 29: The 30-Day Agentic Transformation

*Part VII: The Discipline*

You've read the theory. You've seen the workflows. Now it's time to actually do this.

This chapter is a 30-day plan to transform how you build software. Not a gradual maybe-someday shift. A structured, day-by-day plan with specific tasks, checkpoints, and measurements. By day 30, you'll either be working in a fundamentally different way, or you'll have concrete data on why the agentic approach doesn't work for your context. Either outcome is valuable.

One rule: follow the plan in order. Each day builds on the previous one. Skipping ahead is how people end up with powerful tools they use poorly.

## Before You Start

Measure your baseline. Pick a representative task you'll do in the next few days (a feature, a bug fix, a refactoring) and track:


- **Time to complete** (wall clock, not just coding time)
- **Lines of code written/changed**
- **Number of bugs found during testing**
- **How many files you touched**

Write these numbers down. You'll compare against them in Week 4.

## Week 1: Foundation (Days 1-7)

This week is about setup and first contact. You're building the infrastructure that makes everything else work.


### Day 1: Install and Configure Your Agent Tools

Pick your primary agent. I recommend starting with one, not three:

- **Claude Code** (CLI agent, terminal-native, strong for .NET)
- **GitHub Copilot Agent Mode** (IDE-integrated, familiar for VS Code users)
- **Cursor** (IDE with deep agent integration)

Install it. Configure it. Run your first "hello world" prompt on your actual project:

```
Explain the high-level architecture of this codebase.
What are the main projects and how do they relate to each other?
```

Don't ask it to write code yet. Just verify it can read your codebase and produce coherent output.

**Day 1 checkpoint:** Agent installed, configured, and can read your codebase. You've had one conversation with it about your project.

### Day 2: Create AGENTS.md for Your Main Project

This is the most important file you'll create during the 30 days. Open your project root and create `AGENTS.md` (or `CLAUDE.md`, `.cursorrules`, or `copilot-instructions.md`, depending on your tool).

Start minimal. Include only what the agent needs to know right now:

```markdown
# Project: MyApp

## Build & Run
- `dotnet build` to build
- `dotnet test` to run all tests
- `dotnet run --project src/Api` to start the API

## Architecture
- src/Api: ASP.NET Core Web API
- src/Domain: Business logic, no framework dependencies
- src/Infrastructure: EF Core, external service clients
- tests/: xUnit + FluentAssertions

## Conventions
- Use records for DTOs
- Use MediatR for CQRS
- Async all the way (suffix with Async)
- Nullable reference types enabled

## Do NOT
- Add packages without asking
- Change the database schema directly (use migrations)
- Modify Program.cs without explaining why
```

This takes 15-20 minutes and saves hours over the next month.

**Day 2 checkpoint:** AGENTS.md committed to your repository. You've listed build commands, architecture, core conventions, and anti-patterns.

### Day 3: First Agent Task with Context File

Pick a small, low-risk task. A bug fix. A new DTO. Adding validation to an existing endpoint. Something that takes you 20-30 minutes by hand.

Do it with the agent instead. Use this prompt structure:

```
[Task description in 2-3 sentences]

Relevant files:
- src/Api/Controllers/OrdersController.cs
- src/Domain/Orders/Order.cs
- tests/Api.Tests/OrdersControllerTests.cs

[Specific instructions or constraints]
```

Time yourself. Note what went well and what went poorly. Was the agent faster? Did it follow your conventions from AGENTS.md?

**Day 3 checkpoint:** One real task completed with agent assistance. You have a gut feel for whether the context file helped.

### Days 4-5: Add Path-Scoped Rules

Based on your Day 3 experience, the agent probably did some things wrong. Wrong naming conventions in tests. Wrong patterns in the API layer. Wrong import style.

Create path-scoped rules for your most common file types:

For Claude Code, create files like `.claude/rules/tests.md`:
```markdown
# Test Conventions

- Use xUnit with FluentAssertions
- Test class name: {ClassName}Tests
- Method name: {Method}_{Scenario}_{ExpectedResult}
- Use Arrange/Act/Assert comments
- Use NSubstitute for mocking, not Moq
- Always test edge cases and error conditions
```

For Copilot, add sections to `copilot-instructions.md`. For Cursor, use `.cursorrules`.

Create at least 3 path-scoped rules:
1. Test file conventions
2. API/Controller conventions
3. Domain/business logic conventions

**Days 4-5 checkpoint:** Path-scoped rules created. Run another small task and verify the agent follows them.

### Days 6-7: Your First TDD Agent Loop

This is the workflow from Chapter 5. Time to try it for real.

Pick a task with clear business logic. Write the tests first. All of them. Then hand it to the agent:

```
Make all tests in [TestFile] pass.
Create the necessary types and implementation in [TargetDirectory].
Run the tests after implementation to verify they pass.
```

Don't help the agent. Let it iterate. Watch how it handles test failures and self-corrects.

**Days 6-7 checkpoint:** One complete TDD Agent Loop task done. Tests pass. Code reviewed and committed. You've experienced the full cycle.

### Week 1 Retrospective

At the end of Week 1, update your AGENTS.md with anything you learned. Add conventions the agent missed. Remove instructions that were unnecessary. This file is a living document.

Ask yourself:
- Is the agent saving me time? On what types of tasks?
- What's my biggest friction point?
- What do I keep correcting?

Write your answers down. They shape Week 2.

## Week 2: Core Workflows (Days 8-14)

This week is about repetition and range. You're building muscle memory for the three core agentic workflows.

### Days 8-10: TDD Agent Loop Variations

Run the TDD Agent Loop on three different task types:

**Day 8: Business logic.** Pure domain code. A service, calculator, or validator. No database, no HTTP. This is the easiest type.

**Day 9: API endpoint.** Integration test with `WebApplicationFactory`. The agent builds the full vertical slice: controller, handler, service, and DI registration. This is moderately complex.

**Day 10: Refactoring.** Write tests that capture existing behavior. Ask the agent to refactor the implementation while keeping tests green. This is the trust exercise.

By Day 10, the TDD loop should feel natural. If it doesn't, repeat Days 8-10 with different tasks before moving on.

**Days 8-10 checkpoint:** Three different TDD loop tasks completed. You can do the workflow without referencing the book.

### Days 11-12: Error-Driven Debugging

The debugging workflow: paste an error message, let the agent diagnose and fix.

Pick a real bug (or introduce one deliberately). Give the agent the error message and relevant context:

```
This test is failing with the following error:

[paste full error output]

The test is in [file]. The code under test is in [file].
Diagnose the root cause and fix it. Run the tests to confirm.
```

Practice this workflow on:
- A failing unit test (Day 11)
- A runtime exception from a log (Day 12)

**Days 11-12 checkpoint:** Two bugs fixed using error-driven agent debugging.

### Days 13-14: Codebase Understanding

Use agents to explore unfamiliar code. If your project doesn't have unfamiliar parts, use an open-source project you've never seen before.

```
I need to understand how [feature] works in this codebase.

Trace the flow from the API endpoint to the database for [operation].
Include: which files are involved, what patterns are used,
and where the business logic lives.
```

Then go deeper:

```
Based on the [feature] flow you traced:
1. What are the key design decisions?
2. Are there any code smells or potential issues?
3. How would you add [new capability] to this flow?
```

Use agents for codebase archaeology at least twice this week. It's one of the highest-value use cases and one that most developers underuse.

**Days 13-14 checkpoint:** You've used agents to understand two unfamiliar code areas and can explain them to a colleague.

## Week 3: Scale Up (Days 15-21)

This week you push beyond single-agent, single-task workflows.

### Days 15-16: Parallel Agent Sessions

Run two agents simultaneously on different tasks. This requires git worktrees or separate branches:

```bash
# Create a worktree for the second agent
git worktree add ../myapp-agent2 -b feature/agent2-task
```

Assign each agent a different, non-overlapping task. While Agent 1 works on a new endpoint, Agent 2 writes tests for an existing module. Practice context-switching between the two: check on Agent 1, prompt Agent 2, review Agent 1's output, correct Agent 2.

The key insight from parallel work: your bottleneck shifts from coding speed to review speed. The agents produce faster than you can verify. Get comfortable with that tension.

**Days 15-16 checkpoint:** Two parallel tasks completed. You've experienced the review bottleneck.

### Days 17-18: CI/CD Agent Integration

Set up an agent that reacts to CI failures. The specifics depend on your CI platform, but the pattern is universal:

1. CI run fails
2. Agent receives the failure log
3. Agent diagnoses the issue
4. Agent creates a fix
5. Agent pushes the fix (or creates a PR for your review)

For GitHub, Copilot Coding Agent and Codex can be assigned issues directly. For other platforms, use a CLI agent triggered by a webhook or manual step.

Start simple: when a test fails in CI, paste the failure log to your agent and ask it to fix it. You'll automate the trigger later.

**Days 17-18 checkpoint:** At least one CI failure diagnosed and fixed with agent assistance.

### Days 19-21: Background Agent for an Overnight Task

Assign an agent a larger task (2-4 hours of work) and let it run while you do something else. Good candidates:

- Generate comprehensive tests for an untested module
- Migrate a set of endpoints from one pattern to another
- Add structured logging throughout a service
- Create API documentation from code

Use a background agent tool (Codex Cloud, GitHub Copilot Coding Agent, or a long-running Claude Code session). Write a detailed spec as a markdown file and reference it in your prompt:

```
Implement the spec in docs/logging-migration-spec.md.
Work through each file listed in the spec.
Run tests after each file to ensure nothing breaks.
Create a PR when complete.
```

Review the result the next morning. Note what was done well and what needs correction.

**Days 19-21 checkpoint:** One background agent task completed. You've experienced the async workflow.

## Week 4: Full Agentic Workflow (Days 22-30)

This is the capstone. You're building a complete feature using everything you've learned.

### Days 22-24: Plan the Feature

Pick a real feature from your backlog. Something meaningful: a new module, a significant enhancement, or a complex bug fix. Not a toy example.

Write the spec as a markdown document:
- What the feature does (user stories or requirements)
- Acceptance criteria
- Affected files and modules
- Test strategy
- Any constraints or considerations

Break it into tasks. Each task should be one agent session (30-60 minutes of agent work). A typical feature breaks into 4-8 tasks.

**Days 22-24 checkpoint:** Feature spec written. Tasks broken down. Ready for implementation.

### Days 25-28: Build It

Implement the feature using only agentic methods:

- TDD Agent Loop for each task
- Parallel agents when tasks don't overlap
- Error-driven debugging when things break
- Background agents for boilerplate and tests
- Security review agent on the completed code (Chapter 27)

Track everything:
- Time per task
- Number of agent iterations
- Manual corrections required
- Bugs found in review

Be disciplined about Chapter 28 too. If you hit a task where the agent is clearly the wrong tool, do it by hand. Note the decision and why.

**Days 25-28 checkpoint:** Feature complete. All tests passing. Code reviewed and ready for PR.

### Days 29-30: Measure and Refine

Compare your Week 4 feature build against your baseline measurement from before Day 1:

- **Time:** Faster or slower? By how much?
- **Quality:** More or fewer bugs? Better or worse code structure?
- **Coverage:** More or fewer tests? Better edge case handling?
- **Confidence:** Do you trust the code more or less?

Update your AGENTS.md one final time. After a month of use, you know exactly what the agent needs to know. Your context file should be tight, specific, and battle-tested.

Set up your ongoing rhythm:
- **Daily:** Use the TDD Agent Loop for feature work. Review and update path-scoped rules when the agent drifts.
- **Weekly:** Run a dependency audit and security scan.
- **Monthly:** Review your AGENTS.md. Remove stale instructions. Add new patterns you've adopted.
- **Quarterly:** Measure your productivity again. Are you still improving?

## How to Measure Your Progress

Subjective feeling is unreliable (remember METR: developers felt 20% faster while being 19% slower). Use objective measurements:


**Task completion time.** Pick 3-5 representative task types and track time consistently. Compare month-over-month.

**PR turnaround.** From task start to merged PR. This captures the full cycle including review and correction.

**Test coverage delta.** Are you writing more tests with agents? (You should be. Tests are cheap when agents help implement against them.)

**Bug escape rate.** Bugs found after merge. This should decrease as your TDD and security review workflows mature.

**Context file quality.** Subjective, but track it: how often does the agent need correction? Fewer corrections means better context.

Don't measure lines of code. More lines isn't better. Don't measure prompts per day. More prompts isn't better. Measure outcomes: features shipped, bugs prevented, time saved.

## Common Pitfalls and How to Avoid Them

### Week 1 Pitfalls

**Pitfall: Writing a massive AGENTS.md on Day 2.** You don't know what the agent needs yet. Start small. Add instructions when the agent does something wrong, not preemptively. A 20-line AGENTS.md beats a 200-line one that's full of irrelevant instructions.

**Pitfall: Picking a complex first task on Day 3.** Your first agent task should be embarrassingly simple. A DTO addition. A validation rule. You're learning the tool, not testing its limits. Save the complex tasks for Week 2.

**Pitfall: Abandoning the plan after a bad Day 3.** Your first agent task will be slower than doing it by hand. That's expected. The investment pays off in Week 2 when the context file starts working for you.

### Week 2 Pitfalls

**Pitfall: Skipping the TDD loop because "it works without tests."** It does work without tests. It works worse. The TDD loop isn't about making agents functional. It's about making agents reliable. Without tests, you're reviewing code hoping it works. With tests, you know it works and you're reviewing for quality.

**Pitfall: Not updating context files after corrections.** Every time you correct the agent, ask: "Should this correction be in AGENTS.md so I never make it again?" If yes, add it immediately. Context files grow from corrections, not from imagination.

### Week 3 Pitfalls

**Pitfall: Running too many parallel agents.** Start with two. Seriously. Two parallel agents already strain your review capacity. Three is manageable for experienced users. Five is for when you have months of practice and well-tested context files. The bottleneck is always your review speed, not the agent count.

**Pitfall: Expecting the background agent to produce perfect output.** Background agents produce first-draft output. Plan 30-60 minutes of review and correction for every 2-4 hours of background agent work. If you're not budgeting review time, you'll be disappointed.

### Week 4 Pitfalls

**Pitfall: Forcing the agent on every task.** Some parts of your feature will be faster by hand. Do them by hand. The goal is building the feature efficiently, not proving that agents can do everything.

**Pitfall: Not measuring.** If you don't compare against your baseline, you have opinions instead of data. Opinions are unreliable (METR proved this). Measure. Compare. Adjust.

**Pitfall: Declaring victory (or defeat) too early.** Day 30 isn't the end. It's the beginning of a practice that improves over months. Your context files get better. Your prompts get sharper. Your judgment about when to use agents gets more accurate. Measure again at Day 60 and Day 90.


## The Day 31 Question

On Day 31, ask yourself: "Would I go back to working without agents?"

If the answer is "no," you've transformed. Not because agents are magic, but because you've built the discipline, the context, and the judgment to use them well. You've internalized when they help and when they don't. You've built the infrastructure (context files, test habits, review workflows) that makes agent-assisted development genuinely productive instead of performatively productive.

If the answer is "yes" or "maybe," that's valid too. Review your measurements. Where did agents help? Where did they hurt? Maybe the transformation is narrower than a full workflow shift. Maybe agents work for your test writing but not your feature building. Maybe they work for new code but not maintenance. Partial adoption based on evidence is better than full adoption based on hype.

Either way, you have 30 days of data, a refined context file, and a clear understanding of what agentic development means for your specific work. That's worth more than any amount of theory.

Now go build something.
