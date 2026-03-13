# Chapter 8: Skills: Teaching Your Agent New Tricks

Context files tell agents how to write code. Path-scoped rules tell them how to write code in specific areas. Skills are different. Skills teach agents entirely new workflows, complete processes they can invoke when the situation calls for it.

Think of it this way: your AGENTS.md is the employee handbook. Path-scoped rules are the department-specific procedures. Skills are the specialized training courses, the ones an employee takes when they need to handle something they don't already know how to do.

## What Skills Are (and Aren't)

A skill is a bundled set of instructions, documentation, and optional scripts that an agent can invoke on demand. Unlike context files that load automatically, skills load when the agent decides they're relevant based on the skill's description.

This distinction matters. Your AGENTS.md loads every session, consuming context window whether it's relevant or not. A skill for database migrations only loads when the agent is actually doing a migration. A deployment skill only loads when deploying. This keeps your base context lean while giving the agent access to deep, specialized knowledge when it needs it.

Skills are NOT:
- Slash commands (those are deprecated in Claude Code, and for good reason)
- Macros or scripts (though skills can include scripts)
- Prompt templates (they're richer than that)

Skills ARE:
- Reusable instruction sets that agents invoke autonomously
- Self-contained packages of knowledge for specific workflows
- The way you encode complex, multi-step processes that agents can follow

## Skills vs. Slash Commands

If you've used Claude Code, you might have encountered slash commands: user-triggered shortcuts that expand into prompts. Slash commands are being deprecated, and skills replace them. The reason is fundamental to how agentic development works.


Slash commands are human-invoked. You type `/deploy` and the agent executes a predefined sequence. This requires you to know when to invoke the command and remember its exact name.

Skills are LLM-invokable. You say "deploy the API to staging" and the agent recognizes that its deployment skill is relevant, loads it, and follows the instructions. You don't need to remember a command name. You describe what you want, and the agent finds the right skill.

This is a meaningful upgrade. It means:

1. **Discovery is automatic.** The agent matches your intent to available skills based on their descriptions. No memorization required.
2. **Composition is natural.** An agent can invoke multiple skills in a single task. "Run the migrations, then deploy to staging" can chain the migration skill and the deployment skill without you managing the sequence.
3. **New team members benefit immediately.** They don't need to learn your project's slash commands. They describe what they want, and the agent finds the right skill.

## How Skills Work in Claude Code

Claude Code looks for skills in the `.claude/skills/` directory (project-level) or `~/.claude/skills/` (user-level). Each skill is a directory containing at minimum a `SKILL.md` file that describes the skill and provides instructions.

```
.claude/
  skills/
    deploy/
      SKILL.md
      scripts/
        deploy.sh
    db-migrate/
      SKILL.md
      scripts/
        migrate.sh
    pr-review/
      SKILL.md
```

The `SKILL.md` file has a specific structure:

```markdown
---
description: Deploy the API to a target environment (staging or production)
---

# Deployment Skill

## Prerequisites
- Authenticated to Azure CLI (`az account show` to verify)
- Docker running locally
- Access to the container registry

## Steps

1. Run tests first:
   ```bash
   dotnet test --configuration Release
   ```
   If any test fails, STOP. Do not deploy with failing tests.

2. Build the Docker image:
   ```bash
   docker build -t myapi:$(git rev-parse --short HEAD) -f src/Api/Dockerfile .
   ```

3. Tag and push to registry:
   ```bash
   docker tag myapi:$(git rev-parse --short HEAD) myregistry.azurecr.io/myapi:$(git rev-parse --short HEAD)
   docker push myregistry.azurecr.io/myapi:$(git rev-parse --short HEAD)
   ```

4. Deploy to target environment:
   - Staging: `az containerapp update --name myapi-staging --image myregistry.azurecr.io/myapi:$(git rev-parse --short HEAD)`
   - Production: `az containerapp update --name myapi-prod --image myregistry.azurecr.io/myapi:$(git rev-parse --short HEAD)`

5. Verify deployment:
   ```bash
   curl https://myapi-{environment}.azurecontainerapps.io/health
   ```

## Safety
- NEVER deploy to production without explicit user confirmation
- Always run tests before deploying
- If health check fails after deployment, alert the user immediately
```

When a user says "deploy to staging," the agent reads the skill descriptions, identifies this skill as relevant, loads the full SKILL.md, and follows the instructions step by step.

## Anatomy of a Good Skill


Every effective skill has four components, whether or not you formalize them into separate sections.

### 1. Description (The Hook)

The description in the frontmatter is how the agent finds the skill. It should be concise, specific, and use the language developers naturally use.

Good: `Deploy the API to a target environment (staging or production)`
Bad: `Deployment procedures`
Bad: `This skill handles the deployment workflow for the application API including building Docker containers and pushing to Azure Container Registry`

The first is searchable and clear. The second is too vague (deploy what? where?). The third is too long for a description, putting instructions where a summary belongs.

### 2. Instructions (The Steps)

The core of the skill: what to do, in what order, with what commands. Be explicit. Don't assume the agent knows your deployment pipeline, your migration conventions, or your review process.

Write instructions the way you'd write them for a capable new hire on their first week. They know how to code. They know the tools. They don't know your specific process.

### 3. Scripts (The Automation)

Skills can include shell scripts, PowerShell scripts, or any executable that the agent can invoke. This is optional but powerful.

```bash
#!/bin/bash
# scripts/deploy.sh
set -euo pipefail

ENVIRONMENT=${1:?Usage: deploy.sh <staging|production>}
IMAGE_TAG=$(git rev-parse --short HEAD)

echo "Running tests..."
dotnet test --configuration Release || { echo "Tests failed. Aborting."; exit 1; }

echo "Building Docker image..."
docker build -t myapi:$IMAGE_TAG -f src/Api/Dockerfile .

echo "Pushing to registry..."
docker tag myapi:$IMAGE_TAG myregistry.azurecr.io/myapi:$IMAGE_TAG
docker push myregistry.azurecr.io/myapi:$IMAGE_TAG

echo "Deploying to $ENVIRONMENT..."
az containerapp update \
  --name myapi-$ENVIRONMENT \
  --image myregistry.azurecr.io/myapi:$IMAGE_TAG

echo "Verifying..."
curl --fail --silent https://myapi-$ENVIRONMENT.azurecontainerapps.io/health \
  || { echo "Health check failed!"; exit 1; }

echo "Deployed to $ENVIRONMENT successfully."
```

The skill's SKILL.md can reference this script: "Run `scripts/deploy.sh <environment>` to execute the deployment." The agent gets the benefit of your tested automation while the skill provides the decision-making context (when to deploy, what to verify, when to stop).

### 4. Safety Guardrails

Every skill that touches production systems, external services, or irreversible operations needs explicit safety instructions. The agent follows instructions. If your deployment skill doesn't say "ask before deploying to production," the agent might not ask.

Be explicit about:
- What requires user confirmation
- What to do when something fails
- What to never do automatically
- Rollback procedures

## Real Examples

### Database Migration Skill

```markdown
---
description: Create and apply EF Core database migrations
---

# Database Migration Skill

## When to Use
When schema changes are needed: new tables, new columns, index changes,
relationship modifications.

## Creating a Migration

1. Verify the current migration state:
   ```bash
   dotnet ef migrations list --project src/Infrastructure --startup-project src/Api
   ```

2. Make the entity/configuration changes in the Domain and Infrastructure projects.

3. Generate the migration:
   ```bash
   dotnet ef migrations add <DescriptiveName> \
     --project src/Infrastructure \
     --startup-project src/Api
   ```

4. Review the generated migration file:
   - Verify the Up() method does what you expect
   - Verify the Down() method correctly reverses it
   - Check for missing indexes on foreign keys
   - Check string column lengths (never use unbounded nvarchar(max))

5. Apply locally and run tests:
   ```bash
   dotnet ef database update --project src/Infrastructure --startup-project src/Api
   dotnet test
   ```

## Naming Conventions
- AddOrderStatusColumn (adding a column)
- CreatePaymentsTable (new table)
- AddIndexOnOrderCustomerId (new index)
- Breaking_RemoveDeprecatedFields (breaking change, prefixed)

## Rules
- NEVER edit an existing migration that's been committed
- NEVER combine data migrations with schema migrations
- Always include Down() that cleanly reverses the migration
- Test Down() locally before committing
- If migration generation fails, check that the DbContext is correctly configured

## Common Problems
- "No migrations configuration": Missing IDesignTimeDbContextFactory
- "Pending model changes": Run `dotnet ef migrations add` first
- "Column already exists": Someone else added a migration; pull and rebase
```

### PR Review Skill

```markdown
---
description: Review a pull request for code quality, architecture, and conventions
---

# PR Review Skill

## Process

1. Read the PR description and linked issue (if any)
2. Get the diff:
   ```bash
   git diff main...HEAD --stat
   git diff main...HEAD
   ```

3. Check the following, in order:

### Architecture
- [ ] Changes follow the project's architecture patterns (see AGENTS.md)
- [ ] No layer violations (domain doesn't reference infrastructure)
- [ ] New features use vertical slice structure
- [ ] No circular dependencies introduced

### Code Quality
- [ ] Methods under 30 lines
- [ ] Clear naming (no abbreviations, no generic names)
- [ ] No code duplication (check for similar existing code)
- [ ] Error handling uses Result pattern, not exceptions
- [ ] Async all the way down (no .Result or .Wait())

### Testing
- [ ] New code has corresponding tests
- [ ] Test names follow MethodName_Scenario_ExpectedResult
- [ ] Integration tests for new endpoints
- [ ] Edge cases covered (null, empty, boundary values)

### Security
- [ ] No secrets or credentials in code
- [ ] New endpoints have [Authorize] (unless explicitly public)
- [ ] Input validation present for user-supplied data
- [ ] No SQL injection vectors (parameterized queries)

### Database
- [ ] Migrations are clean and reversible
- [ ] Indexes added for new foreign keys
- [ ] No N+1 query patterns introduced

4. Summarize findings as:
   - **Must fix:** Issues that block merge
   - **Should fix:** Issues that should be addressed but aren't blockers
   - **Nit:** Style preferences and minor suggestions

## Tone
Be constructive. Explain WHY something is an issue, not just that it is.
Suggest fixes, don't just flag problems.
```

### Release Skill

```markdown
---
description: Create a release with changelog, version bump, and Git tag
---


# Release Skill

## Steps

1. Determine the version bump:
   - Check commits since last tag: `git log $(git describe --tags --abbrev=0)..HEAD --oneline`
   - Breaking changes: major bump
   - New features: minor bump
   - Bug fixes only: patch bump

2. Update the version:
   ```bash
   # In the .csproj file
   # <Version>X.Y.Z</Version>
   ```

3. Generate changelog from commits:
   - Group by: Features, Bug Fixes, Breaking Changes
   - Include PR numbers and authors
   - Write to CHANGELOG.md, prepending to existing content

4. Create the release commit:
   ```bash
   git add -A
   git commit -m "release: vX.Y.Z"
   git tag vX.Y.Z
   ```

5. Ask user before pushing:
   ```bash
   git push origin main --tags
   ```

## Rules
- NEVER push without user confirmation
- Follow semantic versioning strictly
- Always update CHANGELOG.md
```

## Creating Skills for Your Project

Start with the workflows you repeat most often. Think about the multi-step processes that you currently do manually or explain to teammates verbally.

Common candidates:

- **Deployment:** Building, testing, pushing, deploying, verifying
- **Database migrations:** Creating, reviewing, applying, rolling back
- **New feature scaffolding:** Creating the handler, command/query, controller, tests, and mapping
- **PR review:** Systematic code review against your project's standards
- **Release management:** Version bumping, changelog, tagging, publishing
- **Incident response:** Checking logs, identifying errors, creating hotfix branches
- **Dependency updates:** Checking for updates, upgrading, running tests, resolving breaking changes

### The Skill Creation Process

1. **Do the task manually** and write down every step
2. **Identify decision points** (where you make choices based on context)
3. **Identify automation candidates** (steps that are always the same)
4. **Write the SKILL.md** with steps, decisions documented, and scripts for automation
5. **Test it** by asking the agent to perform the task
6. **Refine** based on where the agent struggled or deviated

The best skills emerge from real work, not from planning sessions. Do the task, then encode what you did.

## Sharing Skills Across Projects and Teams

Skills are portable. A deployment skill written for one .NET project often works for another with minor modifications. A PR review skill based on general engineering principles works across the entire organization.


### Project-Level Skills (.claude/skills/)

Skills specific to one project live in the project's repository. Database migration skills reference project-specific paths and configurations. Deployment skills reference project-specific infrastructure.

These are committed to the repo and evolve with the project.

### User-Level Skills (~/.claude/skills/)

Skills that apply across all your projects live in your home directory. A general PR review skill, a "create a new .NET project" skill, or a "write a blog post" skill aren't project-specific.

These are personal productivity tools. They travel with you across projects.

### Organization-Level Skills

For teams, shared skills can live in a dedicated repository or internal package. The pattern:

1. Create a shared `agent-skills` repository
2. Each skill is a directory with SKILL.md and optional scripts
3. Projects reference shared skills by copying or symlinking

This is still an emerging pattern. The tooling for skill distribution is immature (as of early 2026), but the concept is sound. Claude Code's skills system, for instance, supports installing skills from external sources, and community skill marketplaces are beginning to emerge.

### What Makes Skills Shareable

A skill is easy to share when it:
- Uses relative paths or environment variables instead of hardcoded paths
- Documents its prerequisites clearly
- Doesn't assume a specific project structure beyond what's standard
- Separates project-specific configuration from reusable process

A skill is hard to share when it:
- Hardcodes paths, URLs, or credentials
- Assumes specific file structures unique to one project
- Mixes process instructions with project-specific details

## Skills vs. Other Approaches

### Skills vs. Documentation

"Why not just write good documentation?" You should. But documentation is passive. An agent might or might not read your deployment guide when asked to deploy. A skill is explicitly designed to be discovered and invoked. Its description is optimized for agent matching. Its instructions are optimized for agent execution.

Skills are documentation that's designed to be consumed by agents, not just humans.

### Skills vs. CI/CD Pipelines

"Why not just encode workflows in CI/CD?" You should do that too. CI/CD handles automated, triggered workflows. Skills handle interactive, agent-driven workflows. Your CI pipeline runs tests on push. Your deployment skill helps an agent deploy interactively, with decision points and confirmations.

They complement each other. The deployment skill might say "verify the CI pipeline passed before deploying."

### Skills vs. Scripts

"Why not just write shell scripts?" Scripts are part of skills, not a replacement for them. A shell script handles the mechanical execution. A skill provides the context: when to run the script, what to check before running it, how to interpret the results, what to do when something goes wrong.

The script is the hands. The skill is the brain.

## Anti-Patterns

### The Mega-Skill

A skill that tries to handle every possible scenario becomes an AGENTS.md in disguise. If your deployment skill covers staging, production, canary releases, rollbacks, hotfixes, and database migrations, it's too big. Split it into focused skills: deploy, rollback, hotfix.

### The Stale Skill

Like stale context files, stale skills are worse than no skills. If your deployment process changed and the skill still references the old process, the agent will follow the old process confidently. Audit skills quarterly.

### The Over-Documented Skill

A skill with 500 lines of instructions overwhelms the agent's context. Skills should be concise, focused on the process, and light on background explanation. If the agent needs background knowledge, link to documentation rather than inlining it.

### The Permission-Free Skill

Any skill that touches production, sends emails, modifies databases, or performs irreversible actions needs explicit confirmation steps. "Ask the user before proceeding" should appear at every dangerous decision point.

## Key Takeaways

1. **Skills are agent-invokable workflows.** They load on demand, keeping your base context lean while giving the agent deep knowledge when needed.

2. **Skills replace slash commands.** They're discoverable by description, composable, and don't require memorization.

3. **Start with your most-repeated workflows.** Deployment, migrations, reviews, and scaffolding are common candidates.

4. **Include scripts for automation, instructions for decisions.** The skill provides the brain (when, why, what-if). The scripts provide the hands (how).

5. **Share skills across projects.** Project-level for specific workflows, user-level for personal productivity, organization-level for team standards.

6. **Keep skills focused and current.** One workflow per skill. Update them when processes change. Delete them when they're obsolete.

Skills complete the "passive context" portion of the context stack. Your AGENTS.md, path-scoped rules, and skills together give the agent everything it needs to know about your project's conventions and workflows. The next chapter introduces the "active context" layer: MCP servers, which give agents access to external tools and data in real time.
