# Chapter 20: Multi-Agent Coordination

Running three agents in parallel is one thing. Having those agents coordinate with each other is another thing entirely.

Parallel agents (Chapter 18) work on independent tasks. They don't know about each other. They don't need to. Multi-agent coordination is what happens when the tasks aren't independent, when Agent A's output is Agent B's input, when three agents need to work on the same feature without stepping on each other's code, when one agent needs to plan the work and distribute it to others.

This is harder. It's also where the real leverage lives.

## The Specialization Model

The most common multi-agent pattern is specialization: different agents with different roles working on different aspects of the same feature. Think of it like a small team where each member has a clear responsibility.

### The Classic Three-Agent Setup

For a full-stack feature, the setup looks like this:


**API Agent:** Builds the backend, the controllers, services, repositories, DTOs, and API tests. This agent has deep context about your backend architecture, your data access patterns, and your API conventions.

**Frontend Agent:** Builds the UI components, pages, state management, and frontend tests. This agent knows your component library, your routing patterns, and your styling conventions.

**Test Agent:** Writes integration tests that verify the API and frontend work together. This agent understands your test infrastructure, your test data setup, and your CI pipeline.

Each agent gets its own context file tailored to its specialty. The API agent's context file emphasizes your backend patterns. The frontend agent's context file emphasizes your component architecture. Specialization isn't just about dividing work; it's about giving each agent the right context for its role.

### Why Specialization Works

The alternative to specialization is giving one agent the entire task: "Build the full-stack order export feature." This works for simple features but falls apart as complexity grows. A single agent trying to hold backend architecture, frontend patterns, and test infrastructure in context simultaneously will make compromises in all three areas.

Specialized agents produce better output because they have focused context. The API agent doesn't waste context tokens on React component patterns. The frontend agent doesn't waste context tokens on Entity Framework configurations. Each agent is an expert in its lane.

The tradeoff is coordination overhead. Three specialized agents need someone (or something) to make sure their outputs fit together. That's where orchestration comes in.

## Agent Orchestrators

An orchestrator is an agent (or tool) that manages other agents. It takes a high-level goal, breaks it into tasks, assigns those tasks to specialized agents, monitors progress, handles failures, and integrates the results.

### The Planning Phase

The orchestrator's first job is planning. Given "Build the order export feature," the orchestrator:

1. Reads the feature specification
2. Identifies the components needed (API endpoint, exporter services, frontend page, tests)
3. Determines dependencies (the frontend needs the API to exist first, integration tests need both)
4. Creates a task graph with ordering constraints
5. Assigns tasks to specialized agents in the right order

This planning step is crucial. Without it, you get agents working at cross-purposes or building against interfaces that don't exist yet.

### The Coordination Phase

Once tasks are assigned, the orchestrator monitors execution:

- **Progress tracking:** Which agents are done? Which are stuck?
- **Dependency management:** Agent B can't start until Agent A delivers the API contract.
- **Conflict detection:** Are two agents trying to modify the same file?
- **Failure handling:** If Agent A fails, what happens to the agents that depend on its output?

### File-Based Locking

When multiple agents work on the same repository, file conflicts are the primary coordination challenge. Several patterns have emerged:

**Branch isolation:** Each agent works on its own branch (same as the worktree pattern from Chapter 18). The orchestrator handles merging.

**File ownership:** The orchestrator assigns file-level ownership. Agent A owns `src/Services/`, Agent B owns `src/Controllers/`, Agent C owns `tests/`. No agent touches another agent's files.

**Interface contracts:** Agents communicate through shared interfaces defined before any agent starts working. The interfaces are committed to the main branch. Each agent implements against them in isolation.

**Lock files:** Some orchestrators use a simple lock file mechanism. Before an agent modifies a file, it claims a lock. Other agents skip or queue changes to locked files. This is the most granular approach but adds complexity.

In practice, branch isolation combined with interface contracts handles 90% of coordination needs. Lock files are overkill for most teams.

## VS Code as Multi-Agent HQ

In February 2026, Microsoft announced that VS Code would become a unified interface for managing multiple agents simultaneously. This isn't just marketing. The practical implications are significant.

