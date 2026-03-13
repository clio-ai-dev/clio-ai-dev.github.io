# Chapter 17: Migration Generation

Nobody likes migrations. Framework upgrades, database schema changes, API versioning, language version bumps. They're tedious, error-prone, and the kind of work where a small mistake cascades into hours of debugging. They're also exactly the kind of work that agents handle well.

Migrations are pattern-heavy. Upgrade .NET 8 to .NET 10, and 90% of the changes are mechanical: update the target framework moniker, update NuGet packages, fix the handful of breaking API changes. The other 10% requires judgment. Agents crush the 90% and flag the 10% for your review.

This chapter covers the major categories of migration work and how to structure each for agentic development.

## Framework Version Upgrades

Let's start with the most common migration: upgrading your .NET version. We'll use .NET 8 to .NET 10 as the example, but the patterns apply to any framework upgrade.

### What Agents Handle Well

**Target framework updates.** Changing `<TargetFramework>net8.0</TargetFramework>` to `net10.0` across every project file. Mechanical, repetitive, zero judgment required.

**NuGet package updates.** Bumping `Microsoft.AspNetCore.*`, `Microsoft.EntityFrameworkCore.*`, and other first-party packages to their .NET 10 versions. The agent reads the current versions, checks compatibility, and updates them.

**Breaking API changes.** Each .NET release has a documented list of breaking changes. Agents are good at identifying which ones affect your code and applying the fixes. For example, if a method signature changed or an API was obsoleted, the agent finds every usage and updates it.

**Build error resolution.** After the initial upgrade, `dotnet build` produces errors. The agent reads each error, applies the fix, rebuilds, and iterates until the build succeeds. This is the TDD Agent Loop applied to compilation instead of tests.

### What Agents Handle Poorly

**Behavioral changes.** Some upgrades change how things work without changing the API. A serialization library might handle null values differently. A middleware might process requests in a different order. These don't produce build errors, and agents can't detect them without tests.


**Performance regressions.** The upgrade might introduce performance changes (positive or negative) that only show up under load. Agents can't benchmark for you.

**Configuration changes.** New versions sometimes change default configuration values or add required configuration. The agent might miss these if they're not documented in the breaking changes list.

### The Upgrade Workflow

Here's how I structure a framework upgrade with agents:


**Step 1: Preparation (you, 15 minutes)**

Read the official migration guide. Yes, actually read it. The agent will handle the mechanical work, but you need to know about the behavioral changes and new features that might affect your architecture.

