# Chapter 14: Spec-First Development

The previous chapter showed you the TDD Agent Loop: write tests, let the agent implement, review with confidence. That workflow is powerful for well-defined features where you can express the behavior in code. But what about the 30 minutes before you write those tests? What about the architectural decisions, the trade-offs, the "how should this thing even work?" questions?

That's where spec-first development comes in. You write the design document before you write any code or tests. You think through the problem, make the hard decisions, then hand the spec to an agent and say "build this."

Simon Willison nailed the insight: "Code that started from your own specification is a lot less effort to review." He's right, and the reason is simple. When you wrote the spec, you already made the decisions. The agent is executing your decisions, not making its own. Reviewing execution is fast. Reviewing decisions is slow.

## Why Specs Matter More Now

Before agents, writing a detailed spec felt like overhead. You'd write the spec, then write the code yourself, and the spec would rot in a Confluence page that nobody ever looked at again. The spec was documentation of intent, disconnected from the implementation.

With agents, the spec IS the implementation instruction. The spec doesn't rot because it gets consumed immediately. You write it, the agent reads it, code comes out. The spec is the prompt, just a structured, thorough one.

This changes the economics of specification. Writing a detailed spec used to double your work (spec + implementation). Now it replaces your work (spec instead of implementation). The time you invest in the spec is the time you save on implementation, review, and debugging.

Addy Osmani put it well: "The better your specs, the better the AI's output." This isn't motivational fluff. It's a mechanical truth. Agents are completion machines. Give them a vague spec, they'll complete it with assumptions. Give them a precise spec, they'll complete it with precision.

## The Spec Format


A good spec for agentic development isn't the same as a traditional design document. It's shorter, more structured, and optimized for consumption by both humans and agents. Here's the format I use:

```markdown
# Feature: Discount Code System

## Overview
Allow customers to apply discount codes at checkout. Codes can be
percentage-based or fixed-amount, with optional constraints on minimum
order value, usage limits, and expiration dates.

## Requirements
1. Customers can apply a single discount code per order
2. Codes are case-insensitive ("SAVE20" == "save20")
3. Percentage discounts apply to the subtotal before tax
4. Fixed-amount discounts reduce the subtotal (minimum $0, no negative totals)
5. Expired codes return a clear error message with the expiration date
6. Codes at their usage limit return a clear error message
7. Orders below the minimum threshold return a clear error with the minimum

## Constraints
- Discount codes are stored in the existing PostgreSQL database
- Use EF Core for data access (follow existing repository patterns)
- API follows our REST conventions: POST /api/v1/orders/{id}/discount
- Response codes: 200 (applied), 400 (invalid code), 422 (business rule violation)
- No discount stacking in v1 (explicitly reject if discount already applied)

## Architecture Notes
- New DiscountCode entity in the Domain layer
- DiscountService in Domain (pure business logic, no I/O)
- IDiscountCodeRepository interface in Domain, implementation in Infrastructure
- ApplyDiscountHandler in Application layer (orchestrates service + repo)
- Endpoint in API layer using minimal APIs

## Test Scenarios
- Apply valid percentage code: 20% off $100 = $80
- Apply valid fixed code: $15 off $100 = $85
- Apply expired code: returns 422 with expiration date
- Apply code at usage limit: returns 422 with limit info
- Apply code below minimum order: returns 422 with minimum amount
- Apply code to order with existing discount: returns 422
- Case-insensitive lookup: "save20" finds "SAVE20"
- Fixed discount exceeding subtotal: caps at $0, not negative
- Apply invalid/nonexistent code: returns 400

## Out of Scope
- Discount stacking (v2)
- Automatic discount application (v2)
- Discount analytics/reporting (v2)
```

Notice what this spec includes and what it doesn't.

**It includes decisions.** The spec says "single discount code per order." That's a product decision you made. The spec says "POST /api/v1/orders/{id}/discount" with specific response codes. That's an API design decision you made. The agent doesn't have to guess any of this.

**It includes the architecture.** The spec tells the agent exactly where things go: Domain layer, Application layer, Infrastructure layer. This eliminates the most common source of agent-generated code that "works but doesn't fit."

**It includes test scenarios.** These aren't code yet, but they're specific enough that you (or the agent) can turn them into tests quickly. Each scenario has concrete numbers, not "apply a valid code" but "20% off $100 = $80."

**It excludes implementation details.** The spec doesn't say how to validate expiration dates or how to check usage limits. Those are implementation decisions the agent can make. You're constraining the what and where, not the how.

**It explicitly calls out scope boundaries.** The "Out of Scope" section prevents the agent from gold-plating. Without it, agents love to add features you didn't ask for, especially stacking logic that makes the code 3x more complex.

## Breaking Specs into Agent-Sized Chunks


