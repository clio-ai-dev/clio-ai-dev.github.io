# Chapter 7: Path-Scoped Rules and When to Use Them

Your main context file handles the broad strokes. It tells agents how your project works, what conventions to follow, what patterns to use. But projects aren't monoliths. Your controllers have different conventions than your domain models. Your test files follow different rules than your migration scripts. Your frontend components live in a different world than your backend services.

Path-scoped rules solve this. They're modular, targeted instructions that only activate when an agent is working with matching files. Think of them as surgical context: the right guidance, at the right time, for the right code.

## Beyond the Main Context File

Chapter 6 gave you the AGENTS.md foundation. It works. But there's a ceiling to what a single file can do effectively.

Consider a typical .NET project. Your controllers should be thin wrappers around MediatR. Your domain entities should never reference infrastructure concerns. Your EF Core migrations should follow specific naming and ordering conventions. Your React components (if you have a frontend) use a completely different set of conventions.

Putting all of this in AGENTS.md creates the "Novel" anti-pattern from Chapter 6: a bloated file that degrades model performance through sheer volume. Path-scoped rules let you keep each concern separate, loading only what's relevant.

The principle is simple: **give the agent the minimum context it needs for the specific file it's editing.**

## How Path-Scoped Rules Work


### Claude Code: .claude/rules/

Claude Code stores path-scoped rules in the `.claude/rules/` directory. Each rule is a markdown file with a description and glob patterns that determine when it activates.

The structure looks like this:

```
.claude/
  rules/
    controllers.md
    tests.md
    migrations.md
    frontend.md
    domain.md
```

Each file contains a YAML frontmatter block specifying when it applies, followed by the actual instructions:

```markdown
---
description: Conventions for API controllers
globs: src/Api/Controllers/**/*.cs
---

Controllers are thin. Three responsibilities only:
1. Validate the request
2. Send a command/query via MediatR
3. Map the result to an HTTP response

No business logic. No direct database access. No try/catch blocks.
```

When an agent opens or modifies a file matching `src/Api/Controllers/**/*.cs`, these rules load automatically. When it's editing a test file, the controller rules stay dormant. The agent sees only what it needs.

### Cursor: .cursor/rules/

Cursor uses the same concept with `.cursor/rules/` directory. The format is slightly different but the idea is identical: markdown files with glob patterns that scope when rules activate.

```markdown
---
description: Testing conventions
globs: tests/**/*.cs
---

Use xUnit, FluentAssertions, NSubstitute. No other test libraries.
```

### The Universal Pattern

Regardless of tool, the pattern is the same:

1. A directory of markdown files
2. Each file targets specific paths using glob patterns
3. Rules load automatically when the agent touches matching files
4. Rules supplement (don't replace) the main context file

If you're using a tool that doesn't support path-scoped rules natively, you can approximate them by including relevant instructions in your prompts when working on specific areas. But native support is better because it's automatic: you don't have to remember to include the right context.

## Glob Patterns and File-Type Matching


Glob patterns determine when your rules fire. Getting them right matters. Too broad and you're loading irrelevant context. Too narrow and the rules miss files they should cover.

### Common Patterns

```
src/Api/Controllers/**/*.cs     # All C# files under Controllers, any depth
tests/**                         # Everything in the tests directory
**/*.test.cs                     # Any test file anywhere in the project
src/Infrastructure/Data/*.cs     # Migration and DbContext files
src/**/Models/*.cs               # Model files in any project
*.proto                          # Protocol buffer definitions
docker-compose*.yml              # All docker-compose variants
```

### Pattern Tips

**Use `**` for recursive matching.** `src/Api/*.cs` only matches files directly in the Api folder. `src/Api/**/*.cs` matches everything in Api and all subdirectories.

**Be specific about file extensions.** `tests/**` matches everything, including JSON fixtures, text files, and markdown. `tests/**/*.cs` matches only C# files, which is usually what you want for coding conventions.

**Match by convention, not just location.** If your test files follow a naming pattern like `*.Tests.cs`, you can use `**/*.Tests.cs` to catch them regardless of directory structure. This is more resilient to project restructuring.

**Avoid overlapping patterns.** If `src/**/*.cs` loads one set of rules and `src/Api/**/*.cs` loads another, files in `src/Api/` get both. This isn't necessarily a problem, but conflicting instructions between the two will confuse the agent. Be intentional about overlap.

## Real Examples

Here's a complete set of path-scoped rules for a typical .NET project. Each one addresses real problems I've seen agents get wrong repeatedly.

### Controller Rules

File: `.claude/rules/controllers.md`

```markdown
---
description: API controller conventions
globs: src/Api/Controllers/**/*.cs
---

# Controller Conventions

Controllers are thin orchestrators. They do NOT contain business logic.

## Structure
Every action method follows this pattern:
1. Accept the request (model binding handles validation)
2. Send a command or query via MediatR
3. Map the Result<T> to an ActionResult

## Template
```csharp
[HttpPost]
public async Task<ActionResult<OrderResponse>> Create(
    [FromBody] CreateOrderRequest request)
{
    var result = await sender.Send(
        new CreateOrderCommand(request.Sku, request.Quantity));

    return result.Match<ActionResult<OrderResponse>>(
        order => CreatedAtAction(nameof(Get), new { id = order.Id }, order),
        error => error.ToProblemDetails()
    );
}
```

## Rules
- Use primary constructors for dependency injection
- Always include [Authorize] unless the endpoint is explicitly public
- POST returns 201 with Location header
- PUT and PATCH return 204 (no content)
- DELETE returns 204
- Use [FromRoute], [FromQuery], [FromBody] explicitly
- No try/catch (global exception middleware handles it)
- No logging in controllers (middleware handles request logging)
```

### Test Rules

File: `.claude/rules/tests.md`

```markdown
---
description: Testing patterns and conventions
globs: tests/**/*.cs
---

# Testing Conventions

## Libraries
- xUnit for test framework
- FluentAssertions for assertions
- NSubstitute for mocking
- Do NOT use Moq, MSTest, or any other test library

## Unit Tests
- One test class per handler/service
- Test name format: MethodName_Scenario_ExpectedResult
- Use Arrange/Act/Assert with blank line separators
- Mock interfaces only, never concrete classes
- Use test builders from tests/Builders/ for complex objects

## Integration Tests
- Inherit from IntegrationTestBase (sets up WebApplicationFactory)
- Each test class gets its own database (see TestDatabaseFixture)
- Seed data in constructor, clean up in Dispose
- Test real HTTP calls through the pipeline
- Do NOT mock repositories in integration tests

## Example
```csharp
[Fact]
public async Task Handle_ValidOrder_ReturnsCreatedResult()
{
    // Arrange
    var command = new CreateOrderCommand("SKU-001", 2);

    // Act
    var result = await _handler.Handle(command, CancellationToken.None);

    // Assert
    result.IsSuccess.Should().BeTrue();
    result.Value.Sku.Should().Be("SKU-001");
    await _repository.Received(1).AddAsync(Arg.Any<Order>());
}
```
```

### Migration Rules

File: `.claude/rules/migrations.md`

```markdown
---
description: EF Core migration conventions
globs: src/Infrastructure/Data/Migrations/**/*.cs
---

# Migration Conventions

## CRITICAL: Never edit existing migrations
Existing migration files are immutable. If a migration has been applied
to any environment, it cannot be modified. Create a new migration instead.

## Creating Migrations
Always use the CLI:
```bash
dotnet ef migrations add <MigrationName> --project src/Infrastructure --startup-project src/Api
```

## Naming
- Use descriptive PascalCase: AddOrderStatusColumn, CreatePaymentsTable
- Prefix breaking changes: Breaking_RemoveObsoleteColumns
- Never use generic names like "Update1" or "Changes"

## Rules
- Always include a Down() method that cleanly reverses the migration
- Add indexes for any foreign key columns
- Add indexes for columns used in WHERE clauses
- Use string max lengths explicitly (no unbounded nvarchar(max))
- Include data migrations in separate migration files from schema changes
- Add comments explaining WHY for non-obvious schema decisions
```

### Domain Entity Rules

File: `.claude/rules/domain.md`

```markdown
---
description: Domain layer conventions
globs: src/Domain/**/*.cs
---

# Domain Conventions

## Entities
- Entities have private setters; modify state through methods
- Use factory methods (static Create()) instead of public constructors
- Raise domain events for significant state changes
- No infrastructure references (no EF Core attributes, no JSON attributes)
- Validation in factory methods and state-changing methods

## Value Objects
- Implement as records
- Include validation in constructor
- Override ToString() for logging

## Example
```csharp
public class Order : Entity
{
    public Guid CustomerId { get; private set; }
    public OrderStatus Status { get; private set; }
    public Money Total { get; private set; }

    private Order() { } // EF Core

    public static Result<Order> Create(Guid customerId, Money total)
    {
        if (total.Amount <= 0)
            return Result.Failure<Order>("Order total must be positive");

        var order = new Order
        {
            Id = Guid.NewGuid(),
            CustomerId = customerId,
            Status = OrderStatus.Pending,
            Total = total
        };

        order.AddDomainEvent(new OrderCreatedEvent(order.Id));
        return Result.Success(order);
    }
}
```
```


### Frontend Rules (if applicable)

File: `.claude/rules/frontend.md`

```markdown
---
description: Frontend component conventions
globs: src/Web/Components/**/*.razor, src/Web/Pages/**/*.razor
---

# Blazor Component Conventions

## Structure
- One component per file
- Component parameters at the top, then inject directives, then fields
- Event handlers as private methods at the bottom
- Extract components when they exceed 100 lines

## Naming
- Pages end with "Page": OrderListPage.razor
- Reusable components are descriptive: OrderStatusBadge.razor
- Parameters use PascalCase with [Parameter] attribute

## Rules
- Use CascadingAuthenticationState, not manual auth checks
- Call StateHasChanged() only when necessary (not after every operation)
- Dispose event handlers and subscriptions in IDisposable
- Use @key for list rendering performance
- No inline styles; use CSS isolation (Component.razor.css)
```

## When to Add Path-Scoped Rules

This is where most developers get it wrong. The instinct is to sit down, think of every possible convention, and create rules for everything. Resist that instinct.

**Add rules reactively, not proactively.**

The workflow:

1. You give the agent a task in a specific area of the codebase
2. The agent produces code that doesn't follow your conventions
3. You correct it during review
4. You ask yourself: "Will this keep happening?"
5. If yes, create a path-scoped rule

This approach has three advantages:

**You only create rules you actually need.** Hypothetical rules for hypothetical problems waste your time and the model's context window.

**The rules reflect real pain points.** A rule born from an actual mistake is more valuable than one born from speculation. It addresses a specific, demonstrated failure mode.

**You don't over-constrain the agent.** Too many rules limit the agent's ability to make good decisions. Some things are better left to the model's judgment. Only constrain the things where the model's default judgment consistently fails for your project.

### The Trigger Threshold

Not every agent mistake warrants a rule. Here's the filter:

**Create a rule when:**
- The agent makes the same mistake twice in the same area
- The convention is non-obvious (the agent can't infer it from existing code)
- The convention contradicts common patterns (your project does it differently than most)
- Getting it wrong has significant consequences (security, data integrity, architecture violations)

**Don't create a rule when:**
- The mistake was a one-off caused by a vague prompt
- The convention is obvious from existing code (agents learn from surrounding files)
- A quick prompt correction is sufficient ("use NSubstitute, not Moq")
- The "rule" is actually a code review preference, not a convention

## Anti-Patterns

Path-scoped rules are powerful. They're also easy to misuse.

### Too Many Rules

I've seen projects with 30+ rule files. At that point, you've recreated the "Novel" problem from Chapter 6, just distributed across more files. The agent is drowning in instructions.

**Guideline:** Start with 3-5 rule files for distinct areas of your codebase. Add more only when you have demonstrated need. If you're above 10, audit whether some rules should be consolidated or removed.

### Conflicting Rules

When rules overlap in scope, they can contradict each other. Your general `src/**` rules say "use constructor injection." Your controller rules say "use primary constructors." These aren't contradictory to a human, but an agent might struggle with the nuance.

**Fix:** When rules overlap, make the more specific rule self-contained. Don't assume the agent will correctly synthesize instructions from multiple rule files. If controller rules need to mention injection, include the full instruction rather than assuming the agent will reference the general rules.

### Overly Broad Rules

A rule file matching `**/*.cs` (every C# file in the project) is barely better than putting everything in AGENTS.md. The whole point of path-scoped rules is specificity.

**Fix:** Scope rules to the narrowest useful path. `src/Api/Controllers/**/*.cs` is better than `src/**/*.cs`. If a convention truly applies everywhere, it belongs in AGENTS.md, not in a path-scoped rule.

### Rules That Duplicate the Context File

If your AGENTS.md says "use xUnit and FluentAssertions" and your test rules also say "use xUnit and FluentAssertions," you've wasted context. Path-scoped rules should extend the main context file, not repeat it.

**Fix:** AGENTS.md covers project-wide conventions. Path-scoped rules cover area-specific conventions that don't apply globally. There should be minimal overlap.

### Stale Rules

A rule that references patterns, classes, or conventions that no longer exist actively misleads the agent. This is worse than having no rule at all.

**Fix:** When you refactor an area of the codebase, update (or delete) the corresponding rules. Include rule files in your code review process: when a PR changes conventions in an area, the reviewer should check whether the rules still match.

## Managing Rules as a Team

Path-scoped rules are code. Treat them that way.

**Commit them to the repo.** Rules in `.claude/rules/` or `.cursor/rules/` should be version-controlled. They're part of your project's development infrastructure, just like your CI configuration or linting rules.

**Review them in PRs.** When someone adds or changes a rule, the team should review it. A bad rule affects everyone's agent interactions.

**Document the intent.** The `description` field in the frontmatter isn't just metadata. It helps team members understand why the rule exists without reading the entire file.

**Delete aggressively.** If a rule hasn't been useful in a month, delete it. You can always recreate it. Stale rules cost more than missing rules.

## A Complete Example: Rule Set Evolution

Here's how a typical project's rules evolve over the first month of agentic development.

**Week 1:** You create AGENTS.md. No path-scoped rules yet. The agent writes decent code but keeps using AutoMapper in new controllers (you don't use it) and keeps writing synchronous test setup code.

**Week 2:** You add two rules: `controllers.md` (with the "no AutoMapper, use manual mapping" instruction) and `tests.md` (with async patterns and your test base classes). Agent output improves noticeably in these areas.

**Week 3:** You notice agents generate EF Core migrations with missing indexes and no Down() methods. You add `migrations.md`. A teammate notices agents put validation logic in entities instead of using the Result pattern, so they add `domain.md`.

**Week 4:** The team reviews all rules. One rule about "always use StringBuilder for string concatenation" turns out to be unnecessary (the agent already does this for performance-sensitive code). It gets deleted. Another rule about Blazor components gets refined based on two weeks of actual usage.

By week 4, you have 4-5 well-tested rules that meaningfully improve agent output. Each one exists because of a real, observed problem. None of them are speculative.


## Key Takeaways

1. **Path-scoped rules are surgical context.** They load the right instructions at the right time, keeping the agent focused on what matters for the specific file it's editing.

2. **Add rules reactively.** Wait for the agent to make a mistake twice, then create a rule to prevent it. Don't speculate about what rules you might need.

3. **Keep them focused and non-overlapping.** Each rule file should cover a distinct area of your codebase. Avoid duplication with AGENTS.md.

4. **Treat rules as code.** Version control them. Review them in PRs. Delete them when they're stale.

5. **Less is more.** Five well-targeted rules beat thirty broad ones. Every rule you add costs context window space. Make each one earn its place.

Path-scoped rules are the second layer of your context stack. They turn a good context file into a great one by adding precision where it matters most. But they're still passive: the agent reads them when it encounters matching files. The next chapter covers something more dynamic: skills, where you teach the agent entirely new workflows it can invoke on demand.
