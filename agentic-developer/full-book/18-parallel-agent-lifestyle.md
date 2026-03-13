# Chapter 18: The Parallel Agent Lifestyle

You have one brain. You have one set of eyes. And starting today, you have five agents.


This is the parallel agent lifestyle, and it changes everything about how you structure your workday. Not because the tools are flashy, but because the economics are different. When code generation takes seconds and review takes minutes, the bottleneck shifts from "how fast can I write" to "how fast can I review." And the only way to maximize review throughput is to have work ready to review at all times.

Simon Willison, creator of Datasette and one of the most public practitioners of agentic development, described his daily workflow in late 2025: three to five agents running simultaneously, each on a different task, each producing work he could review in bursts. He was skeptical at first. Then he wasn't. "The natural bottleneck," he said, "is how fast I can review."

That's the insight this chapter is built on. You're not trying to replace yourself with agents. You're trying to keep yourself, the reviewer, fully utilized.

## The Four Categories


Not all agent tasks are created equal. Willison identified four categories of work that parallelize well, and this framework has held up under heavy use by thousands of developers since.

### 1. Research and Proof-of-Concept

"How does the Stripe subscription API handle prorated upgrades?" "What's the recommended way to implement distributed caching with Redis in .NET Aspire?" "Show me three different approaches to implementing event sourcing in C#."

These are research tasks. The agent reads documentation, explores APIs, builds small prototypes, and reports back. You don't need to review these with the same rigor as production code. You're gathering information, not shipping features.

Research agents are the lowest-risk parallel work. If the agent goes sideways, you've lost nothing. If it finds something useful, you've saved an hour of reading docs.

### 2. Codebase Questions

"How does our authentication middleware work?" "Trace the request flow from the API gateway to the order service." "What's the relationship between the User aggregate and the Permission entities?"

These are codebase archaeology tasks. The agent reads your code, follows the call chains, and produces documentation that helps you (or your teammates) understand what exists. This is one of the most underrated uses of agents: generating internal documentation from code.

The output is markdown, not code. The review is fast: does this accurately describe what I know about the system? If yes, you've just created documentation that would have taken a junior developer a full day to write.

### 3. Small Maintenance Tasks

Fix deprecation warnings. Update a NuGet package and fix the breaking changes. Rename a poorly named class across the codebase. Add XML documentation to public APIs. Convert a set of classes from the old pattern to the new pattern.

Maintenance tasks are the bread and butter of parallel agents. They're well-defined, low-risk, and tedious for humans. An agent can churn through 50 deprecation warnings while you focus on actual feature work. The review is mechanical: did it fix the warnings without changing behavior? Run the tests and move on.

### 4. Carefully Specified Implementation Work

This is the high-value category, and the one that requires the most discipline. You write a specification, the agent implements it. The specification has to be precise enough that you'd feel comfortable handing it to a junior developer, because that's essentially what you're doing.

"Implement a `SubscriptionService` that handles plan upgrades with prorated billing. Use the Stripe API via `IStripeClient`. Return `Result<Subscription>` for all operations. Handle these error cases: invalid plan, payment failed, already subscribed. Write unit tests using xUnit and NSubstitute. Follow the existing service patterns in `src/Services/`."

That's a spec that produces reviewable output. Contrast it with "build the subscription feature," which produces code you'll spend more time understanding than you saved.

## Git Worktrees: The Practical Foundation

You can't run three agents in the same directory. They'll step on each other's files, create merge conflicts in real time, and generally make a mess. Git worktrees solve this problem elegantly.


A worktree is a separate working directory that shares the same Git repository. Each worktree has its own branch, its own file state, and its own index. But they all share the same `.git` directory, which means they share history, remotes, and refs.

Here's the setup:

```bash
# You have your main repo
cd ~/repos/my-app

# Create worktrees for parallel agent sessions
git worktree add ../my-app-agent1 -b agent/subscription-service
git worktree add ../my-app-agent2 -b agent/fix-deprecations
git worktree add ../my-app-agent3 -b agent/add-caching
```

Now you have four directories:

```
~/repos/my-app/           # Your main working copy
~/repos/my-app-agent1/    # Agent 1: subscription service
~/repos/my-app-agent2/    # Agent 2: deprecation fixes
~/repos/my-app-agent3/    # Agent 3: caching layer
```