A spec like the one above is too big for a single agent pass. Not because the agent can't handle it technically, but because the output would be too large to review effectively. Remember: you're trading implementation time for review time. If the review takes an hour because the agent generated 15 files, you've lost the advantage.

Break the spec into chunks that each produce a reviewable unit of work:

**Chunk 1: Domain model and service**
```
Implement the DiscountCode entity and DiscountService based on the spec.
Create the types in src/Domain/Discounts/.
Write unit tests in tests/Domain.Tests/Discounts/.
Follow the test scenarios from the spec.
Run tests to verify.
```

**Chunk 2: Repository and persistence**
```
Implement IDiscountCodeRepository and its EF Core implementation.
Add the DiscountCode entity configuration.
Add a migration for the new table.
Create types in src/Infrastructure/Discounts/.
Follow existing repository patterns (see src/Infrastructure/Orders/).
```

**Chunk 3: Application handler**
```
Implement ApplyDiscountHandler in src/Application/Discounts/.
Wire up the DiscountService and IDiscountCodeRepository.
Write integration tests in tests/Application.Tests/Discounts/.
Follow existing handler patterns (see src/Application/Orders/).
```

**Chunk 4: API endpoint**
```
Add the POST /api/v1/orders/{id}/discount endpoint.
Follow minimal API conventions from the spec.
Write integration tests using WebApplicationFactory.
Test all response codes: 200, 400, 422.
Register the handler and service in DI.
```

Each chunk produces 2-5 files. Each chunk is reviewable in 5-10 minutes. Each chunk builds on the previous one. And each chunk can use the TDD Agent Loop from the previous chapter: write the tests (or let the agent write them from the spec's test scenarios), then implement.

## The Spec, Agent, Review, Iterate Cycle


Here's the full workflow in practice:

**Phase 1: Spec (you, 20-40 minutes)**

Write the spec document. This is your thinking time. You're making architectural decisions, defining constraints, listing test scenarios. This is the highest-value work you do as a developer.

Save the spec as a markdown file in your repo. I keep them in `docs/specs/` alongside the code. Some teams use `docs/adr/` for architectural decisions. The location doesn't matter. What matters is that it's in the repo, versioned, and accessible to agents.

**Phase 2: Chunk and delegate (you, 5 minutes)**

Break the spec into agent-sized chunks as described above. You can do this in your head or write it out. For complex features, I write the chunks as a checklist in the spec itself.

**Phase 3: Agent implementation (agent, 5-15 minutes per chunk)**

Hand each chunk to the agent with the spec as context:

```
Read the spec in docs/specs/discount-codes.md.

Implement Chunk 1: Domain model and service.
Create DiscountCode entity and DiscountService in src/Domain/Discounts/.
Write tests based on the test scenarios in the spec.
Run tests to verify.
```

The agent reads the spec, understands the full picture, and implements the chunk within that context. This is critical: the agent sees the whole spec even when implementing a piece. It knows what's coming next, so it makes design choices that support the full feature.

**Phase 4: Review (you, 5-10 minutes per chunk)**

Review the output. With a good spec, your review focuses on:
- Does the code match the spec's decisions?
- Is the code clean and idiomatic?
- Did the agent make reasonable implementation choices?
- Are the tests comprehensive?

If something's wrong, either fix it directly (if it's small) or prompt the agent with corrections. This is iteration, not failure. Two passes is normal. Three is fine. Ten means your spec was unclear.

**Phase 5: Commit and continue**

Commit the chunk. Move to the next one. Each chunk builds on committed, reviewed, working code.

## ADR Generation

Architecture Decision Records (ADRs) are a natural byproduct of spec-first development. You're already making architectural decisions in the spec. Capturing them as ADRs is a small extra step with outsized long-term value.


An ADR records why you made a decision, not just what you decided. Six months from now, when someone asks "why did we use a separate DiscountService instead of putting the logic in the handler?", the ADR answers that question.

Here's the thing: agents are excellent at generating ADRs from specs. After you've implemented a feature, prompt the agent:

```
Based on the spec in docs/specs/discount-codes.md and the
implementation in src/Domain/Discounts/ and src/Application/Discounts/,
generate an ADR for the key architectural decisions.

Use the format in docs/adr/template.md.
Focus on decisions that future developers would question.
```

The agent produces something like:

```markdown
# ADR-017: Discount Code Architecture

## Status
Accepted

## Context
We need to support discount codes at checkout. The system must handle
percentage and fixed-amount discounts with expiration, usage limits,
and minimum order constraints.

## Decision
- Pure domain service (DiscountService) for business logic, no I/O
- Separate repository for discount code persistence
- Application handler orchestrates service and repository
- Single discount per order (no stacking in v1)
- Case-insensitive code lookup at the repository level

## Consequences
- Business logic is testable without infrastructure dependencies
- Adding discount stacking in v2 requires changes to DiscountService
  and the handler, but not the repository or API contract
- Case-insensitive lookup in the repository means the database
  handles collation, not the application code
```

