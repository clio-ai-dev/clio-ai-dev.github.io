# Chapter 21: Agent + CI/CD Integration

Your CI pipeline just failed. A NuGet package update introduced a breaking change in the serialization layer. Twelve tests are red. In the old world, you'd spend 30 minutes diagnosing the failure, 45 minutes fixing the code, and 15 minutes waiting for CI to go green again.

In the new world, an agent reads the CI failure log, identifies the breaking change, fixes the serialization code, updates the affected tests, pushes a commit, and the pipeline goes green. You get a Slack notification: "CI failure on `main` auto-fixed. See commit `a3f7bc2`."

That's not science fiction. That's Tuesday.

Agent-integrated CI/CD pipelines represent one of the most practical and under-discussed applications of agentic development. While most of the conversation around coding agents focuses on writing new code, the real day-to-day value often comes from agents that maintain, fix, and optimize your existing delivery pipeline.

## Agents That React to Failing Builds

The simplest and most immediately useful CI/CD integration is an agent that reacts to build failures. The pattern is straightforward:

1. CI pipeline fails
2. A webhook triggers the agent with the failure log
3. The agent analyzes the failure, reads the relevant code, and proposes a fix
4. The fix is either auto-committed (for low-risk changes) or submitted as a PR (for anything substantial)

### What Agents Can Fix Automatically

Not all CI failures are created equal. Agents handle some categories reliably and others poorly.

**High confidence (auto-commit candidates):**
- Compilation errors from updated dependencies (renamed methods, changed signatures)
- Formatting/linting failures
- Missing using statements after refactoring
- Test failures caused by changed return types or renamed properties
- Outdated snapshot tests

**Medium confidence (PR candidates, human review required):**
- Test failures from changed business logic
- Integration test failures from environment changes
- Performance test regressions
- Security scan findings

