# Chapter 28: When NOT to Use Agents

*Part VII: The Discipline*

Every chapter in this book has been about when and how to use agents effectively. This chapter is about when to turn them off.

This is the chapter most agentic development advocates won't write. The toolmakers won't write it because it's bad for business. The enthusiasts won't write it because it contradicts the narrative. But if you're going to be genuinely productive with agents, you need to know when they're the wrong tool. Using agents everywhere, on everything, all the time, will make you slower. Not theoretically slower. Measurably slower.

The METR study proved it. Experienced developers on familiar codebases were 19% slower with AI tools. And they *believed* they were 20% faster. That gap between perception and reality is the danger zone. This chapter is your map out of it.


## Security-Critical Code Paths

Chapter 27 covered how agents can help with security review. Here's the flip side: agents should not be the primary author of security-critical code.

Authentication flows, cryptographic implementations, authorization logic, token handling, certificate validation, key management. These are areas where subtle bugs have catastrophic consequences and where agents make subtle bugs.

An agent will happily generate a JWT validation routine that looks correct, passes your tests, and has a timing vulnerability that leaks token validity information to attackers. It'll write a password hashing function that uses bcrypt (good) with a work factor of 4 (dangerously low). It'll implement OAuth correctly for 95% of cases and miss the state parameter validation that prevents CSRF attacks.

The problem isn't that agents write *bad* security code. They write *almost correct* security code. And in security, almost correct is worse than obviously broken, because you'll ship it.

**The rule:** Use agents to review security code. Use agents to write tests for security code. Write the security code yourself, or use battle-tested libraries (which is what you should do anyway).

## Performance-Sensitive Hot Paths

Agents optimize for correctness and readability. Those are usually the right priorities. But in hot paths (code that executes thousands or millions of times per second) performance dominates, and agents consistently make the wrong tradeoffs.

Consider a serialization hot path in a high-throughput API:

```csharp
// What the agent writes (correct, readable, slow)
public string Serialize(Order order)
{
    return JsonSerializer.Serialize(order);
}

// What you need (correct, less readable, 10x faster)
public void Serialize(Order order, IBufferWriter<byte> buffer)
{
    using var writer = new Utf8JsonWriter(buffer, new JsonWriterOptions { SkipValidation = true });
    writer.WriteStartObject();
    writer.WriteString("id"u8, order.Id);
    writer.WriteNumber("total"u8, order.Total);
    // ... manual serialization for each field
    writer.WriteEndObject();
}
```

Agents don't know your performance requirements. They don't know that this method is called 50,000 times per second. They'll use LINQ where a for loop saves allocations. They'll create new objects where pooling is essential. They'll use string concatenation where `StringBuilder` or `Span<T>` is required.

You *can* prompt agents for performance-optimized code. But you'll spend more time specifying the constraints, reviewing the output, and benchmarking the result than you'd spend writing it yourself. The "faster by hand" test (more on this below) almost always triggers for hot path code.

**The rule:** Identify your hot paths with profiling first. Write those paths by hand. Use agents for everything else. That's probably 95-99% of your codebase.

## Deep Domain Logic

Every codebase has logic that requires business context no agent possesses. Insurance rate calculation tables. Regulatory compliance rules. Medical dosage algorithms. Financial instrument pricing models. Tax calculation edge cases for specific jurisdictions.

These are areas where:

1. The requirements are complex, nuanced, and often contradictory
2. The source of truth is a human expert, a legal document, or a spreadsheet, not code
3. Getting it wrong has real-world consequences (financial, legal, medical)
4. The logic changes based on context that isn't in the codebase

An agent can implement a tax calculation if you give it a complete, unambiguous specification. But creating that specification is the hard part. And if the specification is complete enough for an agent to implement correctly, it's complete enough that the implementation is trivial. You're not saving time; you're adding a translation layer between your spec and the code.

**The rule:** When the domain expert needs to be in the room while you code, the agent doesn't help. Write it yourself, with the expert, and add comprehensive tests. Then use agents to maintain and refactor it later, when the tests protect the business rules.

## The METR Paradox Revisited

The METR study deserves deeper examination here because it reveals something important about when agents fail.

The study measured experienced open-source developers working on codebases they maintained. These developers knew every file, every pattern, every quirk. When they used AI tools:

- Tasks took 19% longer on average
- Developers believed they were 20% faster
- The perception gap was roughly 40 percentage points

Why? Several factors:

**Context switching cost.** Prompting the agent, waiting for output, reviewing the output, correcting the output. For code you could write in 30 seconds from muscle memory, this overhead adds 2-3 minutes. Multiply by dozens of small changes per day.

**Review burden on familiar code.** When you know the codebase intimately, you can write correct code on the first try. But you still have to review agent output line by line, because the agent doesn't know the codebase intimately. The review takes longer than writing.

**The illusion of delegation.** "I'll let the agent handle this" feels productive. You're delegating! But if the delegation cost (prompting + reviewing + correcting) exceeds the implementation cost, you've paid more for less.

**Overcorrection loops.** The agent produces something 90% right. You correct the 10%. The agent "fixes" it but breaks something in the original 90%. You correct again. Two iterations later, you've spent triple the time.