Each agent gets its own terminal, its own worktree, its own branch. They can all build and run tests independently. No conflicts. No coordination needed.

When an agent finishes, you review the diff, merge the branch, and either reuse the worktree for the next task or tear it down:

```bash
# Clean up a finished worktree
git worktree remove ../my-app-agent2
```

### The Worktree Workflow in Practice

Here's what a typical morning looks like with worktrees:

```bash
# Terminal 1: Main work (you're here)
cd ~/repos/my-app

# Terminal 2: Launch agent on subscription feature
cd ~/repos/my-app-agent1
claude "Implement the SubscriptionService according to the spec in docs/subscription-spec.md"

# Terminal 3: Launch agent on maintenance
cd ~/repos/my-app-agent2
claude "Fix all CS0618 deprecation warnings in the src/ directory. Run dotnet build after each fix to verify."

# Terminal 4: Launch agent on research
cd ~/repos/my-app-agent3
claude "Explore how to integrate Redis caching with our existing IRepository pattern. Build a proof-of-concept in a new CachingRepository class."
```

You've just launched three agents. Total time: maybe five minutes to write the prompts. Now you go back to Terminal 1 and do your own work (the thing that actually requires your brain, like architectural design or a complex algorithm).

Thirty minutes later, Agent 2 finishes the deprecation fixes. You review the diff (2 minutes), run the tests (they pass), merge the branch. That worktree is now free for the next task.

An hour later, Agent 1 has the subscription service roughed out. You review, leave some feedback ("use the Result pattern, not exceptions, for business logic failures"), and let it iterate.

Agent 3 comes back with a caching proof-of-concept and a write-up. You read the summary, decide the approach is sound, and file it away for tomorrow's implementation.

## Task Decomposition: The Parallel Mindset

The hardest part of parallel agents isn't the tooling. It's learning to think in parallel. Most developers are trained to work sequentially: finish one thing, start the next. Parallel agents require you to decompose work differently.

The key question isn't "what do I need to build?" It's "what can I break into independent pieces that don't touch the same files?"

### Good Decomposition

Consider building a new feature: order notifications. A customer places an order, and the system sends email and SMS notifications. Here's how you might decompose it:

**Agent 1: Notification Domain Model**
- `Notification` entity, `NotificationType` enum, `INotificationRepository`
- Unit tests for the domain model
- Files touched: `src/Domain/Notifications/`, `tests/Domain.Tests/Notifications/`

**Agent 2: Email Integration**
- `EmailNotificationSender` implementing `INotificationSender`
- Integration with SendGrid via `ISendGridClient`
- Files touched: `src/Infrastructure/Email/`, `tests/Infrastructure.Tests/Email/`

**Agent 3: SMS Integration**
- `SmsNotificationSender` implementing `INotificationSender`
- Integration with Twilio via `ITwilioClient`
- Files touched: `src/Infrastructure/Sms/`, `tests/Infrastructure.Tests/Sms/`

**You (manually): Orchestration**
- `NotificationOrchestrator` that ties it all together
- Integration tests that verify the full flow
- This is the part that requires understanding all three pieces

Notice the pattern: each agent works in a different directory, on a different concern, with a shared interface (`INotificationSender`) that you defined upfront. The interface is the contract. The agents implement it independently. You wire it together.

### Bad Decomposition

"Agent 1, build the backend. Agent 2, build the frontend. Agent 3, write the tests."


This fails because the agents are working on the same conceptual feature from different angles, which means they'll make conflicting assumptions. Agent 1 designs the API one way, Agent 2 expects it another way, and Agent 3 tests assumptions that match neither.

The rule of thumb: **decompose by bounded context or module, not by layer.** Each agent should own a vertical slice, not a horizontal layer.

### The Interface-First Pattern

The best parallel agent workflows start with interfaces. Before launching any agents, you define the contracts:

```csharp
public interface INotificationSender
{
    Task<Result<NotificationReceipt>> SendAsync(
        Notification notification,
        CancellationToken cancellationToken = default);
}

public interface INotificationRepository
{
    Task<Result<Notification>> GetByIdAsync(
        NotificationId id,
        CancellationToken cancellationToken = default);
    
    Task<Result> SaveAsync(
        Notification notification,
        CancellationToken cancellationToken = default);
}
```

These interfaces go into your main branch. Every worktree gets them. Every agent codes against them. Conflicts become nearly impossible because each agent is implementing a different side of the same contract.

