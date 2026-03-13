# Chapter 10: Designing an AI-Friendly Codebase

Here's the thing nobody tells you about agentic development: the biggest factor in agent output quality isn't your prompt, your context file, or your model choice. It's your codebase.

Your existing code is the single largest source of context an agent has. When an agent needs to add a feature, it reads your existing features. When it needs to write a test, it reads your existing tests. When it needs to follow a pattern, it looks at how you've implemented that pattern before.

A well-structured codebase makes agents dramatically more effective. A poorly structured one makes them confidently produce garbage that matches your existing garbage.

The practices in this chapter aren't new. They're the same engineering principles that senior developers have advocated for decades: clear naming, small focused files, good documentation, comprehensive tests. What's new is the payoff. These practices always helped human developers. Now they help AI agents too, and the compounding effect is enormous.

## Naming Conventions That Help Agents (and Humans)

Agents take names at face value. A human teammate might know that `OrderProcessor` actually handles payment processing because they sat in the meeting where someone named it badly. An agent doesn't have that institutional knowledge. It reads `OrderProcessor` and assumes it processes orders.

### Be Descriptive, Not Clever

```csharp
// Bad: What does this process?
public class OrderProcessor { }


// Good: Exactly what it does
public class OrderPaymentProcessor { }

// Bad: Manager of what? How?
public class DataManager { }

// Good: Specific responsibility
public class CustomerRepository { }
public class OrderCacheInvalidator { }
```

### Name Methods for Behavior, Not Implementation

```csharp
// Bad: Describes the mechanism
public async Task<List<Order>> RunQuery(string customerId) { }

// Good: Describes the behavior
public async Task<List<Order>> GetOrdersByCustomer(string customerId) { }

// Bad: Too generic
public async Task<Result> Process(Command command) { }

// Good: Clear intent
public async Task<Result<OrderConfirmation>> PlaceOrder(
    PlaceOrderCommand command) { }
```

### Use Consistent Naming Patterns

When agents see consistent patterns, they replicate them. If every handler in your project follows `{Action}{Entity}Handler`, the agent will follow the same pattern for new handlers. If your naming is inconsistent (some handlers are `{Entity}{Action}Handler`, others are `Handle{Entity}{Action}`), the agent picks whichever pattern it encounters first, which might not be your preferred one.

Document your naming conventions in AGENTS.md, but also follow them consistently. Agents learn more from your code than from your documentation.

```
Commands:  Create{Entity}Command, Update{Entity}Command, Delete{Entity}Command
Queries:   Get{Entity}Query, List{Entities}Query, Search{Entities}Query
Handlers:  {CommandOrQuery}Handler
Responses: {Entity}Response, {Entity}ListResponse
```

## File Size and Cohesion

This is the single highest-impact structural change you can make for agent effectiveness: keep files small and focused.

### Why Small Files Win

**Context windows are finite.** When an agent needs to modify a 2,000-line file, it has to load that entire file into context. That's expensive in tokens and leaves less room for other relevant context. A 50-line file leaves room for the agent to also read related files, tests, and documentation.

**Agents make fewer mistakes in small files.** A study by GitClear found a 4x increase in code clones when developers used AI assistants. The root cause: agents working with large, complex files produce more duplicate and inconsistent code. Small, focused files have clear boundaries that agents respect.

**Modifications are surgical.** When an agent needs to change one behavior in a small, focused file, it modifies the right thing. When it needs to change one behavior in a God class, it might accidentally affect other behaviors.

### The Practical Threshold

There's no magic number, but here's a useful guideline:


- **Under 100 lines:** Agent can fully understand and modify confidently
- **100-200 lines:** Agent handles well with good structure
- **200-500 lines:** Agent starts making more mistakes, missing context from distant parts of the file
- **Over 500 lines:** Expect quality issues, extract classes and methods

These aren't hard rules. A 300-line file with clear sections and good naming works fine. A 150-line file with tangled responsibilities is worse. Cohesion matters more than raw line count.

### Extracting for AI-Readability

If you have large files, refactoring them for agent-friendliness is the same as refactoring for human-friendliness: extract classes, extract methods, separate concerns.

```csharp
// Before: 800-line OrderService doing everything
public class OrderService
{
    public async Task<Result<Order>> PlaceOrder(...) { /* 100 lines */ }
    public async Task<Result> CancelOrder(...) { /* 80 lines */ }
    public async Task<Result> RefundOrder(...) { /* 120 lines */ }
    public async Task<List<Order>> GetOrderHistory(...) { /* 60 lines */ }
    public async Task<OrderReport> GenerateReport(...) { /* 150 lines */ }
    // ... more methods, private helpers, validation logic
}

// After: Focused files the agent can work with independently
public class PlaceOrderHandler { /* 60 lines */ }
public class CancelOrderHandler { /* 50 lines */ }
public class RefundOrderHandler { /* 70 lines */ }
public class GetOrderHistoryHandler { /* 40 lines */ }
public class GenerateOrderReportHandler { /* 80 lines */ }
```

