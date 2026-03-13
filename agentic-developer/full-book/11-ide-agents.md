# Chapter 11: IDE Agents: Copilot, Cursor, and Windsurf

Your IDE is where you spend most of your day. It's where code gets written, reviewed, debugged, and shipped. So it makes sense that the most impactful AI tools are the ones embedded directly in your editor, the ones that understand your project, your open files, and your current intent without you having to explain anything.

But here's the problem: there are now at least four serious IDE-integrated AI tools, each with overlapping features, different strengths, and separate subscription costs. Picking the wrong one (or worse, using the right one badly) costs you time and money every single day.

This chapter breaks down the major players: GitHub Copilot, Cursor, Windsurf, and JetBrains AI Assistant. Not with marketing bullet points, but with real workflows, honest opinions, and a decision framework you can actually use.

## GitHub Copilot: The Default Choice

Copilot is the tool most developers try first, and for good reason. It's built into VS Code (and Visual Studio, and JetBrains, and Neovim), it's backed by GitHub's deep integration with your repositories, and it's the most polished of the bunch.

### Inline Completions

The original feature, and still the most used. You type, Copilot suggests. Accept with Tab. This sounds trivial until you realize how much of coding is boilerplate: property declarations, null checks, LINQ queries, constructor injection patterns. Copilot handles these with near-perfect accuracy in C# because it's seen millions of .NET projects.

The key to getting good completions: write clear, descriptive names. A method called `GetActiveUsersByDepartment` gets better completions than one called `GetData`. Your naming conventions are context. Treat them that way.

### Copilot Chat

The chat panel in VS Code gives you a conversation interface with full awareness of your workspace. You can ask questions about your codebase, request explanations of unfamiliar code, or ask for refactoring suggestions. It's essentially a senior developer sitting next to you who has read every file in your project.

Where Chat shines is codebase archaeology. Joining a new project? Ask Chat: "How does the authentication middleware work in this project?" It will trace through the code and give you a coherent explanation. That alone saves hours of onboarding time.

### Agent Mode

This is where Copilot became a real agent, not just an assistant. Agent Mode (launched in VS Code in early 2025 and refined throughout the year) can:

- Edit multiple files simultaneously
- Run terminal commands
- Execute your tests and iterate on failures
- Create and delete files
- Install packages

The workflow is simple. You describe what you want in the chat panel, select Agent Mode, and Copilot proposes a plan. It shows you the files it will touch, the changes it will make, and the commands it will run. You approve, and it executes. If tests fail, it reads the output and tries again.

Here's a real example. You're adding a new endpoint to an ASP.NET Core API:

```
Add a GET /api/orders/{id}/history endpoint that returns the status 
change history for an order. Use the existing OrderRepository pattern.
Include a DTO, a service method, controller action, and a unit test.
```

Agent Mode will create the DTO class, add the service method, wire up the controller, and write a test. Four files, one prompt. You review the diff, tweak anything you don't like, and move on.

The limitation: Copilot Agent Mode is conservative by default. It asks for approval before running terminal commands, which is the right default but slows down iterative workflows. You can adjust this in settings, but be deliberate about what you auto-approve.

### The Edits Panel

Introduced alongside Agent Mode, the Edits panel gives you a middle ground between Chat and full Agent Mode. You select files, describe a change, and Copilot generates a multi-file diff that you review and apply. No terminal access, no command execution, just code changes across files.

This is perfect for refactoring. "Rename the UserService to AccountService and update all references" is exactly the kind of task the Edits panel handles cleanly. It's less powerful than Agent Mode but faster for targeted changes.

### Configuring Copilot

Copilot reads project-level instructions from `.github/copilot-instructions.md`. This file is your chance to tell Copilot how your project works:

```markdown
# Copilot Instructions

## Architecture
This is an ASP.NET Core 10 Web API using Clean Architecture.
- Controllers in src/Api/Controllers/
- Business logic in src/Core/Services/
- Data access in src/Infrastructure/Repositories/
- DTOs in src/Api/Models/

## Conventions
- Use record types for DTOs
- Repository pattern with interfaces in Core, implementations in Infrastructure
- All endpoints return ActionResult<T>
- Use FluentValidation for input validation
- xUnit + NSubstitute for testing

## Do NOT
- Use static methods for business logic
- Put EF Core DbContext in controllers
- Skip null checks on repository returns
```