This is spec-first development taken to its logical conclusion. The interfaces ARE the spec. The agents implement. You review.

## Managing the Review Bottleneck


Here's the uncomfortable truth about parallel agents: the more agents you run, the more review work piles up. And if you let that pile grow, you lose the context that makes review efficient.

Three parallel agents producing 200-400 lines each gives you 600-1,200 lines to review. That's a big pull request by any standard. If you wait until all three are done and review them in a batch, you're going to miss things.

### The Continuous Review Model

The better approach is continuous review. Instead of "launch everything, review later," you treat agent output like a stream.

**Check in every 20-30 minutes.** Glance at agent progress. If one is done, review it immediately while the context is fresh. If one is stuck or going in the wrong direction, intervene early.

**Review in order of complexity.** Start with the maintenance tasks (mechanical review: did the tests pass?). Move to the research (conceptual review: is this approach sound?). Finish with the implementation (deep review: is this correct, secure, maintainable?).

**Timebox reviews.** If a review is taking more than 15 minutes, the spec wasn't precise enough. Don't fix the code yourself. Fix the spec and re-run the agent. This feels slower in the moment but builds the habit of writing better specs.

### You Are the Limiting Factor

This is the mindset shift that trips people up. In traditional development, the limiting factor is typing speed, comprehension speed, the raw mechanics of turning thoughts into code. With agents, you are no longer limited by production. You are limited by consumption.

Your job is to stay fed. Always have something to review. Always have agents working on the next batch. The moment you're sitting idle while agents work, you've under-scheduled. The moment you're drowning in unreviewed output, you've over-scheduled.

Three to five parallel agents is the sweet spot for most developers. Fewer than three and you'll have idle time. More than five and the review backlog becomes unmanageable. Find your personal number and stay there.

## The Daily Rhythm


After a few weeks of parallel agent work, a natural rhythm emerges. Here's what a typical day looks like:

### Morning (9:00 - 9:30): Launch and Spec

