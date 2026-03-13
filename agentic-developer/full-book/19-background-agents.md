# Chapter 19: Background Agents and Async Workflows

There's a particular kind of satisfaction in assigning a coding task from your phone while lying on the couch, then waking up the next morning to a pull request waiting for review. It feels like having a junior developer who works overnight, doesn't need coffee, and never complains about the assignment.

That's the promise of background agents. And in early 2026, the promise is largely delivered.

Background agents represent a fundamentally different interaction model from the IDE-based and CLI-based agents we've covered so far. With those, you're present. You're watching, guiding, iterating in real time. Background agents are fire-and-forget. You describe the task, the agent works autonomously in a cloud sandbox, and you come back later to review the results.

This chapter covers how to use them effectively, which tasks to trust them with, and how to set up your repository so background agents can actually succeed.

## The Big Three

As of early 2026, three background agent platforms have meaningful traction.

### GitHub Copilot Coding Agent

Microsoft's entry works directly with GitHub Issues. You assign an issue to "Copilot," and the agent creates a branch, writes the code, runs your CI pipeline, and opens a pull request. The entire workflow happens inside GitHub's infrastructure.

The integration is the selling point. If your team already lives in GitHub Issues and Pull Requests, the Copilot Coding Agent slots into your existing workflow with zero friction. You don't need a new tool, a new dashboard, or a new process. You need an issue with a clear description.

In practice, the workflow looks like this:

1. Create a GitHub Issue: "Add rate limiting middleware to the API gateway. Use `AspNetCoreRateLimit` package. Apply a 100-requests-per-minute limit per API key. Return 429 with a `Retry-After` header. Add integration tests."
2. Assign the issue to Copilot.
3. Walk away.
4. Thirty minutes later (sometimes faster, sometimes slower), a PR appears with the implementation.

The quality of the PR is directly proportional to the quality of the issue description. Vague issues produce vague code. Detailed issues, with specific packages, patterns, test expectations, and error handling requirements, produce code that often needs only minor adjustments.

Between May and September 2025, GitHub reported over a million pull requests created by agents. That number has only grown. The Copilot Coding Agent is rapidly becoming the default way teams handle well-specified, moderate-complexity tasks.

### Codex Cloud (OpenAI)

OpenAI's Codex Cloud takes a different approach. Instead of integrating with your issue tracker, it provides a dedicated interface (web and mobile) where you describe tasks and the agent works in a sandboxed cloud environment with a full copy of your repository.

The key differentiator is the mobile experience. You can launch a Codex task from your phone while commuting, while cooking dinner, while waiting for a meeting to start. The agent clones your repo, sets up the environment, writes the code, runs the tests, and presents you with a diff to review.

Codex Cloud is particularly good for the "I just thought of something" workflow. You're in the shower and realize you forgot to add input validation to the new endpoint. Pull out your phone, describe the task, fire it off. By the time you're dressed, the PR is ready.

The tradeoff is that Codex Cloud operates in a sandbox that may not perfectly replicate your development environment. Complex build configurations, private NuGet feeds, or environment-specific dependencies can cause issues. The setup cost is higher, but once configured, the async workflow is seamless.

### Google Jules

Google's Jules operates similarly to Codex Cloud but with tighter integration into the Google Cloud ecosystem. For teams already on Google Cloud, Jules provides a natural extension of their development workflow.

Jules has been particularly strong at multi-file refactoring tasks and framework migrations. Its context window and planning capabilities make it well-suited for tasks that require understanding broad codebase patterns before making changes.

### Others Worth Watching