Each handler can be modified without the agent needing to understand the others. Each can have its own test file. Each is small enough that the agent can hold the entire implementation in context.

## Project Structure Patterns

How you organize files determines how easily agents navigate your codebase.

### Feature Folders (Vertical Slices)

The most agent-friendly project structure groups code by feature, not by technical layer.

```
src/Api/
  Features/
    Orders/
      PlaceOrder/
        PlaceOrderCommand.cs
        PlaceOrderHandler.cs
        PlaceOrderValidator.cs
        PlaceOrderEndpoint.cs
        PlaceOrderTests.cs
      CancelOrder/
        CancelOrderCommand.cs
        CancelOrderHandler.cs
        CancelOrderEndpoint.cs
      GetOrderHistory/
        GetOrderHistoryQuery.cs
        GetOrderHistoryHandler.cs
        GetOrderHistoryEndpoint.cs
    Payments/
      ProcessPayment/
        ...
      RefundPayment/
        ...
```

Why this is agent-friendly:

**Locality of reference.** When an agent needs to work on order placement, everything it needs is in one folder. It doesn't need to navigate between `Controllers/`, `Services/`, `Models/`, and `Validators/` to understand one feature.

**Pattern replication.** When you say "add a feature to update order status," the agent looks at existing features, sees the consistent structure, and replicates it. The more consistent your feature folders, the better the agent's output.

**Isolation.** Changes to one feature don't require the agent to understand other features. This reduces the context needed per task.

### Layer-Based Structure (Traditional)

The traditional structure groups by technical layer:

```
src/Api/
  Controllers/
    OrdersController.cs
    PaymentsController.cs
  Services/
    OrderService.cs
    PaymentService.cs
  Models/
    Order.cs
    Payment.cs
  Validators/
    CreateOrderValidator.cs
    ProcessPaymentValidator.cs
```

This works but is less agent-friendly because a single feature is spread across multiple directories. The agent needs to navigate more files to understand one feature. It's not a dealbreaker, but feature folders give agents a meaningful advantage.

### The Hybrid Approach

Most real projects use a hybrid: feature folders for application logic, layer separation for cross-cutting concerns.


```
src/
  Api/
    Features/           # Vertical slices for business features
      Orders/
      Payments/
    Middleware/          # Cross-cutting (auth, error handling, logging)
    Infrastructure/     # Database, caching, external services
    Common/             # Shared types (Result<T>, PagedList<T>)
```

This gives agents the best of both worlds: feature locality for business logic, clear homes for shared concerns.

## Documentation-as-Context

Every piece of documentation in your repository is context that agents can read. The question is whether your documentation is useful to them.

### Architecture Decision Records (ADRs)

ADRs are the highest-value documentation for agents. They explain WHY your codebase is structured the way it is, which helps agents make decisions that align with your architectural intent.

```markdown
# ADR-003: Use Result Pattern Instead of Exceptions for Business Logic

## Status
Accepted

## Context
We need a consistent error handling approach for business logic.
Exceptions are expensive in .NET, difficult to compose, and make
control flow implicit.

## Decision
Use a Result<T> type for all business logic outcomes. Only use
exceptions for truly exceptional cases (infrastructure failures,
programming errors).

## Consequences
- Handlers return Result<T> instead of throwing
- Controllers map Result failures to HTTP status codes
- No try/catch in business logic layer
- All business error cases are explicit in the type signature
```

An agent reading this ADR understands not just the pattern but the reasoning. When it encounters a situation where throwing an exception might seem natural, it knows to use the Result pattern instead, and it knows why.

Store ADRs in `docs/adr/` or `docs/decisions/` and reference the directory in your AGENTS.md.

### Inline Comments: When and Why

Agents read comments. Strategic comments can prevent entire categories of mistakes.

**Comment the WHY, not the WHAT:**

