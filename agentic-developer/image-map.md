# Image Map — The Agentic Developer

**Rule:** 1 image every 2–3 pages (~500–750 words apart), placed at major `##` headings. Each image must meet at least one criterion: (1) captures a key learning, (2) communicates faster than text (flows, comparisons, hierarchies), or (3) makes a concept "click" visually.

**Style:** Hand-drawn sketch illustration, consistent line-art style, black ink on white/light background.

**Image ID format:** `img-XX-YY` (XX = chapter, YY = image number within chapter)

**Total:** 52 images

---

## Chapter 1 — Software Development Has Changed (3 images) ✅ DONE

| ID | Section | Description | Placement |
|---|---|---|---|
| img-01-01 | Era 3: Agents | Timeline showing three eras: Autocomplete (2021) → Chat (2023) → Agents (2025–2026), drawn as an ascending staircase with icons for each era | After "Era 3: Agents" section intro |
| img-01-05 | Context Became King | Context engineering concept: a funnel labeled "what the model sees = what you get" with good context flowing in and good code flowing out | After "Context Became King" heading |
| img-01-09 | The Agentic Developer Playbook | A hand holding an open playbook/field guide with chapter icons sketched on its pages, representing the book's roadmap | After "The Agentic Developer Playbook" heading |

---

## Chapter 2 — The METR Paradox (2 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-02-01 | The Study | **Key learning: the 39-point perception gap.** Two overlapping bar charts — one labeled "Perceived speed" (+20% faster, in green) and one "Actual speed" (−19% slower, in red). A giant "39%" gap between them with a question mark. The visual makes the paradox instantly graspable. | Under heading |
| img-02-02 | The Discipline Gap | **Key learning: the variable is methodology, not the tool.** A fork in the road: left path "Naive use" (vague prompt → accept blindly → debug later) slopes downhill; right path "Disciplined use" (context + tests + specs → review → ship) slopes uphill. Same starting tool, opposite outcomes. | Under heading |

---

## Chapter 3 — Your New Job Description (2 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-03-01 | The Old Job vs. The New Job | **Better than text: side-by-side comparison.** Two pie charts — left "Old Job" dominated by "Writing code" (60-70%) with small slices for reading/other; right "New Job" dominated by "Review" (40%) and "Specs & Context" (40%) with a small "Hand-coding" slice (20%). The shift is immediately visible. | Under heading |
| img-03-02 | The 80/20 of Agentic Development | **Key learning: the three foundational practices.** A triangle/pyramid with three blocks: base = "Context Files" (AGENTS.md icon), middle = "Tests First" (green checkmark), top = "Spec Your Tasks" (document icon). Arrow on the side labeled "80% of productivity gains." This is THE takeaway of the chapter. | Under "The 80/20" heading |

---

## Chapter 4 — The Agentic Engineering Mindset (4 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-04-01 | The Junior Developer with Perfect Memory and Zero Judgment | **Lifts the learning: the core mental model.** A robot with an enormous filing cabinet for a brain (labeled "every Stack Overflow answer, every GitHub repo") but a tiny, flickering lightbulb labeled "judgment" — holding up textbook-perfect code that's wrong for THIS project. The gap between knowledge and judgment clicks instantly. | Under heading |
| img-04-02 | The Director Mindset | **Key learning: your new role.** A film director's chair with clapboard, megaphone, and storyboard — the storyboard panels show: Vision (what/why), Constraints (guardrails), Quality Bar (definition of done). Agents work the "set" while the director makes the calls. | Under heading |
| img-04-03 | The Five Mental Traps | **Better than text: pattern recognition.** Five labeled traps on a path: "Over-Trusting" (rubber-stamp), "Under-Specifying" (blank prompt), "Anthropomorphizing" (agent with human face), "All-or-Nothing" (binary switch), "Static Calibration" (frozen dial). A developer navigating around them. Seeing all five at once builds awareness. | Under heading |
| img-04-04 | Calibrating Expectations by Task Type | **Better than text: a visual spectrum.** A vertical gauge from green to red: bottom = "Boilerplate/CRUD" (high agent confidence, trust more), middle = "Business logic" (medium, collaborate), top = "Security/architecture" (low, verify everything). A sliding marker shows how to calibrate review intensity per task. | Under heading |