**Low confidence (alert only, don't auto-fix):**
- Mysterious runtime failures with no clear cause
- Intermittent/flaky test failures
- Infrastructure failures (Docker build issues, network timeouts)
- Authentication or permission errors

The categorization matters because the whole point of CI is trust. If your agent auto-commits a "fix" that papers over a real bug, you've undermined the pipeline's purpose. Start conservative (alert only), graduate to PRs (human review), and only auto-commit when you've built confidence in specific failure categories.

### Implementation Pattern

Here's a concrete implementation using GitHub Actions:

```yaml
# .github/workflows/auto-fix.yml
name: Agent Auto-Fix

on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]

jobs:
  auto-fix:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.workflow_run.head_branch }}
      
      - name: Download failure logs
        uses: actions/download-artifact@v4
        with:
          name: test-results
          run-id: ${{ github.event.workflow_run.id }}
      
      - name: Analyze and fix
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # Feed failure logs to the agent
          claude --print "Analyze the CI failure in test-results/. 
            Fix the issue in the source code. 
            Run 'dotnet test' to verify. 
            Only modify files that are directly related to the failure.
            Do not change test assertions unless the test expectation 
            is clearly outdated." \
            --allowedTools edit,bash
      
      - name: Create PR if changes exist
        if: ${{ steps.fix.outputs.changes == 'true' }}
        uses: peter-evans/create-pull-request@v6
        with:
          title: "fix: auto-remediation for CI failure"
          body: "Automated fix for CI failure. Review carefully."
          branch: auto-fix/${{ github.event.workflow_run.head_sha }}
```

This is a starting point. Production implementations need safeguards: rate limiting (don't let the agent create 50 PRs for the same flaky test), scope limiting (only touch files related to the failure), and approval gates (require human approval before merge).

## Pipeline Generation with Agents


Writing CI/CD pipelines is one of those tasks that's tedious, error-prone, and well-suited to agents. The YAML is finicky. The documentation is sprawling. The debugging cycle is slow (push, wait for CI, read the error, fix, repeat).

### GitHub Actions Generation

Give an agent your project structure and ask for a CI pipeline:

"Generate a GitHub Actions workflow for this .NET 9 solution. It should: build all projects, run unit tests with coverage reporting, run integration tests against a PostgreSQL service container, publish coverage to Codecov, and create a release on tag push. Use caching for NuGet packages. Target `ubuntu-latest`."

The agent produces a working `ci.yml` in seconds. But here's the important part: you review it. CI pipelines are security-sensitive. An agent that adds `permissions: write-all` or a dubious third-party action is a real risk. Review pipeline changes with the same rigor you'd apply to authentication code.

### Azure DevOps Pipelines

The same pattern works for Azure DevOps, though the YAML schema is different and the documentation is more fragmented. Agents are particularly useful here because Azure DevOps pipeline syntax has subtle differences from GitHub Actions that trip up even experienced developers. Let the agent handle the syntax; you focus on the logic.

```yaml
# Agent-generated azure-pipelines.yml (review before committing!)
trigger:
  branches:
    include:
      - main
      - release/*

pool:
  vmImage: 'ubuntu-latest'

variables:
  buildConfiguration: 'Release'
  dotnetVersion: '9.0.x'

stages:
  - stage: Build
    jobs:
      - job: BuildAndTest
        steps:
          - task: UseDotNet@2
            inputs:
              version: $(dotnetVersion)
          
          - task: DotNetCoreCLI@2
            displayName: 'Restore'
            inputs:
              command: restore
              projects: '**/*.csproj'
          
          - task: DotNetCoreCLI@2
            displayName: 'Build'
            inputs:
              command: build
              projects: '**/*.csproj'
              arguments: '--configuration $(buildConfiguration) --no-restore'
          
          - task: DotNetCoreCLI@2
            displayName: 'Test'
            inputs:
              command: test
              projects: '**/*Tests.csproj'
              arguments: '--configuration $(buildConfiguration) --collect:"XPlat Code Coverage"'
```

## Infrastructure as Code with Agents

Terraform, Bicep, and Pulumi configurations are another category where agents provide significant leverage. IaC files are declarative, well-documented, and follow predictable patterns. Agents excel at generating them.

### Bicep for Azure Deployments

For .NET developers deploying to Azure, Bicep is the natural IaC choice. Agents can generate Bicep files from a description of your architecture:

"Generate Bicep modules for a .NET Aspire application deployment: an Azure Container Apps environment, two container apps (API and worker), an Azure SQL database, a Redis cache, and Application Insights. Use managed identity for all service-to-service communication. Output connection strings as Container Apps secrets."

The agent produces modular Bicep files that follow Azure best practices. But IaC is another area where review is critical. A misconfigured network rule, an overly permissive role assignment, or a missing encryption setting can create security vulnerabilities. Review IaC changes with security in mind, not just "does it deploy."

### Terraform and Pulumi

The same pattern applies to Terraform (for multi-cloud or AWS/GCP deployments) and Pulumi (for developers who prefer C# over HCL). Agents handle the syntax and resource configuration; you handle the architecture decisions and security review.

Pulumi is particularly interesting for .NET developers because you write infrastructure in C#:

```csharp
// Agent-generated Pulumi infrastructure
var resourceGroup = new ResourceGroup("rg-myapp");

var appServicePlan = new AppServicePlan("plan-myapp", new()
{
    ResourceGroupName = resourceGroup.Name,
    Sku = new SkuDescriptionArgs
    {
        Name = "B1",
        Tier = "Basic",
    },
});

var appService = new WebApp("app-myapp", new()
{
    ResourceGroupName = resourceGroup.Name,
    ServerFarmId = appServicePlan.Id,
    SiteConfig = new SiteConfigArgs
    {
        NetFrameworkVersion = "v9.0",
        AlwaysOn = true,
    },
});
```

An agent can generate, modify, and refactor Pulumi code just like application code. The same context engineering principles apply: give the agent your architecture decisions, your naming conventions, and your security requirements.

## API Contract Testing and OpenAPI

Agents are remarkably good at generating and maintaining OpenAPI specifications. This matters because API contracts are the glue between services, and keeping them accurate is one of those tasks that teams consistently neglect.

### Generating OpenAPI Specs from Code

"Generate an OpenAPI 3.1 specification for all controllers in `src/Api/Controllers/`. Include request/response schemas, error responses, authentication requirements, and example values. Use the XML documentation on the controller methods for descriptions."

The agent reads your controllers, extracts the routes, parameters, and return types, and produces a complete OpenAPI spec. You validate it against the actual API behavior (run the tests, hit the endpoints), and now you have accurate, up-to-date API documentation.

### Contract Testing

Once you have an OpenAPI spec, agents can generate contract tests that verify your API actually matches the spec:

```csharp
[Theory]
[InlineData("/api/customers", "GET", 200)]
[InlineData("/api/customers/999", "GET", 404)]
[InlineData("/api/customers", "POST", 201)]
[InlineData("/api/customers", "POST", 400)] // Invalid body
public async Task ApiEndpoint_MatchesOpenApiContract(
    string path, string method, int expectedStatus)
{
    // Agent generates these tests from the OpenAPI spec
    var request = CreateRequestFromSpec(path, method, expectedStatus);
    var response = await _client.SendAsync(request);
    
    Assert.Equal(expectedStatus, (int)response.StatusCode);
    await AssertResponseMatchesSchema(response, path, method, expectedStatus);
}
```

This is one of those areas where agents create a virtuous cycle: the agent generates the spec from code, generates tests from the spec, and the tests catch when code and spec diverge. The maintenance burden drops to near zero.

## The Agent-in-the-Loop CI/CD Pipeline


Putting it all together, here's what a fully agent-integrated CI/CD pipeline looks like:

```
Developer pushes code
    │
    ▼
CI Pipeline Runs
    │
    ├── Build ─── Fails? ──► Agent analyzes, creates fix PR
    │
    ├── Unit Tests ─── Fails? ──► Agent analyzes, creates fix PR
    │
    ├── Integration Tests ─── Fails? ──► Agent analyzes, alerts team
    │
    ├── Security Scan ─── Findings? ──► Agent creates remediation PR
    │
    ├── API Contract Check ─── Drift? ──► Agent updates spec or code
    │
    ├── Code Coverage ─── Below threshold? ──► Agent generates missing tests
    │
    └── All Green ──► Deploy to staging
                          │
                          ├── Smoke Tests ─── Fails? ──► Agent rolls back, alerts
                          │
                          └── All Green ──► Deploy to production
```

Each failure point has an agent that can respond intelligently. Not blindly, not without oversight, but with targeted analysis and proposed fixes that a human can review and approve.

The key insight: agents in CI/CD aren't replacing your pipeline. They're reducing the time between "something broke" and "here's the fix." Instead of a developer context-switching away from their current task to investigate a CI failure, the agent handles triage and initial remediation. The developer reviews and approves.

## Security Scanning with Agent Remediation

Security scanning in CI is common. Acting on the results is rare. Most teams have a security scan that produces findings, and those findings sit in a backlog until someone gets around to them (which is never).


Agents change this dynamic. When a security scan finds a vulnerability:

1. The agent reads the finding (CVE ID, affected package, severity)
2. The agent checks for an available fix (updated package version, patch)
3. The agent applies the fix, updates the package, and runs the tests
4. The agent creates a PR with the fix and a summary of the vulnerability

For dependency vulnerabilities (the most common category), this is nearly fully automatable. The fix is usually "update package X to version Y." The agent does it, the tests verify nothing broke, and you approve the PR.

For code-level vulnerabilities (SQL injection, XSS, insecure deserialization), the agent can still help. It may not produce a perfect fix, but it can identify the vulnerability, explain the risk, and propose a remediation approach. That's better than a finding sitting in a backlog for six months.

## Real Example: Agent Fixes a Failing CI Build

Let's walk through a concrete scenario. Your team pushes a routine PR that updates `Microsoft.EntityFrameworkCore` from 9.0.1 to 9.0.2. CI runs. Eight tests fail.

### Without Agent Integration

1. Developer gets notified (Slack, email). Maybe they see it 30 minutes later.
2. Developer opens the CI logs. Reads through the failure output. Identifies that the `SaveChangesAsync` behavior changed for batch operations.
3. Developer reads the EF Core 9.0.2 release notes. Finds the breaking change.
4. Developer updates the affected code. Runs tests locally. Pushes a fix.
5. CI runs again. Green. Total time: 60-90 minutes.

### With Agent Integration

1. CI fails. The auto-fix workflow triggers.
2. Agent reads the test failure output. Identifies 8 failures, all in `RepositoryTests`.
3. Agent reads the EF Core 9.0.2 release notes (it fetches the changelog from NuGet).
4. Agent identifies the breaking change: batch `SaveChangesAsync` now throws `DbUpdateConcurrencyException` instead of returning 0 for concurrent modifications.
5. Agent updates the repository implementations to handle the new exception type.
6. Agent updates the affected tests to expect the new behavior.
7. Agent runs `dotnet test`. All green.
8. Agent creates a PR with a clear description: "Fix EF Core 9.0.2 breaking change in batch save behavior. Updated 3 repository classes and 8 tests. See: [link to release notes]."
9. Developer reviews the PR. Approves. Merges. Total developer time: 5-10 minutes.

That's the difference. Not "the developer didn't have to do anything." The developer still reviewed, still approved, still made the judgment call. But the grunt work of diagnosis and remediation happened automatically.

## Setting Up Agent CI/CD Integration

If you want to add agent capabilities to your CI/CD pipeline, start small:

### Step 1: Alert-Only Mode

Add an agent that reads CI failure logs and posts an analysis to your team channel. No auto-fixing. Just "here's what broke and here's my suggested fix." This builds trust and helps you calibrate the agent's analysis quality.

### Step 2: PR Mode

Graduate to creating PRs for well-understood failure categories. Dependency updates, formatting fixes, snapshot test updates. Low-risk, high-frequency fixes that don't require deep domain knowledge.

### Step 3: Selective Auto-Commit

For the categories where the agent has proven reliable (formatting, linting, dependency version bumps), enable auto-commit on the branch (not on main). The changes still go through PR review before merging to main.

### Step 4: Full Integration

Build out the full pipeline with agent checkpoints at each stage. Security scanning, contract testing, coverage enforcement, all with agent remediation capabilities.

The progression matters. Jumping straight to auto-commit for everything is a recipe for disaster. Build trust incrementally, the same way you would with a new team member.

## The Cost-Benefit Reality

Agent CI/CD integration has real costs: API tokens for every CI run that triggers an agent, compute time for the agent's analysis, and the maintenance burden of the integration itself.

For most teams, the math works out. A single CI failure that blocks a team of 5 developers for an hour costs 5 developer-hours. An agent that resolves the failure in 10 minutes (plus 5 minutes of review) costs a few dollars in API tokens. The ROI is clear.

But track it. Measure how often agents successfully fix failures vs. how often they produce noise. If the signal-to-noise ratio is poor, adjust the categories, tighten the scope, or improve your context files. Agent CI/CD integration is a tool that requires tuning, not a set-and-forget solution.