```csharp
// BAD: Describes what the code does (the agent can read the code)
// Loop through orders and calculate total
foreach (var order in orders)
{
    total += order.Amount;
}

// GOOD: Explains why a non-obvious approach is used
// DECISION: Raw SQL here because EF Core generates a suboptimal
// execution plan for this specific join pattern. See ADR-007.
var orders = await db.Database.SqlQueryRaw<OrderDto>("""
    SELECT o.id, o.total, c.name
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.id
    WHERE o.created_at > @cutoff
    """, new NpgsqlParameter("cutoff", cutoffDate));

// GOOD: Warns about a non-obvious constraint
// WARNING: This method must be called BEFORE SaveChangesAsync
// because the domain events are cleared during save.
public IReadOnlyList<IDomainEvent> GetDomainEvents()
{
    return _domainEvents.AsReadOnly();
}
```

**Comment the boundaries:**

```csharp
// IMPORTANT: This endpoint is intentionally [AllowAnonymous]
// because it serves the public product catalog. Do not add [Authorize].
[AllowAnonymous]
[HttpGet]
public async Task<ActionResult<List<ProductResponse>>> ListProducts() { }
```

Without that comment, an agent following your "all endpoints require [Authorize]" convention would "helpfully" add authentication to your public catalog endpoint.

### README Patterns

Your project's README is one of the first things an agent reads. Make it useful:

```markdown
# MyApp API

Order management API for the MyApp platform.

## Quick Start
```bash
docker compose up -d    # Start dependencies (PostgreSQL, Redis, RabbitMQ)
dotnet run --project src/Api
```

## Architecture
Vertical slice architecture with CQRS. See [docs/adr/](docs/adr/) for decisions.

## Key Patterns
- **Commands/Queries:** MediatR handlers in Features/ folders
- **Error handling:** Result<T> pattern (no exceptions for business logic)
- **Testing:** xUnit + FluentAssertions + NSubstitute

## Project Map
- `src/Api/Features/` — Business features (vertical slices)
- `src/Api/Infrastructure/` — Database, caching, external services
- `tests/` — Unit and integration tests
- `docs/adr/` — Architecture decision records
```

Short, actionable, structured. An agent reading this knows how to build, where to find things, and what patterns to follow.

## The Test Suite as Your Most Powerful Context


Your test suite is arguably more valuable than your context file for agent quality. Here's why:

### Tests Are Executable Specifications

When an agent reads your tests, it learns:

1. **What the code should do.** Each test is a behavior specification. `PlaceOrder_WithValidItems_ReturnsConfirmation` tells the agent exactly what the happy path looks like.

2. **What edge cases matter.** `PlaceOrder_WithEmptyCart_ReturnsValidationError` tells the agent that empty carts are a case to handle.

3. **What patterns to follow.** Test structure, naming, mocking patterns, assertion styles, all of this teaches the agent how to write tests that match your standards.

4. **Whether changes work.** An agent that can run tests after making changes can self-correct. This is the most powerful feedback loop in agentic development.

### Tests Enable the Agent Self-Correction Loop

The most effective agentic workflow is test-first development:

1. You write (or describe) the test for the feature you want
2. The agent implements the feature
3. The agent runs the tests
4. If tests fail, the agent reads the error and fixes the code
5. Repeat until all tests pass

Without tests, the agent produces code and hopes it works. With tests, the agent iterates until it provably works. The difference in reliability is massive.

### Test Coverage and Agent Confidence

Higher test coverage means agents can make changes more confidently. If your project has 80%+ coverage:

- The agent can refactor safely (tests catch regressions)
- The agent can add features incrementally (tests verify each step)
- The agent can resolve conflicts (tests confirm correctness after merge)

If your project has 10% coverage:

- Every agent change is a gamble
- You manually verify everything
- Refactoring is risky

Investing in tests has always paid off. With agents, the ROI is 10x what it was.

## Anti-Patterns: What Makes Codebases AI-Hostile

### God Classes

A single class handling validation, business logic, data access, notification, and logging. Agents can't modify one concern without risking the others. The class is too large for the context window, and the tangled dependencies make changes unpredictable.

**Fix:** Extract each responsibility into its own class. Use dependency injection to compose them.

### Hidden Dependencies

Classes that reach into static state, service locators, or ambient contexts instead of declaring their dependencies explicitly.

```csharp
// AI-hostile: Hidden dependency on static context
public class OrderHandler
{
    public async Task Handle(CreateOrderCommand command)
    {
        var user = HttpContext.Current.User; // Where did this come from?
        var config = ConfigurationManager.AppSettings["MaxOrderSize"]; // And this?
        var db = DatabaseFactory.Create(); // And this?
    }
}

// AI-friendly: All dependencies visible
public class OrderHandler(
    ICurrentUser currentUser,
    IOptions<OrderSettings> settings,
    IOrderRepository repository)
{
    public async Task<Result<Order>> Handle(CreateOrderCommand command)
    {
        var user = currentUser.Get();
        var maxSize = settings.Value.MaxOrderSize;
        // Dependencies are clear, mockable, and discoverable
    }
}
```