Review any overnight agent work (if you're using background agents, covered in Chapter 19). Write specs for the day's major tasks. Launch 2-3 agents on morning work.

Your morning specs are the most important writing you'll do all day. Spend the time. A 15-minute spec saves an hour of back-and-forth.

### Late Morning (10:00 - 12:00): Deep Work + Review Cycles

Do your own deep work (architecture, complex problems, meetings). Check agent progress every 30 minutes. Review completed work. Re-launch agents on new tasks as old ones finish.

This is the productive core of the day. You're doing human-level thinking while agents handle implementation. The review breaks actually help your own work by providing natural Pomodoro-style intervals.

### Afternoon (13:00 - 15:00): Integration and Second Wave

Merge morning agent work. Handle integration issues (the places where separately developed pieces don't quite fit). Launch afternoon agents on the next batch of tasks.

Integration is where your expertise matters most. The agents built the pieces. You're fitting them together, resolving the assumptions that don't align, and making architectural adjustments.

### Late Afternoon (15:00 - 17:00): Review and Polish

Final review pass on the day's agent output. Write specs for tomorrow's morning tasks (or for overnight background agents). Clean up, commit, push.

Writing tomorrow's specs today means you can launch agents the moment you sit down in the morning. The parallel lifestyle rewards preparation.

## When Parallel Helps vs. When It Creates Chaos

Parallel agents are not universally better. There are specific conditions where they shine and specific conditions where they make things worse.

### Parallel Helps When:

**Tasks are genuinely independent.** Different modules, different files, different concerns. The agents don't need to know about each other's work.

**You have a strong test suite.** Tests are the fastest review mechanism. If the tests pass and they're comprehensive, you can merge with high confidence. If you don't have tests, every review becomes a manual audit.

**Interfaces are defined upfront.** When agents code against shared contracts, they produce compatible work. Without contracts, you're merging assumptions, not code.

**Tasks are well-specified.** The spec is the multiplier. Good specs produce good code from multiple agents simultaneously. Bad specs produce bad code from multiple agents simultaneously (which is worse, because you have more bad code to deal with).

### Parallel Creates Chaos When:

**Tasks have hidden dependencies.** "Build the payment system" and "build the order system" sound independent until you realize they both need to update the same `Order` entity. Two agents editing the same file is a recipe for merge conflicts and logical inconsistencies.

**The codebase lacks boundaries.** If your code is a big ball of mud where everything touches everything, agents will create conflicts no matter how carefully you decompose. Parallel agents reward (and reveal) good architecture.

**You skip the review.** The temptation with parallel agents is to merge fast and move on. But every unreviewed merge is a time bomb. The debt compounds. Three agents producing unreviewed code for a week will create a codebase nobody understands, including you.

**You're exploring, not building.** When you don't know what you want yet, running three agents in three different directions doesn't help. It gives you three prototypes to evaluate instead of one, which sounds good until you realize evaluation takes longer than exploration.

## Practical Example: Building a Feature with Three Parallel Agents

Let's walk through a real example. You're building an order export feature for an e-commerce application. Customers can export their order history as CSV or PDF.

### Step 1: Define the Interfaces (15 minutes, you do this)

```csharp
public interface IOrderExporter
{
    Task<Result<ExportResult>> ExportAsync(
        ExportRequest request,
        CancellationToken cancellationToken = default);
}

public record ExportRequest(
    Guid CustomerId,
    ExportFormat Format,
    DateRange DateRange);

public enum ExportFormat { Csv, Pdf }

public record ExportResult(
    byte[] Content,
    string ContentType,
    string FileName);
```

### Step 2: Write Three Specs (20 minutes, you do this)

**Spec A (Agent 1): CSV Exporter**
> Implement `CsvOrderExporter : IOrderExporter`. Use CsvHelper for CSV generation. Query orders from `IOrderRepository.GetByCustomerIdAsync()`. Include columns: OrderId, Date, Items (comma-separated), Total, Status. Write unit tests with xUnit. Mock the repository with NSubstitute. Test empty orders, single order, multiple orders, and date range filtering.

**Spec B (Agent 2): PDF Exporter**
> Implement `PdfOrderExporter : IOrderExporter`. Use QuestPDF for PDF generation. Same data source as CSV. Include a header with customer name and export date. Table layout for order rows. Write unit tests. Test the same scenarios as the CSV exporter.

**Spec C (Agent 3): API Endpoint**
> Add a `POST /api/customers/{customerId}/orders/export` endpoint to the existing `CustomersController`. Accept `ExportRequest` as the body. Resolve the correct `IOrderExporter` from DI based on the format. Return `FileResult` with appropriate content type. Add integration tests using `WebApplicationFactory`. Test both formats, invalid customer, empty date range.

### Step 3: Launch (5 minutes)

```bash
# Three terminals, three worktrees, three agents
cd ~/repos/shop-agent1 && claude "$(cat ~/specs/csv-exporter.md)"
cd ~/repos/shop-agent2 && claude "$(cat ~/specs/pdf-exporter.md)"
cd ~/repos/shop-agent3 && claude "$(cat ~/specs/api-endpoint.md)"
```

### Step 4: Review and Merge (45 minutes over the next 2 hours)

Agent 2 finishes first (PDF generation is more complex, but QuestPDF has great docs and the agent nails it). You review: the code follows the existing patterns, the tests pass, the PDF looks reasonable. Merge.

Agent 1 finishes next. The CSV output is correct but the agent used manual string concatenation instead of CsvHelper. You point this out, the agent fixes it in 30 seconds. Merge.

Agent 3 finishes last (it needed to reference the other implementations for DI registration). You review the endpoint, run the integration tests, spot a missing authorization attribute (`[Authorize]`), the agent adds it. Merge.

Total time: about 40 minutes of your active attention, spread over 2 hours. What you got: a complete feature with two exporters, an API endpoint, unit tests, and integration tests. What it would have taken without agents: probably a full day.

That's the parallel agent lifestyle. Not magic. Not autopilot. But a fundamentally different ratio of effort to output.

## The Compound Effect

The real power of parallel agents isn't any single session. It's the compound effect over weeks and months. When you consistently produce 2-3x the output with roughly the same review quality, projects that used to take a quarter take a month. Features that used to take a sprint take a few days.

But only if you invest in the foundations: good architecture with clear boundaries, comprehensive tests, well-defined interfaces, and the discipline to write precise specs. Without those foundations, parallel agents just produce parallel messes faster.

The developers who thrive in the parallel agent lifestyle aren't the fastest coders. They're the clearest thinkers. They can decompose problems into independent pieces, specify them precisely, and review the results efficiently.

That's the new skill. And it's one worth developing.