Before this announcement, running multiple agents meant multiple terminals, multiple browser tabs, and manual context-switching between them. VS Code's multi-agent support puts all your agents in one interface:

- **Side-by-side agent panels:** See Claude Code, Codex, and Copilot working simultaneously
- **Shared workspace context:** All agents see the same files, the same Git state, the same test results
- **Unified diff review:** Review output from multiple agents in a single diff view
- **Agent-to-agent handoffs:** Route the output of one agent as input to another

This is still early (as of this writing), but the direction is clear: the IDE becomes the command center for a team of agents, not just a text editor with AI features.

For .NET developers, this is particularly relevant because VS Code's C# support (via the C# Dev Kit) has reached parity with Visual Studio for most workflows. Running multiple agents in VS Code while maintaining full IntelliSense, debugging, and test runner integration makes the multi-agent workflow practical for day-to-day development.

## Branch Strategy for Multi-Agent Work

When multiple agents contribute to the same feature, your Git strategy matters more than usual.


### The Feature Branch Pattern

```
main
 └── feature/order-export           (integration branch)
      ├── agent/order-export-api     (API agent's branch)
      ├── agent/order-export-ui      (Frontend agent's branch)
      └── agent/order-export-tests   (Test agent's branch)
```

The feature branch is the integration point. Each agent works on its own sub-branch. When an agent completes its work:

1. You review the agent's PR against the feature branch
2. Merge if approved
3. The next agent rebases on the updated feature branch and continues

This pattern keeps main clean (no half-finished features) while allowing agents to work in parallel on separate branches.

### Handling Merge Conflicts

Merge conflicts in multi-agent work usually fall into two categories:

**Trivial conflicts:** Two agents added import statements in the same file. These resolve automatically or with a quick manual fix.

**Semantic conflicts:** Two agents made incompatible assumptions about shared code. The API agent returned `OrderExportResult` but the frontend agent expected `ExportResponse`. These require you to make a decision and update one or both implementations.

Semantic conflicts are the reason you define interfaces upfront. With shared contracts, the only conflicts are trivial ones. Without them, every merge is a negotiation.

### The Rebase-and-Continue Pattern

When Agent A's work is merged and Agent B needs to incorporate those changes:

```bash
cd ~/repos/my-app-agent-b
git fetch origin
git rebase origin/feature/order-export
# Agent B continues working with Agent A's code now visible
```

If you're using worktrees, this is seamless. The agent's worktree picks up the rebased code and continues. In practice, you often just re-launch the agent with an updated prompt: "The API is now merged. Implement the frontend against the actual endpoints in `src/Controllers/OrderExportController.cs`."

## The Orchestrator Pattern


The most powerful (and most complex) multi-agent workflow uses a dedicated orchestrator agent that manages the others. This is the pattern used by tools like ComposioHQ's agent-orchestrator, and it's the pattern that scales to genuinely complex features.

### How It Works

1. **You give the orchestrator a goal:** "Build the order export feature according to the spec in `docs/order-export.md`."
2. **The orchestrator reads the spec** and creates a task breakdown.
3. **The orchestrator spawns specialized agents** for each task, with appropriate context and instructions.
4. **The orchestrator monitors progress,** checking each agent's output, running tests, and intervening when agents get stuck.
5. **The orchestrator integrates the results,** merging branches, resolving conflicts, and running the full test suite.
6. **The orchestrator reports back** with a summary of what was built, what worked, and what needs your attention.

### Personal AI Agents as Orchestrators

This is where tools like OpenClaw enter the picture. A personal AI agent running on your machine (or a server you control) has persistent context, access to your full development environment, and the ability to spawn and manage sub-agents.

The workflow looks like this:

```
You: "Build the order export feature. Spec is in the usual place."

OpenClaw (orchestrator):
  1. Reads docs/order-export.md
  2. Identifies three work streams: API, frontend, tests
  3. Creates three worktrees and branches
  4. Spawns Agent 1 on API implementation
  5. Spawns Agent 2 on frontend (queued until API contract is ready)
  6. Waits for Agent 1 to deliver the API contract
  7. Spawns Agent 2 with the actual API contract as context
  8. Spawns Agent 3 on integration tests (after both are done)
  9. Reviews all output, runs full test suite
  10. Presents you with a summary and three PRs to review
```