---

## Chapter 5 — From Vibe Coding to Vibe Engineering (2 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-05-01 | The Spectrum | **Key learning: the four modes.** A horizontal spectrum bar with four labeled zones: "Pure Vibe Coding" (10-15%, chaos icon) → "Vibe Engineering" (50-60%, balanced scales) → "Agentic Engineering" (25-30%, full discipline gears) → "Traditional" (5-10%, keyboard). Percentage labels show where time SHOULD go. This is THE framework of the chapter. | Under heading |
| img-05-02 | Knowing Which Mode to Use | **Better than text: decision flowchart.** A decision tree: "What's the blast radius?" → High → "Agentic Engineering"; "How long will it live?" → Hours → "Vibe Code it"; "Who else touches it?" → Team → "Agentic Engineering"; etc. Visual flow makes the decision process scannable. | Under heading |

---

## Chapter 6 — Writing Effective Context Files (3 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-06-01 | The Context Stack | **Key learning: the layered context system.** A layered stack diagram: bottom = "Codebase itself" (foundation), then "Test suite", then "AGENTS.md" (highlighted as highest leverage), then "Path-scoped rules", then "Skills", top = "MCP servers". An AI brain sits on top consuming all layers. Shows WHERE to invest effort. | Under heading |
| img-06-02 | Without Context vs. With Context | **Lifts the learning: the compounding payoff.** Split panel — Left: prompt "Add order history endpoint" → agent produces generic code (AutoMapper, sync, no auth, no pagination) → "20 min rewriting." Right: same prompt + AGENTS.md → agent produces architecture-matching code (MediatR, async, [Authorize], paginated) → "3 min review, approved." The 17-minute difference, multiplied across a day, makes context engineering click. | After "A Real Example" heading |
| img-06-03 | Context File Anti-Patterns | **Key learning: four failure modes.** Four sketches in a 2x2 grid: "The Novel" (2000-line file, agent drowning), "The Museum" (dusty cobwebbed file, dated 2024), "The Wishlist" (aspirational rules contradicting actual code), "The Secret Keeper" (missing "don't" rules, agent using AutoMapper). Quick visual reference for what to avoid. | Under heading |

---

## Chapter 7 — Path-Scoped Rules (2 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-07-01 | How Path-Scoped Rules Work | **Better than text: hierarchy + activation.** A project tree: root has AGENTS.md (always active, glowing). Under it, `.claude/rules/controllers.md` lights up ONLY when `src/Api/Controllers/` is being edited. Other rule files (tests.md, migrations.md) stay dim. Shows the "surgical context" concept — right rules, right time. | Under heading |
| img-07-02 | The Reactive Workflow | **Key learning: add rules from mistakes, not speculation.** A 3-step flow: (1) Agent makes wrong choice → (2) Developer corrects in review → (3) Developer adds path-scoped rule → (4) Agent never makes that mistake again. A feedback loop arrow from step 4 back to step 1 with "prevented." | Under "When to Add" heading |

---

## Chapter 8 — Skills (2 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-08-01 | Skills vs. Slash Commands | **Key learning: LLM-invokable vs human-invoked.** Two panels — Left: "Slash commands" — developer must remember `/deploy`, type it manually (human → command → agent). Right: "Skills" — developer says "deploy to staging," agent matches intent to skill description automatically (human → intent → agent finds skill). The upgrade from memorization to discovery. | Under heading |
| img-08-02 | Anatomy of a Good Skill | **Better than text: structural overview.** An annotated SKILL.md file with four callout bubbles: "Description (the hook — how agents find it)", "Prerequisites (what must be true first)", "Steps (explicit, ordered instructions)", "Safety guardrails (confirmation points, rollback)". Shows the four essential components at a glance. | Under heading |

---