You review and commit this alongside the code. Future you (and future team members) will thank present you.

The combination of spec + ADR creates a documentation trail that's actually useful. The spec says what you planned. The ADR says what you decided and why. The code says what you built. The tests say what it does. That's complete traceability from intent to implementation.

## A Real Example: Building a Complete API Feature

Let me walk through a full spec-first workflow for a realistic feature. We're adding a notification preferences system to an existing .NET API.

### The Spec (25 minutes)

```markdown
# Feature: Notification Preferences

## Overview
Users can configure how they receive notifications: email, SMS, push,
or in-app. Each notification type (order updates, promotions,
security alerts) can be independently toggled per channel.

## Requirements
1. Users have a preferences record created on account registration
2. Default: all channels enabled for security alerts,
   email-only for everything else
3. Users can update preferences via PATCH endpoint
4. Security alerts cannot be fully disabled (at least one channel required)
5. SMS requires a verified phone number (return 422 if unverified)
6. Preference changes are eventually consistent (async event published)

## Constraints
- PATCH /api/v1/users/{id}/notification-preferences
- Request body: partial update (only changed fields)
- EF Core with existing User entity relationship
- Publish NotificationPreferencesChanged event via MediatR
- No new external dependencies

## Architecture Notes
- NotificationPreferences entity in Domain, owned by User
- NotificationPreferencesService in Domain (validation logic)
- UpdateNotificationPreferencesHandler in Application
- Minimal API endpoint in API layer

## Test Scenarios
- Get default preferences for new user: security=all, others=email-only
- Update email preference for promotions: toggles correctly
- Disable all channels for security alerts: returns 422
- Enable SMS without verified phone: returns 422
- Partial update: only specified fields change, others unchanged
- Publish event on successful update: event contains user ID and changes
- Update nonexistent user: returns 404
```

### Chunk 1: Domain Model (10 minutes with agent)

I write the unit tests for the domain service based on the test scenarios, then hand them to the agent:

```
Make all tests in NotificationPreferencesServiceTests pass.
Create types in src/Domain/Notifications/.
The NotificationPreferences entity should be an owned entity of User.
Run tests to verify.
```

Agent produces: `NotificationChannel` enum (flags), `NotificationType` enum, `NotificationPreferences` entity, `NotificationPreferencesService` with validation logic. All tests pass. Review takes 5 minutes. Clean code, good use of flags enum for channel combinations.

### Chunk 2: Persistence (8 minutes with agent)

```
Add EF Core configuration for NotificationPreferences as an owned
entity of User. Add a migration. Follow the existing owned entity
pattern in src/Infrastructure/EntityConfigurations/UserConfiguration.cs.
```

Agent adds the configuration, generates the migration. Review takes 3 minutes (mostly checking the migration SQL).

### Chunk 3: Handler and Event (12 minutes with agent)

I write integration tests for the handler, including verification that the MediatR event is published. Agent implements the handler. First pass misses the partial update logic (overwrites all fields instead of merging). Test catches it, agent fixes it on second iteration.

### Chunk 4: API Endpoint (8 minutes with agent)

Agent builds the PATCH endpoint, maps the request to the handler, returns appropriate status codes. Integration tests via `WebApplicationFactory` cover all response codes.

**Total time: 25 minutes speccing + 38 minutes implementation + ~20 minutes review = ~83 minutes** for a complete feature with full test coverage, clean architecture, ADR, and documentation.

The spec drove the whole thing. Every decision in the code traces back to a line in the spec. Every test scenario maps to a requirement. The agent didn't guess, didn't improvise, didn't gold-plate. It built exactly what the spec described.

## When Spec-First Doesn't Fit

Not every task deserves a full spec. Bug fixes, small refactors, and quick scripts don't need a design document. The TDD Agent Loop from Chapter 13 handles those beautifully.

Spec-first shines for:
- New features with multiple components
- Anything touching the API contract
- Features that span multiple layers of the architecture
- Work that multiple developers (or agents) will touch
- Anything you'll need to explain to someone else later

Use your judgment. A five-line spec is still a spec. A mental model you hold in your head while writing tests is, loosely, a spec. The format matters less than the act of thinking through the problem before writing code.

The real insight is this: in an agentic workflow, the spec is your highest-leverage artifact. It's the one thing that scales your judgment across every agent interaction. Write it once, use it across every chunk, reference it in every review. The 25 minutes you spend writing a spec saves hours of debugging agent output that went in the wrong direction.

Write the spec. Break it into chunks. Let agents build it. Review with the spec as your guide. That's spec-first development.