You went from "read the spec" to "review three PRs" with a single instruction. The orchestrator handled decomposition, sequencing, context management, and integration.

This is the high end of multi-agent coordination. It requires trust in the orchestrator, comprehensive tests (the orchestrator's primary quality signal), and well-structured repositories. But when it works, the leverage is extraordinary.

## Real Example: Building a Full-Stack Feature with Coordinated Agents

Let's walk through building a customer notification preferences feature using coordinated agents. Customers can choose which notifications they receive (email, SMS, push) and set quiet hours.

### Phase 1: Contract Definition (You, 20 minutes)

You write the API contract and the shared types:

```csharp
// Shared contract
public record NotificationPreferences
{
    public bool EmailEnabled { get; init; }
    public bool SmsEnabled { get; init; }
    public bool PushEnabled { get; init; }
    public TimeOnly QuietHoursStart { get; init; }
    public TimeOnly QuietHoursEnd { get; init; }
}

// API contract
// GET  /api/customers/{id}/notification-preferences
// PUT  /api/customers/{id}/notification-preferences
// Response: NotificationPreferences
// Errors: 404 (customer not found), 400 (invalid quiet hours range)
```

You commit this to the feature branch. All agents will see it.

### Phase 2: Parallel Implementation (3 agents, ~1 hour)

**Agent 1 (API):** "Implement the notification preferences API endpoints. Use the contract in `src/Contracts/NotificationPreferences.cs`. Create `NotificationPreferencesService` and `NotificationPreferencesRepository`. Use EF Core for persistence. Add a migration. Write unit and integration tests."

**Agent 2 (Frontend):** "Build a notification preferences page at `/settings/notifications`. Use the API contract types. Toggle switches for email/SMS/push. Time pickers for quiet hours. Optimistic UI updates. Component tests with React Testing Library."

**Agent 3 (Infrastructure):** "Add notification preferences to the database schema. Create the EF Core migration. Seed default preferences for existing customers (all enabled, no quiet hours). Add a health check for the notification preferences table."

### Phase 3: Integration (You, 30 minutes)

Agent 1 and Agent 3 both touched the database schema. You resolve the migration ordering (Agent 3's seed data migration depends on Agent 1's schema migration). Quick fix.


Agent 2's frontend calls the API correctly because it coded against the shared contract. The only adjustment: you add CORS configuration for the new endpoint, which neither agent thought to do.

Run the full test suite. 47 tests pass, 2 fail (both are timezone-related edge cases in the quiet hours logic). You fix them manually. Takes 10 minutes.

Total elapsed time: about 2 hours, of which maybe 50 minutes was your active involvement. The feature is complete with API, frontend, database migration, seed data, and comprehensive tests.

## When Multi-Agent Coordination Makes Sense

Multi-agent coordination has significant overhead. The planning, the interface definitions, the branch management, the integration work. This overhead is only worth paying when the feature is complex enough to justify it.

### Use Multi-Agent Coordination When:

- The feature has clear architectural boundaries (API/frontend/infrastructure)
- Multiple people would work on it in a traditional team
- The interfaces between components can be defined upfront
- You have a comprehensive test suite to catch integration issues
- The feature would take more than a day to build solo

### Stick to Single or Parallel Agents When:

- The feature is small enough to hold in one context
- The components are tightly coupled (changes in one require changes in another)
- You're still exploring the design (agents can't coordinate on a moving target)
- Your test coverage is thin (you won't catch integration bugs)

Multi-agent coordination is a power tool. It's not for every nail. But for the nails it fits, nothing else comes close.

## The Future of Multi-Agent Coordination

We're in the early days. The tools are improving rapidly. VS Code's multi-agent support will mature. Orchestrator frameworks will get smarter about planning and conflict resolution. Agents will develop better protocols for communicating with each other (not just through files, but through structured messages).

The trajectory is clear: development teams will be hybrid, some human members, some agent members, coordinated through the same tools and processes. The developers who learn to orchestrate agents today will be the ones leading those hybrid teams tomorrow.

But the fundamentals won't change. Clear specifications. Well-defined interfaces. Comprehensive tests. Good architecture. These have always been the foundation of effective teamwork, whether the team members are human or artificial.