## Chapter 9 — MCP Servers (1 image)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-09-01 | What MCP Is | **Better than text: hub-and-spoke architecture.** Center hub labeled "MCP Protocol" with spokes connecting to: database schema, API docs, deployment status, issue tracker, cloud services. Static context (AGENTS.md) shown separately as "what you knew when you wrote it" vs MCP as "what's true right now." The static-vs-dynamic distinction clicks. | Under heading |

---

## Chapter 10 — Designing an AI-Friendly Codebase (2 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-10-01 | Naming and File Size | **Better than text: before/after comparison.** Split panel — Left: a 2000-line file with cryptic names (`OrderProcessor` that actually handles payments, `x`, `doStuff`), agent produces wrong code. Right: small focused files (~50 lines each) with clear names (`PaymentService`, `validateShippingAddress`), agent produces correct code. Two improvements, one visual. | Under "Naming" heading |
| img-10-02 | The Test Suite as Your Most Powerful Context | **Key learning: tests ARE specification.** A test file radiating four arrows to labels: "What the code should do" (specification), "What edge cases matter" (boundaries), "What patterns to follow" (conventions), "Whether changes work" (verification). The test file is drawn as a glowing blueprint — the most valuable file the agent reads. | Under heading |

---

## Chapter 11 — IDE Agents (1 image)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-11-01 | The Decision Matrix | **Better than text: 2×2 comparison grid.** Axes: "Team/Enterprise needs" (low→high) × "Customization/power" (low→high). Copilot in high-team/low-custom quadrant (the default), Cursor in low-team/high-custom (power user), Windsurf in middle. Each with 1-line strength. Makes tool selection instant. | Under heading |

---

## Chapter 12 — CLI and Cloud Agents (2 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-12-01 | When CLI Beats IDE (and Vice Versa) | **Better than text: Venn diagram.** Left circle "CLI Agents" (large refactors, CI integration, headless/scripted, full filesystem access). Right circle "IDE Agents" (visual diffs, quick edits, exploration, inline completions). Overlap: both work for feature implementation. Instant reference for tool selection. | Under heading |
| img-12-02 | Cloud Agents: Fire and Forget | **Lifts the learning: the async workflow.** A timeline: 10pm developer presses "launch" on phone → midnight agent creates PR (developer sleeping) → 8am developer reviews PR with coffee. The "overnight junior developer" concept clicks when you see the timeline. | Under heading |

---

## Chapter 13 — The TDD Agent Loop (2 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-13-01 | The Loop in Detail | **Key learning: THE core workflow.** A circular flow: "You write tests (RED)" → "Agent implements code" → "Agent runs tests" → "Tests fail? Agent fixes" → "All GREEN" → "You review" → back to start for next feature. The tight feedback loop is inherently visual — it's a cycle, not a sequence. Most important image in the book. | Under heading |
| img-13-02 | The Confidence Equation | **Key learning: the formula that ties the book together.** An equation diagram: "Confidence = Context quality × Test coverage × Specification clarity." Three dials, each labeled. If ANY dial is at zero, the output gauge reads zero. When all three are high, the output gauge is maxed. This connects chapters 4, 6, 13, and 14 into one framework. | Under heading |

---

## Chapter 14 — Spec-First Development (2 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-14-01 | Why Specs Matter More Now | **Lifts the learning: diverging outcomes.** Two paths from the same starting point: "No spec" path leads through a maze (rework, misunderstanding, debugging wrong behavior); "Spec first" path is a straight road to "Feature complete." An agent stands at the fork — the spec IS the steering wheel. | Under heading |
| img-14-02 | The Spec → Agent → Review → Iterate Cycle | **Better than text: iterative spiral.** A tightening spiral: outer ring = rough spec → agent builds → developer reviews → feedback. Each loop tighter and closer to center "Done." Shows that it's iterative, not one-shot. | Under heading |

---

## Chapter 15 — Error-Driven Debugging (1 image)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-15-01 | How to Structure Error Context | **Better than text: structured handoff.** A clipboard with four labeled sections being handed from developer to agent: "Error message" (the symptom), "Stack trace" (the evidence), "What I've tried" (context), "Relevant code" (scope). Shows the STRUCTURE that makes error debugging effective vs. just pasting a message. | Under heading |