This file is loaded automatically when Copilot processes your workspace. Every interaction gets better because Copilot understands your conventions without you repeating them.

You can also add VS Code settings to fine-tune behavior:

```json
{
  "github.copilot.chat.codeGeneration.useReferencedFiles": true,
  "github.copilot.chat.agent.runCommand.enabled": true
}
```

### Model Selection

As of early 2026, Copilot lets you choose between multiple models: GPT-4.1, Claude Sonnet 4.5, and others. For C# work, Claude Sonnet tends to produce more idiomatic code. For quick completions and chat, GPT-4.1 is faster. You can switch models per conversation, so use the right one for the task.


## Cursor: The Power User's Editor

Cursor is a fork of VS Code that went all-in on AI. If Copilot is AI added to an editor, Cursor is an editor built around AI. The difference shows in every interaction.

### Tab Completion

Cursor's Tab completion is similar to Copilot's inline suggestions but more aggressive. It predicts multi-line completions, suggests entire code blocks, and adapts quickly to your patterns. The "Tab" model is specifically trained for code completion and feels noticeably faster than Copilot's inline suggestions for complex completions.

Where Cursor Tab really differentiates is in its ability to predict your *next edit*. After you change a method signature, Tab will suggest the corresponding changes in calling code. After you rename a variable, it suggests updates in related files. It's not just completing the current line; it's completing the current *thought*.

### Chat and Inline Editing

Cursor's chat works similarly to Copilot's, but with one critical addition: you can `@mention` files, folders, documentation, and even web URLs directly in your prompts. `@src/Core/Services/OrderService.cs` pulls that file into context explicitly. `@docs` references your project documentation. This explicit context management makes a huge difference in output quality.

Inline editing (Cmd+K / Ctrl+K) lets you select code and describe a change in natural language. Cursor rewrites the selection in place. This is faster than chat for targeted edits: select a method, type "add caching with a 5-minute expiration," and the code transforms.

### Agent Mode

Cursor's Agent Mode (called Composer in earlier versions) is the most capable IDE agent as of early 2026. It handles multi-file editing, terminal execution, test running, and iterative development in a single flow.

The key differentiator: Cursor's agent is more autonomous than Copilot's. It will run commands, observe output, and iterate without asking for permission at every step (configurable, of course). For developers who trust the agent and have a good test suite, this means faster iteration cycles.

A typical Cursor Agent Mode workflow:

1. Open a new Composer tab
2. Describe the feature or fix
3. Cursor proposes a plan with file changes
4. You approve or modify the plan
5. Cursor executes, runs tests, fixes issues
6. You review the final diff

### Background Agents

This is Cursor's standout feature. Background Agents run in the cloud, working on tasks asynchronously while you continue coding. You describe a task, spin up a background agent, and it works independently. When it finishes, it creates a branch with its changes for your review.

The workflow is similar to cloud agents like Codex Cloud (covered in Chapter 12), but integrated directly into your editor. You can launch a background agent, switch to another task, and come back to review its work later.

Use cases that work well for Background Agents:

- Writing tests for existing code
- Refactoring large files into smaller ones
- Adding documentation comments
- Updating deprecated API calls
- Migrating configuration formats

Use cases that don't work well: anything requiring deep architectural understanding of runtime behavior, anything involving secrets or environment-specific configuration.

### Configuring Cursor

Cursor reads project rules from `.cursor/rules/` (the newer format) or `.cursorrules` (legacy, still supported). The newer format supports path-scoped rules:

```
.cursor/
  rules/
    general.mdc       # Always applied
    csharp.mdc         # Applied when editing .cs files
    testing.mdc        # Applied when editing test files
```

A `.mdc` rule file looks like this:

```markdown
---
description: Rules for C# source files
globs: ["**/*.cs"]
---

# C# Conventions

- Use file-scoped namespaces
- Prefer primary constructors where appropriate
- Use `required` keyword for mandatory properties on DTOs
- Collections should use IReadOnlyList<T> in return types
- Always use async/await for I/O operations, never .Result or .Wait()
```

