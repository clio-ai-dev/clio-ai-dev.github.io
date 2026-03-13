# Chapter 12: CLI and Cloud Agents: The Power Tools

IDE agents are where most developers start. CLI and cloud agents are where the serious productivity gains live.

The difference is fundamental. An IDE agent operates inside your editor, constrained by the UI, limited to the files you have open, and dependent on your active attention. A CLI agent operates in your terminal with full access to your development environment: your file system, your build tools, your test runner, your git history, everything. A cloud agent doesn't even need your machine running. It works in the background, creates a PR, and pings you when it's done.

If IDE agents are your pair programmer, CLI agents are your senior developer who works independently and comes back with a pull request. Cloud agents are the contractor you hire for well-defined tasks and check in on later.

This chapter covers the major players, when to use each, and how to combine them into a workflow that lets you do the work of a small team.

## Claude Code: The Terminal-Native Agent

Claude Code is, in my opinion, the most capable coding agent available as of early 2026. It runs entirely in your terminal, which sounds like a limitation until you realize it's actually a superpower.


Because Claude Code operates in the terminal, it has access to everything your terminal has access to: your full file system, your shell, your environment variables, your build tools, your test runner, your git configuration. It doesn't need a plugin or extension. It doesn't need a specific editor. It works everywhere.

### What Claude Code Actually Does

When you launch Claude Code in a project directory, it reads your codebase and understands your project structure. Then you give it a task in natural language:

```bash
$ claude
> Add rate limiting to the /api/orders endpoint. Use the built-in 
  ASP.NET Core rate limiter with a fixed window of 100 requests 
  per minute per user. Add integration tests.
```

Claude Code will:

1. Read your existing code to understand the patterns
2. Identify which files need changes
3. Make the edits
4. Run your tests to verify nothing broke
5. If tests fail, read the output and iterate
6. Present you with a summary of changes

The key differentiator: Claude Code *runs your tools*. It doesn't just generate code and hope for the best. It executes `dotnet build`, reads the compiler errors, fixes them, runs `dotnet test`, reads the failures, and fixes those too. This iterative loop is what separates it from chat-based tools.

### Sub-Agents

Claude Code can spawn sub-agents for parallel work. When you give it a complex task, it can break it into pieces and assign each piece to a separate agent. One sub-agent researches the existing codebase structure. Another implements the feature. A third writes the tests. The main agent orchestrates.

This isn't theoretical. On a task like "refactor the notification system from synchronous to event-driven," Claude Code might:

1. Spawn a sub-agent to analyze the current notification call sites
2. Spawn another to design the event schema
3. Implement the changes in the main agent
4. Spawn a sub-agent to update all the tests

The result is faster completion of complex, multi-file tasks.

### Skills

Skills are reusable instruction sets that Claude Code loads on demand. Think of them as specialized playbooks. You might have a skill for "creating a new ASP.NET Core endpoint" that includes your specific patterns: where to put the controller, how to structure the DTO, which validation library to use, which test patterns to follow.

Skills are stored as markdown files and loaded by description matching. When Claude Code encounters a task that matches a skill's description, it reads the skill file and follows the instructions. This is more powerful than context files because skills can include step-by-step procedures, not just conventions.

### Setting Up Claude Code

The most important setup step is creating a `CLAUDE.md` file at the root of your project. This is Claude Code's equivalent of `.cursorrules` or `copilot-instructions.md`, but it tends to be more detailed because Claude Code is more autonomous and needs more guidance.

A solid `CLAUDE.md` for a .NET project:

```markdown
# CLAUDE.md

## Project
ASP.NET Core 10 Web API with Clean Architecture.
Solution file: GameStore.sln

## Build & Test
- Build: `dotnet build`
- Test: `dotnet test --no-build`  
- Single test: `dotnet test --filter "FullyQualifiedName~TestName"`
- Run: `cd src/Api && dotnet run`

## Architecture
- src/Api/ - Controllers, DTOs, middleware
- src/Core/ - Domain entities, interfaces, services
- src/Infrastructure/ - EF Core, external services
- tests/Api.Tests/ - Integration tests (WebApplicationFactory)
- tests/Core.Tests/ - Unit tests

## Conventions
- File-scoped namespaces
- Record types for DTOs
- Primary constructors where appropriate
- IReadOnlyList<T> for collection return types
- Async all the way down, never .Result or .Wait()
- FluentValidation for request validation
- xUnit + NSubstitute for testing

## Patterns
- Repository pattern: interface in Core, implementation in Infrastructure
- CQRS-lite: separate query and command services, no full MediatR
- Result pattern for service returns (not exceptions for business logic)

## Do NOT
- Add packages without asking
- Modify the DbContext directly (use migrations)
- Use Console.WriteLine (use ILogger)
- Skip writing tests
```