The background agent space is evolving rapidly. Amazon Q Developer handles AWS-centric tasks. Various startups (Sweep, Devin's async mode, and others) offer specialized background agent capabilities. The common thread is the same: describe a task, let the agent work, review the result.

## The "Launch and Review" Model


Background agents enable a workflow pattern I call "launch and review." It's simple in concept and transformative in practice.

**Evening (15-20 minutes): Launch**

Before you close your laptop for the day, review your backlog. Pick 2-4 tasks that are well-specified, independent, and testable. Write clear descriptions (or use pre-written specs from your task board). Assign them to background agents.

```
Task 1: Add health check endpoints for all external dependencies
         (database, Redis, message broker). Use AspNetCore.HealthChecks
         packages. Register in Program.cs. Add integration tests.

Task 2: Migrate the UserService from the old repository pattern to
         the new CQRS pattern. Follow the pattern established in
         OrderService. Update all tests.

Task 3: Add structured logging with Serilog to the PaymentController.
         Log request/response for all endpoints. Mask sensitive fields
         (card numbers, CVV). Add unit tests for the masking logic.
```

**Morning (30-45 minutes): Review**

You sit down with coffee and three pull requests waiting. You review each one, leave comments where needed, approve the ones that pass muster, and request changes on the ones that don't. The agents iterate on your feedback while you move to your day's primary work.

This model effectively gives you a few extra hours of productive output per day, but those hours happen while you're sleeping, eating, or living your life. Over a week, that's 10-20 additional hours of implementation work. Over a month, it's the equivalent of having a part-time developer on your team.

### The Morning Review Ritual

The review part of this workflow deserves its own process. Here's what works:


1. **Start with CI status.** If the tests failed, don't even look at the code yet. Check the failure, decide if it's an agent issue or a flaky test.
2. **Read the PR description.** Good background agents write detailed PR descriptions explaining what they did and why. Read this first for context.
3. **Scan the diff for red flags.** Security issues, deleted tests, changed configurations, new dependencies. These are the high-signal areas.
4. **Check test coverage.** Did the agent write tests? Do they test meaningful behavior or just cover lines?
5. **Run the code locally if needed.** For UI changes or complex integrations, pull the branch and verify manually.

Most well-specified background agent PRs take 5-10 minutes to review. If you're consistently spending 30+ minutes reviewing a single agent PR, the specs need work.

## What Works Well for Background Agents

Background agents excel at specific categories of work. Understanding these categories helps you assign the right tasks and avoid frustration.

### Well-Specified Implementation Tasks

"Add endpoint X with behavior Y, error handling Z, and tests A, B, C." When you've done the thinking and the agent does the typing, background agents are remarkably effective. The spec is the product. The code is just the mechanical output.

### Repetitive Refactoring

"Convert all 15 repository classes from the old interface to the new interface." Humans hate this work. It's tedious, error-prone, and mind-numbing. Agents love it. They don't get bored, they don't skip classes, and they apply the pattern consistently.

### Test Generation

"Add unit tests for all public methods in the PaymentService. Cover happy path, error cases, and edge cases. Use xUnit and NSubstitute. Follow the patterns in existing test files." Test generation is one of the highest-ROI uses of background agents. The work is well-defined, the quality is easy to verify (do the tests actually test meaningful behavior?), and the result directly improves your codebase.

### Documentation

"Generate XML documentation for all public APIs in the `Services` namespace. Include parameter descriptions, return value descriptions, and example usage where appropriate." Documentation is another task that's easy to specify, easy to verify, and miserable for humans to do manually.

### Dependency Updates

"Update `Microsoft.EntityFrameworkCore` from 8.x to 9.x. Fix all breaking changes. Ensure all tests pass." Package updates with breaking changes are a perfect background agent task. The agent can read the migration guide, apply the changes, and iterate until the build passes.

## What Doesn't Work

Background agents fall apart on certain categories of tasks, and knowing these boundaries saves you from wasted cycles and frustrating mornings.

### Ambiguous Requirements


"Improve the user experience of the dashboard." Improve how? For whom? By what metric? Background agents can't read your mind. They'll make choices, and those choices will be different from what you wanted. Then you'll spend more time understanding and undoing their work than it would have taken to do it yourself.

### Tasks Requiring Clarification

If a task would make a human developer walk over to your desk and ask three questions before starting, a background agent will either guess wrong or get stuck. Background agents don't (yet) have a good mechanism for asking clarifying questions mid-task. They make their best guess and ship it.

### Complex Architectural Decisions

"Design the caching strategy for our microservices." Designing is your job. Implementing a well-specified caching strategy is the agent's job. Don't confuse the two.

### Tasks With Heavy External Dependencies

If the task requires access to a running database, a third-party sandbox API, or a specific hardware configuration, background agents in cloud sandboxes will struggle. They work best when the codebase is self-contained enough to build and test in isolation.

### Deeply Interconnected Changes

Changes that touch many parts of the system simultaneously (cross-cutting concerns like changing your error handling strategy or your logging format) are risky for background agents. The agent might make the change correctly in 18 out of 20 places and subtly wrong in the other 2. Those 2 become bugs that are hard to find during review.

## Setting Up Your Repo for Background Agent Success


Background agents clone your repo and try to build it. If that process is fragile, undocumented, or dependent on local state, the agent will fail before it writes a single line of code.

### The README Test

Can a new developer clone your repo, follow the README, and have a running application with passing tests within 10 minutes? If no, fix that first. Background agents are effectively new developers joining your team every time they pick up a task.

### Deterministic Builds

Use lock files (`packages.lock.json` in .NET, or enable central package management). Pin your SDK version with `global.json`. Ensure `dotnet build` and `dotnet test` work from a clean clone without any manual setup.

```json
// global.json
{
  "sdk": {
    "version": "9.0.200",
    "rollForward": "latestPatch"
  }
}
```

### Context Files

Background agents read your `AGENTS.md`, `.github/copilot-instructions.md`, or equivalent context files. These files are even more important for background agents than for interactive ones, because you can't course-correct in real time.

Your context files should include:

- Build and test commands
- Architecture overview (what's in each project/folder)
- Coding conventions (naming, patterns, error handling approach)
- What NOT to do (common mistakes, deprecated patterns)
- Test expectations (framework, mocking library, coverage requirements)

### Comprehensive Test Suites

This is the most important factor. Background agents use tests as their feedback loop. When an agent writes code and runs the tests, failures tell it what to fix. Without tests, the agent has no signal. It writes code that compiles and calls it done.

The more comprehensive your tests, the higher quality output you'll get from background agents. This is one of those cases where investment in testing pays dividends in an entirely unexpected way: it makes your agents better.

### CI Pipeline That Runs on PRs

Background agents, especially the GitHub Copilot Coding Agent, rely on your CI pipeline to validate their work. If your pipeline doesn't run on pull requests, or if it's slow (30+ minutes), or if it has flaky tests, the agent's feedback loop is broken.

Fast, reliable CI is a prerequisite for effective background agents. Aim for under 10 minutes from push to green (or red). Every minute of CI time is a minute the agent waits before it can iterate.

## Real Workflow: Overnight Agent Tasks

Let's walk through a concrete weekly workflow using background agents.

### Monday Evening

You've been planning the week's work. You have a feature (order export) that you'll build yourself, but there are several supporting tasks that are well-defined:

```
Issue #234: Add CSV export utility class with unit tests
Issue #235: Add PDF generation service using QuestPDF with unit tests
Issue #236: Update API documentation for the export endpoints
Issue #237: Add rate limiting to the export endpoint (100/hour/user)
```

You assign Issues #234 and #235 to the Copilot Coding Agent. You fire #236 to Codex Cloud from your phone while watching TV. #237 can wait until the export endpoint exists.

### Tuesday Morning

Three PRs are waiting:

- **#234 (CSV utility):** Clean implementation, tests pass, one minor issue (used `StringBuilder` instead of `CsvHelper`). You leave a comment, the agent fixes it in 5 minutes. Merge.
- **#235 (PDF service):** Solid work. The agent even added a table of contents for exports with many orders. Tests pass. Merge.
- **#236 (API docs):** Accurate documentation based on the existing endpoint signatures. A few descriptions could be more specific. You edit them directly (faster than requesting changes for docs). Merge.

Total review time: 25 minutes. You now have three pieces of infrastructure ready for the export feature you're building today. You saved roughly 4-6 hours of implementation work.

### Tuesday - Thursday

You continue this pattern. Each evening, review the backlog, pick 2-3 tasks, assign them to agents. Each morning, review PRs, merge, move on. By Thursday, you've completed roughly twice the throughput of a normal week, with the same number of working hours.

### The Compounding Effect

Over a month, background agents contribute the equivalent of 40-80 hours of additional implementation work. That's not a rounding error. That's a full extra developer's output. The cost is subscription fees (covered in Chapter 22) and 30-45 minutes of review per morning.

The developers who get the most from background agents are the ones who build a pipeline. They maintain a backlog of well-specified, agent-ready tasks. They write specs as part of their planning process, not as an afterthought. They treat background agents as a permanent part of their team's capacity.

## The Trust Calibration

Background agents require a different trust model than interactive agents. With an interactive agent, you're watching it work. You catch mistakes in real time. With a background agent, you're reviewing after the fact. The mistakes are already in the code when you see them.

This means your review process needs to be more rigorous, not less. Don't merge background agent PRs without:

1. Reading the full diff (not just the summary)
2. Checking that tests exist AND test meaningful behavior
3. Verifying security-sensitive code (auth, input validation, data access)
4. Running the test suite locally for complex changes

Over time, you'll calibrate your trust. You'll learn which categories of tasks your background agents handle reliably and which ones need extra scrutiny. You'll learn to write specs that produce consistently good results. You'll develop a sixth sense for which PRs need a deep review and which ones are rubber-stamp merges.

That calibration is earned, not assumed. Start with more review, not less. Relax as you build confidence. And never stop reading the diffs.