Create a migration spec (Chapter 14's format works well):

```markdown
# Migration: .NET 8 → .NET 10

## Scope
- All 12 projects in the solution
- Target framework, NuGet packages, breaking API changes
- Do NOT adopt new features yet (separate PR)

## Known Breaking Changes Affecting Us
- JsonSerializerOptions.PropertyNameCaseInsensitive default changed
- IHostEnvironment.ContentRootPath behavior in test host
- Obsolete middleware removed (we use UseExceptionHandler override)

## Out of Scope
- Adopting new .NET 10 features (HybridCache, new minimal API features)
- Performance optimization
- Dependency injection changes
```

**Step 2: Mechanical upgrade (agent, 10-20 minutes)**

```
Upgrade this solution from .NET 8 to .NET 10.

1. Update TargetFramework in all .csproj files
2. Update all Microsoft.* NuGet packages to .NET 10 compatible versions
3. Fix any build errors from breaking API changes
4. Run dotnet build and iterate until it compiles cleanly
5. Run dotnet test and fix any test failures

Read the migration spec in docs/specs/net10-migration.md for known
breaking changes and scope boundaries.
```

The agent works through the solution project by project. It updates the framework, bumps packages, resolves build errors, and runs the tests. Most of this is mechanical. The agent handles it in a fraction of the time you would.

**Step 3: Review (you, 20-30 minutes)**

Review the changes. Focus on:
- Did the agent handle the known breaking changes correctly?
- Are there any changes that look suspicious (logic changes, not just API updates)?
- Do all tests pass? Are there any tests that pass but might be testing the wrong thing now?

**Step 4: Manual verification (you)**

Test the behavioral changes from your spec manually or with targeted integration tests. The agent can help you write those tests:

```
The .NET 10 migration changed JsonSerializerOptions defaults.
Write integration tests that verify our API responses still
serialize property names the same way as before the upgrade.
```

## Database Schema Evolution

EF Core migrations with agents are one of the smoothest agentic workflows. The combination of a declarative model (your entity classes), a diff engine (EF Core's migration scaffolder), and a test framework (integration tests against a real database) creates a tight feedback loop.

### Adding a New Entity

```
Add a DiscountCode entity to the domain model with these properties:
- Id (Guid, primary key)
- Code (string, max 50, unique index)
- Type (enum: Percentage, FixedAmount)
- Value (decimal)
- MinimumOrderAmount (decimal, nullable)
- MaxUsageCount (int, nullable)
- CurrentUsageCount (int, default 0)
- ExpiresAt (DateTimeOffset, nullable)
- CreatedAt (DateTimeOffset)

Create the entity in src/Domain/Discounts/.
Add EF Core configuration in src/Infrastructure/EntityConfigurations/.
Generate a migration.
Follow existing patterns (see OrderConfiguration.cs for reference).
```

The agent creates the entity, writes the configuration (column types, indexes, constraints), and runs `dotnet ef migrations add AddDiscountCode`. The generated migration is deterministic based on the model, so reviewing it is straightforward: check that the SQL matches your intent.

### Modifying Existing Entities

Schema changes to existing entities are trickier because they involve data migration. Agents handle the schema part well but need explicit guidance for data:

```
Add a "Tier" property to the Customer entity:
- Enum: Standard, Silver, Gold, Platinum
- Default: Standard
- All existing customers should be Standard

Generate the migration. The migration should:
1. Add the column with a default value of 0 (Standard)
2. NOT use a data migration script (the default handles existing rows)
```

Without that explicit guidance, agents sometimes generate data migration scripts that are unnecessary or, worse, incorrect. Be specific about data handling.

### Complex Migrations

For migrations that involve data transformation (splitting a table, merging columns, changing a relationship), write the migration spec carefully:

```markdown
# Migration: Split Address from Customer

## Current State
Customer table has address columns inline:
Street, City, State, ZipCode, Country

## Target State
Separate Address table with one-to-many relationship to Customer
(customers can have multiple addresses, one marked as default)

## Data Migration
1. Create Address table
2. For each Customer, create an Address record from their inline columns
3. Mark the created Address as the default
4. Remove inline address columns from Customer table

## Safety
- Migration must be reversible (down migration restores inline columns)
- Run in a transaction
- Test with production-like data volume (500K customers)
```

Hand this to the agent:

```
Generate an EF Core migration based on the spec in
docs/specs/split-address-migration.md.

Create the new Address entity and configuration first,
then generate the migration. Include the data migration
in the Up method using raw SQL for performance.
```

The agent generates the migration with the data transformation. Review the SQL carefully. Run it against a copy of production data before deploying.

## API Versioning and Contract Migration

API versioning is one of those tasks that's conceptually simple but mechanically tedious. You're duplicating endpoints, adjusting request/response models, maintaining backward compatibility, and updating documentation. Agents handle the mechanical parts well.

### Adding a New API Version

```
Create v2 of the Orders API endpoints.

Changes from v1:
- CreateOrder request adds an optional "discountCode" field
- OrderResponse includes "discountAmount" and "finalTotal" fields
- GET /orders supports filtering by status (query parameter)

Requirements:
- v1 endpoints continue to work unchanged
- v2 endpoints live in a new OrdersV2 folder
- Shared logic stays in the Application layer (handlers are version-aware)
- Both versions share the same domain model

Follow the existing versioning pattern in the Users API (v1 and v2 exist).
```

The agent creates the v2 endpoint definitions, the new request/response models, adapts the handlers, and wires everything up. The key here is pointing the agent to an existing versioning pattern. Without that reference, agents make inconsistent choices about how to structure versioned endpoints.

### Contract Migration

When you need to migrate consumers from v1 to v2, agents help generate the migration guide:

```
Generate a migration guide for consumers of our Orders API,
covering the upgrade from v1 to v2.

For each changed endpoint, show:
- The v1 request/response
- The v2 request/response
- What changed and why
- Code examples for updating client code (C# HttpClient)

Also generate a deprecation timeline recommendation.
```

This produces documentation that your API consumers actually need, generated directly from the code differences between v1 and v2.

## Large-Scale Refactoring

Large refactors are where agents provide the most dramatic time savings, and where they're most dangerous if uncontrolled. The key is breaking the refactor into safe, reviewable steps.

### The Safe Refactoring Pattern

**Step 1: Write characterization tests.**


Before changing anything, capture the current behavior:

```
Write integration tests that capture the current behavior of
the OrderService. Test every public method with representative
inputs and outputs. These tests should pass against the current
implementation. They're our safety net for the refactoring.
```

**Step 2: Break the refactor into atomic steps.**

Each step should be independently committable and deployable:

```markdown
# Refactoring Plan: Extract Payment Processing

## Step 1: Extract interface
Create IPaymentProcessor interface from existing PaymentService methods.
No behavior change. All existing code continues to work.

## Step 2: Implement adapter
Create StripePaymentProcessor implementing IPaymentProcessor.
Move Stripe-specific logic from PaymentService. PaymentService
delegates to the adapter. No behavior change.

## Step 3: Wire up DI
Register IPaymentProcessor -> StripePaymentProcessor.
Update consumers to depend on IPaymentProcessor instead of
PaymentService. No behavior change.

## Step 4: Remove PaymentService
Once all consumers use IPaymentProcessor, remove the old
PaymentService class. Characterization tests still pass.
```

**Step 3: Agent implements each step.**

Give the agent one step at a time. After each step, run the characterization tests. If they pass, commit. If they fail, the agent broke something; fix it before moving on.

This approach works because each step is small enough to review, safe enough to commit, and testable. The agent can work quickly because the scope is constrained. And you can stop after any step if something goes wrong, because each step is independently valid.

## The Migration Safety Net


Every migration, regardless of type, needs a safety net. The safety net has three layers:

### Layer 1: Tests

Tests are your first line of defense. Before any migration, ensure your test suite covers the areas you're changing. If coverage is thin, write characterization tests first (let the agent help, it's fast at generating tests from existing code).

After the migration, all existing tests must pass. New tests cover any new behavior or changed contracts.

### Layer 2: Staged Rollout

Don't deploy migrations to all users at once. Use feature flags, canary deployments, or blue-green deployments to limit blast radius:

- **Feature flags** for API changes (new version behind a flag)
- **Canary deployments** for framework upgrades (10% of traffic first)
- **Blue-green** for database migrations (new schema active, old schema on standby)

Agents can help set up the staged rollout:

```
Add a feature flag for the v2 Orders API using our existing
feature flag system (Microsoft.FeatureManagement).
When the flag is disabled, v2 endpoints return 404.
When enabled, they work normally.
```

### Layer 3: Rollback Plan

Every migration needs a rollback plan before it starts. For framework upgrades, that's usually "revert the commit." For database migrations, it's the `Down` method in the EF Core migration. For API versions, it's disabling the feature flag.

Document the rollback plan in the migration spec. Make the agent include it:

```
Add a "Rollback Plan" section to the migration spec.
Include specific commands to reverse each step.
```

## Legacy Modernization Patterns

The biggest migration challenge most teams face isn't upgrading from .NET 8 to 10. It's modernizing legacy systems: .NET Framework 4.x to modern .NET, monoliths to services, old patterns to new ones.

Agents are surprisingly effective here because legacy modernization is largely pattern translation: take this old pattern, produce the equivalent in the new framework. The logic stays the same; the infrastructure changes.

### The Strangler Fig Approach

Instead of rewriting everything at once, wrap the legacy system with a modern API and migrate feature by feature:

```
Analyze the legacy OrderController (ASP.NET MVC 5) and create
an equivalent minimal API endpoint in the new .NET 10 project.

The new endpoint should:
- Accept the same request format (for backward compatibility)
- Call the same business logic (through an anti-corruption layer)
- Return the same response format
- Add the new response fields our mobile app needs

Reference the legacy controller at legacy/Controllers/OrderController.cs
and the new project structure at src/Api/.
```

The agent reads the legacy code, understands the behavior, and produces a modern equivalent. Your job is reviewing the translation for correctness, especially around edge cases the legacy code handles implicitly (null checks that aren't obvious, error handling buried in base classes, configuration that affects behavior).

### Batch Migration of Patterns

For large codebases, some migrations involve changing hundreds of files in the same way. Converting from `ILogger` property injection to constructor injection. Replacing `async void` event handlers with `async Task`. Updating from old EF Core query syntax to the new patterns.

Agents handle batch migrations well when you give them a clear before/after pattern:

```
Find all classes in src/ that inject ILogger via a property
(pattern: "public ILogger<T> Logger { get; set; }").

Convert each one to constructor injection:
- Add ILogger<T> parameter to the constructor
- Assign to a private readonly field
- Remove the property
- Update all usages of Logger to _logger

Do one project at a time. Run tests after each project.
```

The agent processes each file, applies the transformation, and verifies with tests. What would take you a day of tedious find-and-replace takes the agent 20 minutes.

## The Migration Mindset

Migrations are where agents provide some of the clearest ROI in agentic development. The work is mechanical, pattern-heavy, and well-defined. The risks are manageable with tests and staged rollouts. And the time savings are substantial: a framework upgrade that takes a team two weeks by hand takes a few days with agents.

The key principles:

1. **Spec the migration before starting.** Know the scope, the breaking changes, and the rollback plan.
2. **Break it into atomic steps.** Each step is reviewable, testable, and committable.
3. **Tests are non-negotiable.** They're your proof that the migration preserved behavior.
4. **Stage the rollout.** Limit blast radius. Verify in production gradually.
5. **Let agents handle the mechanical work.** Save your judgment for the decisions that matter.

Migrations aren't exciting. But they're necessary, and with agents, they're fast. That's a win.