The glob-based scoping is powerful. You can have different rules for your API layer, your domain layer, and your test project. The agent only sees the rules relevant to the files it's currently working with.

### Cursor's Cost

Cursor Pro runs $20/month and includes generous usage of fast models. The Business plan at $40/month adds admin controls and team features. Compared to Copilot ($10/month for Individual, $19/month for Business), Cursor is more expensive but includes more capable agent features.


## Windsurf (Codeium): The Underdog Worth Watching

Windsurf, built by Codeium, takes a different approach. While Copilot and Cursor focus on individual agent interactions, Windsurf centers its experience around what it calls Cascade and Flows.

### Cascade

Cascade is Windsurf's agent mode, and its defining characteristic is deep codebase awareness. When you make a request, Cascade automatically identifies relevant files across your entire project, pulling them into context without you having to `@mention` anything. It reads your project structure, understands import chains, and follows references.

For large codebases, this automatic context gathering is genuinely useful. You don't have to know which files are relevant; Cascade figures it out. The trade-off is that it can sometimes pull in too much context, slowing down responses on very large projects.

### Flows

Flows are Windsurf's take on multi-step workflows. Instead of a single prompt-response cycle, a Flow maintains state across multiple interactions, remembering what you've done and building on it. This is useful for complex tasks that unfold over multiple prompts: "First set up the database model, then create the repository, then add the API endpoint, then write the tests."

Each step in a Flow has access to the results of previous steps, which reduces the context you need to provide manually.

### Where Windsurf Shines

Windsurf's free tier is the most generous of any IDE agent. You get meaningful access to AI features without paying anything, which makes it a solid choice for developers who want to try agentic development without committing to a subscription.

Windsurf also handles large monorepo codebases better than Cursor or Copilot in my experience. The automatic context gathering, while sometimes over-eager, scales better than manual `@mentions` when you're working across dozens of projects in a single solution.

### Configuration

Windsurf reads project-level instructions from `.windsurfrules` in your project root. The format is similar to `.cursorrules`: plain markdown describing your conventions and preferences.

## JetBrains AI Assistant

If you're a Rider user (and many .NET developers are), JetBrains AI Assistant deserves a mention. It integrates directly into Rider's existing refactoring, inspection, and navigation features, which gives it an advantage in code-aware suggestions.

The AI Assistant can generate code, explain unfamiliar code, suggest refactorings, and write tests. It's competent but not best-in-class for agentic workflows. As of early 2026, JetBrains doesn't offer the same level of autonomous agent mode that Copilot, Cursor, and Windsurf provide. It's more of an enhanced assistant than a true agent.

Where it does excel: if you're deeply embedded in the JetBrains ecosystem and use Rider's refactoring tools heavily, the AI Assistant enhances those existing workflows rather than replacing them. It suggests ReSharper-style fixes powered by AI, which feels natural if you're already a Rider power user.

JetBrains also announced Junie, their dedicated coding agent, which operates more autonomously. Keep an eye on it, but as of this writing, it's still catching up to the competition in capability.

## The Decision Matrix

Here's when to reach for each tool:


**Choose Copilot when:**
- You want the most stable, well-integrated experience in VS Code or Visual Studio
- You're already paying for GitHub and want seamless repository integration
- You need inline completions that just work with minimal configuration
- Your team needs a single, standardized tool with admin controls
- You want access to multiple models (GPT-4.1, Claude) in one subscription

**Choose Cursor when:**
- You want the most powerful agent mode available in an IDE
- You use Background Agents for parallel async work
- You want fine-grained, path-scoped rules for your project
- You're comfortable with a VS Code fork (same extensions, slightly different update cycle)
- You're a power user who wants maximum control over AI interactions

**Choose Windsurf when:**
- You're working with large monorepos or complex multi-project solutions
- You want automatic context gathering without manual `@mentions`
- Budget matters and you want a strong free tier
- You prefer the Flows model for multi-step development tasks

**Choose JetBrains AI when:**
- Rider is your primary editor and you won't switch
- You want AI that enhances existing JetBrains refactoring workflows
- You value tight integration with ReSharper inspections