### Permissions and Allowed Tools

Claude Code has a permission system that controls what it can do without asking. Configure this based on your comfort level:

```bash
# Allow running build and test commands without prompting
claude config set allowedTools "dotnet build" "dotnet test" "dotnet run" "git status" "git diff"
```

For trusted projects where you have a good test suite, allowing build and test commands to run without approval dramatically speeds up the iterative loop. Claude Code builds, tests, observes failures, and fixes them without interrupting you for permission at each step.

For less trusted contexts (unfamiliar codebases, production-adjacent work), keep the defaults restrictive and approve each command manually.

## Codex CLI: OpenAI's Terminal Agent

Codex CLI is OpenAI's answer to Claude Code. It runs in your terminal, understands your project, and can make multi-file edits. It's powered by GPT-5-Codex (or whatever model OpenAI is shipping when you read this).

### How It Compares to Claude Code

Codex CLI is competent and improving rapidly. Its strengths:

- Tight integration with OpenAI's model ecosystem
- Good at following existing code patterns
- Solid at explaining code and reasoning through problems
- Fast response times

Its weaknesses relative to Claude Code (as of early 2026):

- Less autonomous in iterative workflows (doesn't loop on test failures as aggressively)
- Smaller effective context window for very large codebases
- Fewer extensibility features (no equivalent to Claude Code's skills system)

That said, having both installed gives you optionality. Some tasks respond better to one model's reasoning style than the other. When Claude Code struggles with a particularly gnarly debugging session, switching to Codex CLI sometimes produces a fresh perspective that cracks the problem.

### Basic Usage

```bash
$ codex
> Fix the flaky test in OrderServiceTests.cs. It intermittently 
  fails on the date comparison assertion. Find the root cause 
  and fix it properly, don't just add retry logic.
```

Codex CLI will read the test, trace the code under test, identify the timezone or timing issue, and propose a fix. Like Claude Code, it can run your build and test commands to verify its changes.

## Cloud Agents: Fire and Forget

Cloud agents represent a fundamentally different workflow. You don't sit with them. You don't watch them work. You assign a task, walk away, and come back to a pull request.

### Codex Cloud (GitHub)

Codex Cloud (previously called GitHub Copilot Coding Agent, now accessible through what GitHub calls "Agent HQ") runs in GitHub's cloud infrastructure. You can launch it from:

- The GitHub web interface
- GitHub Mobile (your phone)
- VS Code's agent panel

The workflow:

1. Open a GitHub issue or describe a task
2. Assign it to Codex Cloud
3. The agent spins up an environment, clones your repo, makes changes
4. It runs your CI pipeline (if configured)
5. It opens a pull request with its changes
6. You review the PR like any other

This is the "fire-from-phone" workflow that changes how you think about productivity. Sitting in a waiting room? Open GitHub Mobile, create an issue: "Add pagination to the /api/products endpoint, following the existing pagination pattern in /api/orders." Assign it to Codex. Put your phone away. By the time you're back at your desk, there's a PR waiting.

What works well with Codex Cloud:

- Well-defined, scoped tasks with clear acceptance criteria
- Tasks that follow existing patterns in your codebase
- Bug fixes with clear reproduction steps
- Adding tests for existing untested code
- Documentation updates

What doesn't work well:

- Architectural changes that require deep understanding of system behavior
- Tasks that need access to running services or databases
- Anything requiring interactive debugging
- Tasks where the spec is ambiguous

### Google Jules

Jules is Google's background coding agent, integrated with GitHub repositories. It occupies similar territory to Codex Cloud: you assign a task, it creates a branch, makes changes, and opens a PR.

Jules differentiates itself with its plan-first approach. Before writing any code, Jules generates a detailed plan and asks for your approval. This adds a step but catches misunderstandings early. If the plan looks wrong, you redirect before any code is written, saving time overall.

Jules works well for:

- Dependency updates and migration tasks
- Code cleanup and refactoring
- Implementing features from well-written specs
- Bug fixes with clear context

### Amazon Q Developer

Amazon Q Developer is AWS's entry in the coding agent space. If you're working heavily with AWS services (and many .NET developers are, especially those using Lambda, ECS, or App Runner), Q Developer has the deepest understanding of AWS APIs, IAM policies, CloudFormation templates, and AWS-specific patterns.

For .NET on AWS specifically, Q Developer handles:

- Lambda function scaffolding and deployment configuration
- CDK (Cloud Development Kit) template generation
- IAM policy generation with least-privilege principles
- AWS SDK integration patterns

If your stack is Azure-centric, Q Developer is less compelling. But if you're deploying .NET to AWS, it's worth having in your toolkit alongside your primary agent.

## When CLI Beats IDE (and Vice Versa)

This isn't an either/or choice. CLI and IDE agents excel at different things.


**Reach for CLI agents when:**

- The task involves multiple files across the codebase
- You need the agent to run builds, tests, or other tools
- The task requires reading and understanding a large portion of the codebase
- You want the agent to iterate autonomously until tests pass
- You're working on a task that doesn't require visual context (no UI work)
- You want to work in parallel, running the agent in one terminal while you code in another

**Reach for IDE agents when:**

- You're doing inline edits to a single file or small set of files
- You need visual diff review in the editor
- The task benefits from seeing the code structure in the file tree
- You're doing exploratory work where you want to see completions as you type
- You need tight integration with editor features (debugging, go-to-definition)

**The practical split:** Use your IDE agent for the code you're actively writing and thinking about. Use CLI agents for tasks you want to delegate and review later. Use cloud agents for tasks you want to fire and forget entirely.

## The Parallel Coding Agent Lifestyle


Simon Willison coined this term, and it describes the workflow that delivers the biggest productivity multiplier: running multiple agents simultaneously on different tasks.

The concept: instead of doing one thing at a time, you break your work into independent tasks and assign each to a separate agent. While they work, you either work on something yourself or orchestrate more agents. Your role shifts from implementer to project manager.

### Git Worktrees: The Enabler

The practical foundation for parallel agents is git worktrees. A worktree lets you have multiple working copies of the same repository, each on a different branch, without cloning the repo multiple times.


```bash
# Create worktrees for parallel agent sessions
git worktree add ../myproject-feature-auth feature/auth-refactor
git worktree add ../myproject-feature-export feature/csv-export  
git worktree add ../myproject-fix-flaky fix/flaky-tests
```

Now you have three separate directories, each on its own branch. Launch a Claude Code session in each:

```bash
# Terminal 1
cd ../myproject-feature-auth
claude "Refactor the auth middleware to support both JWT and API key authentication"

# Terminal 2
cd ../myproject-feature-export
claude "Add CSV export to the orders endpoint, following the existing export pattern in reports"

# Terminal 3
cd ../myproject-fix-flaky
claude "Find and fix all flaky tests. Run the test suite 3 times to verify stability"
```

Three agents working simultaneously on three different tasks. You check in periodically, review their progress, provide guidance if they're stuck, and approve or reject their changes.

When they finish, merge the branches:

```bash
git worktree remove ../myproject-feature-auth
git worktree remove ../myproject-feature-export
git worktree remove ../myproject-fix-flaky
```

### What Works for Parallel Agents

Simon Willison identified four categories of tasks that work well in parallel:

1. **Research and proof-of-concept**: "Investigate whether we can replace Newtonsoft.Json with System.Text.Json. Identify all breaking changes."
2. **Codebase questions**: "Document how the payment processing pipeline works. Trace from API endpoint to Stripe webhook handler."
3. **Small maintenance tasks**: "Update all deprecated API calls to their modern equivalents." "Fix all compiler warnings."
4. **Carefully specified implementation**: Tasks where you've written a clear spec. This is the most productive category because the agent has clear success criteria.

### What Doesn't Work

Don't run parallel agents on tasks that touch the same files. Merge conflicts are painful enough between human developers. Between agents that don't know about each other, they're worse.

Don't run parallel agents on architecturally coupled tasks. If task A changes the database schema and task B adds a new query, they need to be sequential, not parallel.

And don't run more agents than you can review. The bottleneck in parallel agent work is always review. Five agents producing code simultaneously sounds productive until you realize you have five PRs to review, each with 200+ lines of changes. Start with two or three parallel agents and scale up as your review speed improves.

## The Fire-From-Phone Workflow

This deserves its own section because it's genuinely transformative. The ability to launch coding tasks from your phone changes the economics of dead time.


The setup:

1. **GitHub Mobile** installed on your phone
2. **Codex Cloud** (or equivalent cloud agent) enabled on your repository
3. **CI/CD pipeline** that runs tests automatically on new PRs
4. **Clear task templates** so you can describe tasks quickly from a small screen

The workflow:

- Commuting, waiting, walking, whatever: you think of something that needs doing
- Open GitHub Mobile, create an issue with a clear description
- Assign it to the cloud agent
- Put your phone away
- Later, at your desk, the PR is waiting with CI status

Tasks that work from phone:

- "Add input validation to the CreateOrder endpoint"
- "Write unit tests for the DiscountCalculator class"
- "Update the README with the new deployment steps"
- "Fix the N+1 query in the GetOrdersWithItems method"

Tasks that don't work from phone (not enough screen real estate to spec properly):

- Complex architectural changes
- Features requiring detailed acceptance criteria
- Anything where the spec needs diagrams or extensive context

## A Day in the Life: Combining Everything

Here's what a real day looks like when you combine IDE, CLI, and cloud agents:

**8:00 AM, coffee in hand.** Open Cursor. Review the two PRs that Codex Cloud created overnight (you launched them from your phone yesterday evening). One looks good, approve and merge. The other needs tweaks, leave comments.


**8:30 AM.** Start your main task for the day: redesigning the notification system. Write a spec document first (30 minutes of focused thinking, no agents). Break it into three subtasks.

**9:00 AM.** Launch Claude Code in a worktree for subtask 1 (new event types and handlers). Open Cursor for subtask 2 (updating the API endpoints), which you'll do yourself with Agent Mode because it requires design decisions. Assign subtask 3 (updating tests) to a Cursor Background Agent.

**9:30 AM.** Claude Code has a draft of the event handlers. Review in terminal, provide feedback ("use the MediatR notification pattern, not raw events"). It iterates. Meanwhile, you're working on the API changes in Cursor.

**10:00 AM.** Your Cursor Background Agent finishes updating the tests. Review the diff. Mostly good, but it missed an edge case. Add a comment and let it iterate.

**10:30 AM.** All three subtasks are done. Merge the branches. Run the full test suite. Two failures from integration issues between the subtasks. Fix them manually (5 minutes, this is where your expertise matters).

**11:00 AM.** During a break, open your phone. Create two GitHub issues for tomorrow's work: a performance optimization and a documentation update. Assign both to Codex Cloud. They'll be PRs by morning.

That's five developer-tasks completed by lunch, with one person. Not by working faster, but by working in parallel and focusing your attention on the parts that require human judgment: specs, architecture, reviews, and integration.

## Setting Up Your Multi-Agent Environment

Here's the practical setup to enable this workflow:

### 1. Install the tools

```bash
# Claude Code
npm install -g @anthropic-ai/claude-code

# Codex CLI  
npm install -g @openai/codex-cli

# Cursor (download from cursor.com)
# Copilot (VS Code extension)
```

### 2. Create project context files

At minimum, create `CLAUDE.md` and `.cursor/rules/general.mdc` for your project. If you want cross-tool compatibility, create an `AGENTS.md` that both tools can reference.

### 3. Set up git worktree aliases

Add to your shell config:

```bash
# Quick worktree creation for agent sessions
agent-worktree() {
  local branch="agent/$1"
  local dir="../$(basename $PWD)-$1"
  git checkout -b "$branch" 2>/dev/null || true
  git worktree add "$dir" "$branch"
  echo "Worktree ready at $dir"
}

# Quick cleanup
agent-cleanup() {
  for dir in ../$(basename $PWD)-*; do
    [ -d "$dir" ] && git worktree remove "$dir" --force
  done
  git branch --list 'agent/*' | xargs -r git branch -D
}
```

### 4. Configure Claude Code permissions

```bash
# For trusted projects with good test coverage
claude config set allowedTools \
  "dotnet build" \
  "dotnet test" \
  "dotnet run" \
  "git status" \
  "git diff" \
  "git add" \
  "git commit"
```

### 5. Set up CI for cloud agents

Ensure your GitHub Actions (or equivalent) run tests on every PR. Cloud agents create PRs, and your CI pipeline is their verification step. Without CI, you're reviewing agent code without any automated safety net.

## The Cost of Multi-Agent Work

Let's be honest about costs. Running multiple agents simultaneously burns tokens fast.

A typical day of heavy agent use:

| Activity | Estimated Cost |
|----------|---------------|
| Claude Code (3-4 sessions) | $5-15 |
| Cursor Pro (subscription) | ~$1/day |
| Copilot (subscription) | ~$0.50/day |
| Codex Cloud (2-3 tasks) | $2-5 |
| **Daily total** | **$8-22** |

That's $200-500/month for heavy users. Sounds steep until you compare it to developer salaries. If these tools save you 2 hours per day at a $75/hour effective rate, that's $3,000/month in recovered time. The ROI is 6-15x.

But monitor your usage. Token costs can spike unexpectedly on complex tasks where agents iterate many times. Set budget alerts on your Claude and OpenAI accounts. Review your usage weekly.

## The Bottom Line

CLI and cloud agents are where the "parallel coding agent lifestyle" becomes real. IDE agents help you code faster. CLI agents let you delegate entire tasks. Cloud agents let you delegate from anywhere, even your phone.

The developers getting the most out of this era aren't the ones using a single tool really well. They're the ones combining multiple tools, each in its sweet spot: IDE agents for active coding, CLI agents for complex delegated tasks, cloud agents for async fire-and-forget work.

The setup takes an afternoon. The payoff lasts your entire career. Or at least until the next paradigm shift, which, at the current pace, might be next Tuesday.