The METR finding doesn't mean agents are useless. It means agents are useless *when you already know what to type.* The value of agents scales inversely with your familiarity with the code:

- **Unfamiliar codebase:** Agents save massive time (exploration, understanding, boilerplate)
- **Somewhat familiar:** Agents save moderate time (complex features, cross-cutting concerns)
- **Deeply familiar:** Agents often cost time (simple changes, routine maintenance)

The discipline is recognizing which category you're in for each task.

## Tasks Where Agents Consistently Struggle

Beyond the categories above, here are specific task types where agents reliably underperform:


**Large-scale refactoring across many files.** Agents handle single-file refactoring well. But when you need to rename a concept across 50 files, update all the tests, fix all the DI registrations, and adjust the database migrations, agents lose coherence. They'll miss files, introduce inconsistencies, and create merge conflicts with themselves. Your IDE's refactoring tools (Rename Symbol, Find All References) are faster and more reliable.

**UI polish and visual design.** Agents can build functional UI. They cannot make it look good. They'll produce a form that works, with the wrong spacing, inconsistent margins, and colors that clash. Visual quality requires human eyes.

**Debugging production issues from logs.** Agents can help parse logs and suggest hypotheses. But production debugging requires understanding the system's runtime behavior, infrastructure quirks, and deployment history. "The service crashed at 3 AM" requires context about traffic patterns, recent deployments, and infrastructure changes that agents don't have.

**Writing meaningful commit messages and documentation.** Agents write technically accurate but soulless documentation. They'll describe what the code does without explaining why it exists or how it fits the larger picture. Documentation that actually helps future developers requires human judgment about what matters.

**Complex database query optimization.** Agents can write queries. They can't evaluate whether a query will perform well against your specific data distribution, indexes, and access patterns. They'll suggest indexes without knowing your write-to-read ratio. They'll recommend denormalization without understanding your consistency requirements.

## The "Faster by Hand" Test

Before starting any agent task, ask yourself: "Would I finish this faster by just writing it myself?"

Be honest. Factor in:

- **Prompting time.** How long to write the prompt with enough context?
- **Waiting time.** Agent response time (seconds to minutes depending on the tool and task complexity).
- **Review time.** How long to verify the output is correct?
- **Correction time.** How many iterations before it's right?
- **Your typing speed.** For simple code you've written before, your fingers are fast.

If the total agent time (prompt + wait + review + correct) exceeds your direct implementation time by more than 20%, skip the agent. The 20% buffer accounts for the cognitive benefit of reviewing code versus writing it, but beyond that buffer, you're wasting time.

Tasks that almost always pass the "faster by hand" test:

- Simple bug fixes where you already know the root cause
- Adding a field to a model, DTO, and mapping
- Writing a one-line configuration change
- Fixing a typo or renaming a variable
- Adding a log statement
- Updating a version number

Tasks that almost always fail it (use the agent):

- Implementing a new feature with multiple files
- Writing a comprehensive test suite
- Building boilerplate (controllers, DTOs, mappers, DI registration)
- Exploring an unfamiliar part of the codebase
- Migrating code from one pattern to another
- Generating documentation from code

The middle ground is where judgment matters. And that judgment improves with practice.

## Recognizing Diminishing Returns

Agent-assisted development follows a curve of diminishing returns within a single task. The first 80% of the implementation comes fast. The next 15% takes as long as the first 80%. The final 5% takes longer than everything else combined.


This happens because:

- The easy parts (boilerplate, standard patterns, happy path) are what agents do best
- The hard parts (edge cases, integration points, business-specific logic) are what agents do worst
- Each correction cycle takes longer as the code gets more complex and intertwined

Recognize the inflection point. When you're on your third correction cycle and the agent keeps oscillating between two broken states, stop. Take over. Write the remaining code yourself. You've extracted the value the agent can provide.

A practical signal: if you've prompted the agent three times for the same issue and it's still not right, you'll finish faster by hand. This isn't a hard rule, but it's a reliable heuristic.

## The Discipline of Turning Off the Tool

The hardest part of agent-assisted development isn't learning when to use agents. It's learning when to stop.

There's a psychological pull toward using agents for everything. You've invested in learning the tools. You've set up context files. You've built workflows. The sunk cost makes you want to use agents even when they're not helping. Add the perception gap from the METR study (feeling faster while being slower) and you have a recipe for persistent misuse.

Build the habit of checking in with yourself:

- Am I actually making progress, or am I prompting and re-prompting?
- Is the agent adding value here, or am I doing the work twice (once to specify, once to review)?
- Would I be done already if I'd just started typing?
- Am I using the agent because it's the right tool, or because it's the tool I have open?

The best agentic developers I know switch fluidly between agent-assisted and manual coding, sometimes within the same feature. They'll use an agent for the boilerplate, the tests, and the standard patterns. Then they'll close the agent panel, put on headphones, and write the core logic by hand. Then they'll bring the agent back for the cleanup, documentation, and review.

That's the discipline. Not "always use agents" or "never use agents." It's knowing which mode you're in for each task, each file, each function. And being honest with yourself about when the tool is serving you versus when you're serving the tool.

The goal was never to use agents as much as possible. The goal is to build great software as efficiently as possible. Sometimes agents get you there. Sometimes your own keyboard does. The professional knows the difference.