## Subscription Stacking: The Cost Reality

Let's talk money, because nobody else does.


Most serious agentic developers are paying for at least two subscriptions. A typical stack:

| Tool | Cost/Month | What You Get |
|------|-----------|--------------|
| GitHub Copilot Individual | $10 | Inline completions, Chat, Agent Mode |
| Cursor Pro | $20 | Tab, Chat, Agent, Background Agents |
| Claude Pro (for Claude Code) | $20 | CLI agent (covered in Chapter 12) |
| **Total** | **$50** | |

Is $50/month worth it? If you're billing $100+/hour and these tools save you even 30 minutes per day, that's over $1,500/month in recovered time. The math isn't even close.

But don't pay for redundancy. If you're using Cursor as your primary editor, you probably don't need Copilot's inline completions (Cursor's Tab is comparable). If you're using Copilot Agent Mode heavily, you might not need Cursor's agent features.

My recommendation: start with one tool, learn it deeply, then add a second only if you hit clear limitations. For most .NET developers, the highest-impact stack is Cursor (primary editor) plus Claude Code (CLI agent for terminal work). More on that combination in Chapter 12.

## Real Workflow: Building a Feature with an IDE Agent

Let's walk through a realistic workflow. You need to add a feature to an ASP.NET Core API: an endpoint that lets users export their order history as a CSV file.

**Step 1: Write the spec (you, not the agent)**

Before touching the IDE, write what you want in plain language. This becomes your prompt:

```
Add a GET /api/orders/export endpoint that:
- Returns a CSV file of the authenticated user's orders
- Includes columns: OrderId, Date, Status, Total, ItemCount
- Filters by optional date range (startDate, endDate query params)
- Returns 404 if the user has no orders
- Uses the existing IOrderRepository and ICurrentUserService
- Follows the existing controller patterns in OrdersController
- Add a unit test for the service method and an integration test for the endpoint
```

**Step 2: Let the agent work**

Paste this into Agent Mode (Copilot or Cursor). The agent will:
1. Create a `CsvExportService` with the export logic
2. Add the endpoint to `OrdersController`
3. Create a DTO for the query parameters
4. Write unit tests for the service
5. Write an integration test for the endpoint
6. Run the tests

**Step 3: Review**

This is where your expertise matters. Check:
- Does the CSV generation handle special characters (commas in product names)?
- Is the date filtering applied at the database level, not in memory?
- Are the tests testing behavior, not implementation?
- Does the endpoint properly handle the case where the date range is invalid?

**Step 4: Iterate**

Tell the agent what to fix. "The date filtering should be applied in the repository query, not after fetching all orders." The agent makes the change, reruns the tests, and you review again.

Total time: 15-20 minutes for a feature that would have taken an hour or more by hand. And the code is consistent with your existing patterns because the agent read your context files.

## Context Files: The Setup That Pays for Itself

Every IDE agent reads some form of project-level configuration. Here's a quick reference:


| Tool | File/Location | Format |
|------|--------------|--------|
| Copilot | `.github/copilot-instructions.md` | Markdown |
| Cursor | `.cursor/rules/*.mdc` or `.cursorrules` | Markdown with frontmatter |
| Windsurf | `.windsurfrules` | Markdown |
| Claude Code | `CLAUDE.md` | Markdown |
| Cross-tool | `AGENTS.md` | Markdown (emerging standard) |

The emerging `AGENTS.md` standard (from agents.md) aims to unify these into a single file that all tools can read. It's worth adopting now: put your main instructions in `AGENTS.md` at the project root, then create tool-specific files that reference or extend it.

What to put in these files was covered in depth in Chapter 4 (Context Engineering). The short version: build commands, architecture overview, coding conventions, testing patterns, and explicit "do not" rules. Keep it under 500 lines. Review and update it monthly.

## The Bottom Line

IDE agents are the most accessible entry point to agentic development. They meet you where you already work, in your editor, and they layer intelligence on top of your existing workflow.

But they're only one piece of the puzzle. For tasks that require deep codebase reasoning, long-running operations, or parallel execution, you need the tools covered in the next chapter: CLI agents and cloud agents. The real power comes from combining both.