---

## Chapter 16 — Codebase Archaeology (1 image)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-16-01 | Agent-Assisted Codebase Exploration | **Better than text: a request trace.** An agent tracing a request through codebase layers: HTTP Request → Controller → MediatR Handler → Repository → Database, with annotations at each layer. What would take a developer hours of reading, the agent maps in minutes. The FLOW is inherently visual. | Under heading |

---

## Chapter 17 — Migration Generation (2 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-17-01 | The 90/10 Split | **Key learning: agents crush mechanical work, humans handle judgment.** A bar split 90/10: the 90% section (labeled "Mechanical: update TFM, bump packages, fix renamed APIs") is handled by an agent. The 10% section (labeled "Judgment: breaking changes, behavior differences, deprecation decisions") is handled by a developer. The split IS the key insight. | Under heading |
| img-17-02 | Database Schema Evolution | **Better than text: before/after with migration.** Two schema diagrams side by side (before state → after state) with a migration script in between. Annotations: "Agent generates migration" + "Developer reviews SQL" + safety checklist (backup, test on copy, reversible Down()). | Under heading |

---

## Chapter 18 — The Parallel Agent Lifestyle (3 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-18-01 | Git Worktrees: The Practical Foundation | **Better than text: the physical separation.** A main trunk with 3-4 worktree branches, each with its own folder and its own agent working independently. Shows WHY parallel agents work without merge conflicts — physical isolation. | Under heading |
| img-18-02 | Task Decomposition: The Parallel Mindset | **Key learning: break features into independent pieces.** A feature card being broken into 4 puzzle pieces by a developer, each piece handed to a separate agent in a separate worktree. Arrows show pieces reassembling into the completed feature via PRs. The KEY skill of parallel work. | Under heading |
| img-18-03 | Managing the Review Bottleneck | **Key learning: you become the bottleneck.** A funnel: many PRs flowing in from parallel agents at the top, narrow middle (developer reviewing), merged code out the bottom. Annotations show solutions: triage by risk, automate low-risk checks, batch reviews. The constraint that limits parallelism. | Under heading |

---

## Chapter 19 — Background Agents (1 image)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-19-01 | The "Launch and Review" Model | **Lifts the learning: the async workflow.** A timeline: Evening (developer assigns task from phone) → Night (agent works: reads codebase, implements, runs tests, creates PR — shown as a sequence of small steps) → Morning (developer reviews PR with coffee, approves). The overnight productivity gain made tangible. | Under heading |

---

## Chapter 20 — Multi-Agent Coordination (2 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-20-01 | The Specialization Model | **Better than text: assembly line.** Specialized agents at stations: "Frontend Agent" building UI components, "API Agent" creating endpoints, "Database Agent" writing migrations — work flowing between them with defined handoff points. Shows how multi-agent differs from parallel (coordination vs. independence). | Under heading |
| img-20-02 | The Orchestrator Pattern | **Better than text: coordination architecture.** A lead agent at center receiving the full task, breaking it into subtasks, distributing to specialist agents, collecting results, and assembling the final output. Shows the hub-and-spoke coordination that makes complex features possible. | Under heading |

---

## Chapter 21 — Agent CI/CD Integration (1 image)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-21-01 | The Agent-in-the-Loop Pipeline | **Key learning: where the agent fits in CI/CD.** A circular CI/CD pipeline: Code → Build → Test → [FAIL] → Agent reads logs → Agent fixes code → Agent pushes commit → Build → Test → [PASS] → Deploy. The agent is integrated at the failure-recovery point. Shows the NEW pipeline shape. | Under heading |

---

## Chapter 22 — Cost Management (2 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-22-01 | The Real Cost of Running Agents | **Lifts the learning: costs are real.** A monthly receipt/bill: API tokens ($X), subscriptions ($Y), compute ($Z), total = $XXX/month. Next to it: "Productivity gain value: $X,XXX/month." The ROI framing — costs are real but justified when managed. | Under heading |
| img-22-02 | Context Window as Suitcase | **Lifts the learning: context efficiency.** Two suitcases (labeled "context window"): Left is overstuffed (2000-line AGENTS.md, redundant rules, entire documentation) bursting open. Right is efficiently packed (200-line AGENTS.md, scoped rules, lean skills) with room to spare. Same trip, different packing strategy. | Under heading |