Agents can only work with what they can see. Hidden dependencies are invisible to them.

### Convention-Free Codebases

When every file follows a different pattern, every class uses a different naming convention, and there's no consistency anywhere, agents have no patterns to replicate. They fall back on generic training data patterns, which probably don't match your project.

**Fix:** Pick conventions. Document them. Follow them. Consistency is free and compounds over time.

### Magic Strings and Numbers

```csharp
// AI-hostile: What do these mean?
if (order.Status == 3 && order.Total > 500)
{
    SendNotification("order-alert", order.CustomerId);
}

// AI-friendly: Self-documenting
if (order.Status == OrderStatus.Shipped && order.Total > OrderThresholds.HighValue)
{
    await notificationService.SendAsync(
        NotificationType.HighValueOrderShipped,
        order.CustomerId);
}
```

Agents can reason about `OrderStatus.Shipped`. They can't reason about `3`.

### Deep Inheritance Hierarchies

```csharp
// AI-hostile: Agent needs to trace 5 levels to understand behavior
public class PremiumOrderHandler
    : SpecialOrderHandler
    : OrderHandler
    : BaseHandler<Order>
    : AbstractHandler
    : IHandler { }
```


Each layer of inheritance is another file the agent needs to read and hold in context. Composition over inheritance isn't just cleaner for humans. It's dramatically easier for agents to work with.

## Refactoring for AI-Readability

If your codebase has some of these anti-patterns, here's the good news: refactoring for AI-readability is the same as refactoring for human-readability. Every change that helps agents also helps your team.

### Priority Order

1. **Extract God classes.** Highest impact. Split large classes into focused, single-responsibility classes.
2. **Make dependencies explicit.** Replace static access and service locators with constructor injection.
3. **Establish naming conventions.** Pick patterns and apply them consistently across new code. Gradually rename existing code.
4. **Add tests for untested areas.** Focus on the areas agents will modify most. Tests enable the self-correction loop.
5. **Write ADRs for non-obvious decisions.** Start with the decisions agents get wrong most often.
6. **Move to feature folders.** Reorganize from layer-based to feature-based structure, one feature at a time.

### The Incremental Approach

You don't need to refactor your entire codebase before using agents. That's backwards. Start using agents now. Pay attention to where they struggle. Refactor those areas first.

If agents keep producing bad code in your payment module because it's a 3,000-line God class, that's your signal to refactor the payment module. If agents handle your user module perfectly because it's clean and well-structured, leave it alone.

Let agent struggles guide your refactoring priorities. You're optimizing for the areas where it matters most.

## The Compound Effect

Every practice in this chapter reinforces the others:

- Clear naming makes small files easy to discover
- Small files make feature folders practical
- Feature folders make tests easy to colocate
- Colocated tests make agent self-correction possible
- Agent self-correction produces better code
- Better code is easier to name, keep small, and organize

This is why AI-friendly codebase design isn't a separate concern from good engineering. It IS good engineering. The practices that have always been best practices now have a measurable, immediate payoff through agent productivity.

Addy Osmani put it well: "AI-assisted development actually rewards good engineering practices MORE than traditional coding does." Every shortcut you took, every God class you tolerated, every naming convention you skipped, now costs you twice: once in human comprehension, and again in agent output quality.

The flip side is encouraging. Every investment in code quality now pays off twice too.

## Key Takeaways

1. **Your codebase is your largest context source.** How you structure it matters more than any context file.

2. **Small, focused files are the highest-impact change.** Under 100 lines per file is the sweet spot for agent effectiveness.

3. **Feature folders beat layer folders for agents.** Locality of reference reduces the context needed per task.

4. **Tests are your most powerful agent tool.** They specify behavior, enable self-correction, and give agents confidence to refactor.

5. **Name things for discoverability.** Agents read names literally. Clear, consistent naming compounds across every agent interaction.

6. **Document the WHY.** ADRs and strategic comments prevent entire categories of agent mistakes.

7. **Refactor incrementally, guided by agent struggles.** Fix the areas where agents produce the worst output first.

8. **AI-friendly and human-friendly are the same thing.** Every improvement for agents also improves your team's experience.

This concludes Part II: Context Engineering. You now have the complete toolkit: context files for project-wide guidance, path-scoped rules for targeted instructions, skills for complex workflows, MCP servers for external data access, and codebase design principles that make everything work better.

Part III shifts from preparation to execution: the workflows and practices that make day-to-day agentic development productive, reliable, and safe.