---

## Chapter 23 — Context Files for .NET (1 image)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-23-01 | The Complete .NET Context Hierarchy | **Better than text: full hierarchy in one view.** A .NET project tree with context files at each level: root `AGENTS.md` (project-wide), `.claude/rules/controllers.md` scoped to Controllers/, `tests.md` scoped to tests/, `.claude/skills/deploy/` for deployment workflow. Shows how all context layers from chapters 6-8 come together in a real .NET project. | Under heading |

---

## Chapter 24 — Agents and .NET Aspire (1 image)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-24-01 | Aspire Architecture | **Better than text: orchestration diagram.** The AppHost at center orchestrating: API service, Worker service, PostgreSQL, Redis cache — with service discovery arrows connecting them. The Aspire dashboard shown as a control panel monitoring health and logs. This architecture IS the concept; a diagram communicates it 10x faster than prose. | Under heading |

---

## Chapter 25 — EF Core Migrations with Agents (1 image)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-25-01 | The Migration Safety Workflow | **Key learning: the gated process.** A pipeline with gates/checkpoints: Generate migration → [Gate: Review SQL] → Test on database copy → [Gate: Verify Down() works] → Backup production → [Gate: Team approval] → Apply. Each gate has a stop sign. Shows that migrations need MORE gates than normal code, not fewer. | Under heading |

---

## Chapter 26 — Microsoft Agent Framework (2 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-26-01 | The Layered Architecture | **Better than text: layer diagram.** Three layers: bottom = "Microsoft.Extensions.AI" (unified AI abstractions), middle = "Agent patterns" (tool-calling, memory, planning), top = "Multi-agent orchestration" (agent teams). The .NET logo ties them together. Shows how the pieces stack. | Under heading |
| img-26-02 | Agent Patterns Progression | **Better than text: complexity progression.** Three sketches left to right: Simple chat agent (1 box) → Tool-calling agent (1 box + tool connections) → Multi-agent pipeline (multiple boxes with orchestrator). Each progressively more complex. Shows the BUILD path from simple to sophisticated. | Under heading |

---

## Chapter 27 — Security Review with Agents (1 image)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-27-01 | The Systematic Security Review Pipeline | **Better than text: process flow.** A pipeline with security gates: Code → Static Analysis → Dependency Audit (CVE check) → Secret Scan → OWASP Top 10 Review → Agent Report with findings categorized as Critical/High/Medium/Low. Shows that security review is SYSTEMATIC, not ad-hoc — the agent follows a defined process. | Under heading |

---

## Chapter 28 — When Not to Use Agents (2 images)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-28-01 | The Trust Boundary | **Key learning: some code requires human-only.** A vault door labeled "HUMAN REVIEW REQUIRED" — behind it: cryptography, authentication, payment processing, data migration scripts. An agent waits outside, available for consultation but not autonomous action. The boundary between "agent-safe" and "human-only" is the key concept. | Under heading |
| img-28-02 | The "Faster by Hand" Test | **Key learning: sometimes agents add overhead.** Two race lanes: Agent lane shows overhead steps (load context → generate → review → fix → re-review) for a 5-line change. Developer lane shows: just type it (2 minutes). When the overhead exceeds the task, skip the agent. The visual makes the cost/benefit obvious. | Under heading |

---

## Chapter 29 — The 30-Day Transformation (1 image)

| ID | Section | Description | Placement |
|---|---|---|---|
| img-29-01 | The 30-Day Arc | **Better than text: progression timeline.** A 4-week ascending path: Week 1 "Foundation" (single agent, context file, first TDD loop) → Week 2 "Workflows" (TDD loop daily, spec-first, path rules) → Week 3 "Scale" (parallel agents, background tasks, CI integration) → Week 4 "Mastery" (full orchestration, multi-agent, teaching the team). Each week higher than the last, showing progression from beginner to proficient. | Under heading |
